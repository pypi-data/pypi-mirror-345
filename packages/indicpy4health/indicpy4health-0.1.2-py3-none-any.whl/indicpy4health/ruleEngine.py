import duckdb
from pandas import DataFrame
from abc import ABC


class RuleEngine:
    """
    RuleEngine

    This class facilitates the processing and evaluation of indicators on a dataset by leveraging a database engine.
    It is designed to work with data frames and ensures efficient handling of operations, including validation of
    unique identifiers and saving results.

    Args:
        df (pd.DataFrame): Data frame object in which you want to process the indicators.
        unique_identifier_column (str): Name of the column containing unique identifiers for the provided dataframe
            (there can be no repeated values in this column).
        database_path (str, optional): Path where you want to save the database needed to calculate the indicators.
            Defaults to ":memory:" (in memory).

    Examples:
        >>> df = pd.read_csv("dataset.csv", sep="|")
        >>> reng = RuleEngine(df, "hospitalization_id")
        >>> df2 = pd.read_csv("dataset2.csv", sep="|")
        >>> reng2 = RuleEngine(df2, "episode_id", "./indicators.duckdb")

    Returns:
        RuleEngine: An instance of the RuleEngine class.


    """

    def __init__(self, df: DataFrame, unique_identifier_column: str, database_path: str = ":memory:"):
        # Initialize DuckDB connection
        self.conn = duckdb.connect(database_path)
        self.row_identifier = unique_identifier_column
        self.columns = df.columns.tolist()

        # Create and write the dataframe to DuckDB
        self.conn.execute("SET GLOBAL pandas_analyze_sample=500000")
        self.conn.register("df_original", df)
        self.conn.execute("""
            CREATE TABLE dataframe_original AS 
            SELECT row_number() OVER () AS row_index_id, * 
            FROM df_original
        """)

        # Validate unique identifier
        result = self.conn.execute(f"""
            SELECT COUNT(*) = COUNT(DISTINCT {unique_identifier_column}) AS valid_identifier 
            FROM dataframe_original
        """).fetchone()

        if not result[0]:
            raise ValueError(f"Column '{unique_identifier_column}' must contain unique values for each record.")

    def _run_indicators(self, indicators_rules, only_true_indicators=True, append_results=False,
                        to_csv=None, to_parquet=None):
        # Create initial results table
        self.conn.execute(f"""
            CREATE OR REPLACE TABLE results_ AS (
                SELECT row_index_id, {self.row_identifier} 
                FROM dataframe_original
            )
        """)

        self.conn.execute("""
            CREATE OR REPLACE VIEW dataframe_ AS (
                SELECT a.row_index_id, *
                FROM dataframe_original a
                LEFT JOIN results_ b ON a.row_index_id = b.row_index_id
            )
        """)

        for sql_rule in indicators_rules:
            self.conn.execute(f"""
                CREATE OR REPLACE TABLE results_ AS (
                    SELECT a.*, COALESCE(b.{sql_rule.name}, FALSE) AS {sql_rule.name}
                    FROM results_ a
                    LEFT JOIN ({sql_rule.sql_rule}) b ON a.row_index_id = b.row_index_id
                )
            """)

            self.conn.execute("""
                        CREATE OR REPLACE VIEW dataframe_ AS (
                            SELECT a.row_index_id, *
                            FROM dataframe_original a
                            LEFT JOIN results_ b ON a.row_index_id = b.row_index_id
                        )
                    """)

        condition_true = " OR ".join([rule.name for rule in indicators_rules])

        if append_results and only_true_indicators:
            query_get_data = f"""
                SELECT * EXCLUDE(row_index_id) 
                FROM dataframe_original 
                WHERE row_index_id IN (
                    SELECT row_index_id FROM results_ WHERE {condition_true}
                )
            """
        elif append_results:
            query_get_data = "SELECT * EXCLUDE(row_index_id) FROM dataframe_original"
        else:
            query_get_data = f"SELECT * EXCLUDE(row_index_id) FROM results_ WHERE {condition_true}"

        if to_csv is not None:
            query_save_csv = f"COPY ({query_get_data}) TO '{to_csv}' WITH (FORMAT CSV)"
            self.conn.execute(query_save_csv)
        elif to_parquet is not None:
            query_save_parquet = f"COPY ({query_get_data}) TO '{to_parquet}' WITH (FORMAT 'parquet', COMPRESSION 'gzip')"
            self.conn.execute(query_save_parquet)
        else:
            result = self.conn.execute(query_get_data).fetch_df()
            return result

    def __del__(self):
        self.conn.close()


def run_indicators(rule_engine, indicators_rules, only_true_indicators=True, append_results=False, to_csv=None,
                   to_parquet=None):
    """
    Executes the specified indicator rules using the given RuleEngine object and provides options for output customization.

    Args:
        rule_engine (RuleEngine): The RuleEngine object used to apply the indicator rules on the associated dataset.
        indicators_rules (list[SqlRuleIndicator]): List of objects of class `SqlRuleIndicator` (MatchAny, MatchAll, MatchAnyWhere, MatchAllWhere, CustomMatch).
            Each object represents an indicator rule to be applied.
        only_true_indicators (bool, optional): If `True`, the function returns only the records that meet at least one of the indicators. Defaults to `True`.
        append_results (bool, optional): If `True`, the function returns the original dataset along with the indicators.
            If `False`, only the `unique_identifier_column` and the indicator results are returned. Defaults to `False`.
        to_csv (str, optional): Path to save the results as a CSV file. If `None`, no CSV file is created. Defaults to `None`.
        to_parquet (str, optional): Path to save the results as a parquet file format with gzip compression. Defaults to `None`.

    Returns:
        Depends on the parameter values:
        - If `only_true_indicators=True`, only the records matching at least one indicator are returned.
        - If `append_results=True`, the full dataset with appended indicators is returned.
        - If `append_results=False`, only the `unique_identifier_column` and the indicator results are returned.
        - If `to_csv` or `to_parquet` is specified, the results are saved to the respective file format.
        - If both `to_csv` and `to_parquet` are `None`, the results are returned as a DataFrame.

    Examples:
        >>> df = pd.read_csv("dataset.csv", sep="|")
        >>> rule_engine = RuleEngine(df, "hospitalization_id")
        >>> target_columns = ["diagnosis1"]
        >>> definition_codes = ["F10.10", "F10.11", "F10.120", "F10.121"]
        >>> alcohol_indicator = MatchAny(rule_engine, "alcohol_i", target_columns, definition_codes)
        >>> indicators_rules = [alcohol_indicator]
        >>>
        >>> # Option return data frame
        >>> result = run_indicators(rule_engine, indicators_rules, only_true_indicators=True, append_results=False)
        >>>
        >>> # Option save to CSV file
        >>> run_indicators(rule_engine, indicators_rules, only_true_indicators=True, append_results=False, to_csv="output.csv")
        >>>
        >>> # Option save to Parquet file
        >>> run_indicators(rule_engine, indicators_rules, only_true_indicators=True, append_results=False, to_parquet="output.parquet")
    Raises:
        TypeError: If any invalid object is passed in `indicators_rules`.


    """
    # Check if all indicators_rules are instances of SqlRuleIndicator
    if not all(isinstance(rule, SqlRuleIndicator) for rule in indicators_rules):
        raise TypeError(
            "'indicators_rules' only accepts objects of the SqlRuleIndicator class (MatchAny, MatchAll, MatchAnyWhere, MatchAllWhere, CustomMatch)")

    # Execute the indicators through the RuleEngine
    result = rule_engine._run_indicators(indicators_rules, only_true_indicators, append_results, to_csv, to_parquet)

    return result

class SqlRuleIndicator(ABC):
    def __init__(self, name: str, sql_rule: str):
        self.__name = name
        self.__sql_rule = sql_rule


def get_reserved_words(self):
    return ['ABORT', 'ABS', 'ABSOLUTE', 'ACTION', 'ADD', 'ADMIN', 'AFTER', 'AGGREGATE', 'ALL', 'ALSO', 'ALTER',
            'ALWAYS', 'ANALYSE', 'ANALYZE', 'AND',
            'ANY', 'ARRAY', 'AS', 'ASC', 'ASSERTION', 'ASSIGNMENT', 'ASYMMETRIC', 'AT', 'ATTRIBUTE', 'AUTHORIZATION',
            'BACKWARD', 'BEFORE', 'BEGIN',
            'BETWEEN', 'BIGINT', 'BINARY', 'BIT', 'BOOLEAN', 'BOTH', 'BY', 'CACHE', 'CALL', 'CALLED', 'CASCADE',
            'CASCADED', 'CASE', 'CAST', 'CATALOG',
            'CHAIN', 'CHAR', 'CHARACTER', 'CHARACTERISTICS', 'CHECK', 'CHECKPOINT', 'CLASS', 'CLOSE', 'CLUSTER',
            'COALESCE', 'COLLATE', 'COLLATION',
            'COLUMN', 'COLUMNS', 'COMMENT', 'COMMENTS', 'COMMIT', 'COMMITTED', 'CONCURRENTLY', 'CONFIGURATION',
            'CONFLICT', 'CONNECTION', 'CONSTRAINT',
            'CONSTRAINTS', 'CONTENT', 'CONTINUE', 'CONVERSION', 'COPY', 'COST', 'CREATE', 'CROSS', 'CSV', 'CUBE',
            'CURRENT', 'CURRENT_CATALOG',
            'CURRENT_DATE', 'CURRENT_ROLE', 'CURRENT_SCHEMA', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURRENT_USER',
            'CURSOR', 'CYCLE', 'DATA',
            'DATABASE', 'DAY', 'DEALLOCATE', 'DEC', 'DECIMAL', 'DECLARE', 'DEFAULT', 'DEFAULTS', 'DEFERRABLE',
            'DEFERRED', 'DEFINED', 'DEFINER',
            'DELETE', 'DELIMITER', 'DELIMITERS', 'DEPENDS', 'DESC', 'DETACH', 'DICTIONARY', 'DISABLE', 'DISCARD',
            'DISTINCT', 'DO', 'DOCUMENT',
            'DOMAIN', 'DOUBLE', 'DROP', 'EACH', 'ELSE', 'ENABLE', 'ENCODING', 'ENCRYPTED', 'END', 'ENUM', 'ESCAPE',
            'EVENT', 'EXCEPT', 'EXCLUDE',
            'EXCLUDING', 'EXCLUSIVE', 'EXECUTE', 'EXISTS', 'EXPLAIN', 'EXTENSION', 'EXTERNAL', 'EXTRACT', 'FALSE',
            'FAMILY', 'FETCH', 'FILTER',
            'FIRST', 'FLOAT', 'FOLLOWING', 'FOR', 'FORCE', 'FOREIGN', 'FORWARD', 'FREEZE', 'FROM', 'FULL', 'FUNCTION',
            'FUNCTIONS', 'GENERATED',
            'GLOBAL', 'GRANT', 'GRANTED', 'GREATEST', 'GROUP', 'GROUPING', 'GROUPS', 'HANDLER', 'HAVING', 'HEADER',
            'HOLD', 'HOUR', 'IDENTITY',
            'IF', 'ILIKE', 'IMMEDIATE', 'IMMUTABLE', 'IMPLICIT', 'IMPORT', 'IN', 'INCLUDE', 'INCLUDING', 'INCREMENT',
            'INDEX', 'INDEXES', 'INHERIT',
            'INHERITS', 'INITIALLY', 'INLINE', 'INNER', 'INOUT', 'INPUT', 'INSENSITIVE', 'INSERT', 'INSTEAD', 'INT',
            'INTEGER', 'INTERSECT',
            'INTERVAL', 'INTO', 'INVOKER', 'IS', 'ISNULL', 'ISOLATION', 'JOIN', 'KEY', 'LABEL', 'LANGUAGE', 'LARGE',
            'LAST', 'LATERAL', 'LEADING',
            'LEAKPROOF', 'LEAST', 'LEFT', 'LEVEL', 'LIKE', 'LIMIT', 'LISTEN', 'LOAD', 'LOCAL', 'LOCALTIME',
            'LOCALTIMESTAMP', 'LOCATION', 'LOCK',
            'LOCKED', 'LOGGED', 'MAPPING', 'MATCH', 'MATERIALIZED', 'MAXVALUE', 'METHOD', 'MINUTE', 'MINVALUE', 'MODE',
            'MONTH', 'MOVE', 'NAME',
            'NAMES', 'NATIONAL', 'NATURAL', 'NCHAR', 'NEW', 'NEXT', 'NO', 'NONE', 'NOT', 'NOTHING', 'NOTIFY', 'NOTNULL',
            'NOWAIT', 'NULL', 'NULLIF',
            'NULLS', 'NUMERIC', 'OBJECT', 'OF', 'OFF', 'OFFSET', 'OIDS', 'OLD', 'ON', 'ONLY', 'OPERATOR', 'OPTION',
            'OPTIONS', 'OR', 'ORDER', 'ORDINALITY',
            'OTHERS', 'OUT', 'OUTER', 'OVER', 'OVERLAPS', 'OVERLAY', 'OVERRIDING', 'OWNED', 'OWNER', 'PARALLEL',
            'PARSER', 'PARTIAL', 'PARTITION',
            'PASSING', 'PASSWORD', 'PLACING', 'PLANS', 'POLICY', 'POSITION', 'PRECEDING', 'PRECISION', 'PREPARE',
            'PREPARED', 'PRESERVE', 'PRIMARY',
            'PRIOR', 'PRIVILEGES', 'PROCEDURAL', 'PROCEDURE', 'PROCEDURES', 'PROGRAM', 'PUBLICATION', 'QUOTE', 'RANGE',
            'READ', 'REAL', 'REASSIGN',
            'RECHECK', 'RECURSIVE', 'REF', 'REFERENCES', 'REFERENCING', 'REFRESH', 'REINDEX', 'RELATIVE', 'RELEASE',
            'RENAME', 'REPEATABLE', 'REPLACE',
            'REPLICA', 'REQUIRING', 'RESET', 'RESTART', 'RESTRICT', 'RETURNING', 'RETURNS', 'REVOKE', 'RIGHT', 'ROLE',
            'ROLLBACK', 'ROLLUP', 'ROUTINE',
            'ROUTINES', 'ROW', 'ROWS', 'RULE', 'SAVEPOINT', 'SCHEMA', 'SCHEMAS', 'SCROLL', 'SEARCH', 'SECOND',
            'SECURITY', 'SELECT', 'SEQUENCE',
            'SEQUENCES', 'SERIALIZABLE', 'SERVER', 'SESSION', 'SESSION_USER', 'SET', 'SETOF', 'SETS', 'SHARE', 'SHOW',
            'SIMILAR', 'SIMPLE', 'SKIP',
            'SMALLINT', 'SNAPSHOT', 'SOME', 'SQL', 'STABLE', 'STANDALONE', 'START', 'STATEMENT', 'STATISTICS', 'STDIN',
            'STDOUT', 'STORAGE', 'STORED',
            'STRICT', 'STRIP', 'SUBSCRIPTION', 'SUBSTRING', 'SYMMETRIC', 'SYSID', 'SYSTEM', 'TABLE', 'TABLES',
            'TABLESAMPLE', 'TABLESPACE', 'TEMP',
            'TEMPLATE', 'TEMPORARY', 'TEXT', 'THEN', 'TIES', 'TIME', 'TIMESTAMP', 'TO', 'TRAILING', 'TRANSACTION',
            'TRANSFORM', 'TREAT', 'TRIGGER',
            'TRIM', 'TRUE', 'TRUNCATE', 'TRUSTED', 'TYPE', 'TYPES', 'UNBOUNDED', 'UNCOMMITTED', 'UNENCRYPTED', 'UNION',
            'UNIQUE', 'UNKNOWN', 'UNLISTEN',
            'UNLOGGED', 'UNTIL', 'UPDATE', 'USER', 'USING', 'VACUUM', 'VALID', 'VALIDATE', 'VALIDATOR', 'VALUE',
            'VALUES', 'VARCHAR', 'VARIADIC',
            'VARYING', 'VERBOSE', 'VERSION', 'VIEW', 'VIEWS', 'VOLATILE', 'WHEN', 'WHERE', 'WHITESPACE', 'WINDOW',
            'WITH', 'WITHIN', 'WITHOUT', 'WORK',
            'WRAPPER', 'WRITE', 'XML', 'XMLATTRIBUTES', 'XMLCONCAT', 'XMLELEMENT', 'XMLEXISTS', 'XMLFOREST',
            'XMLNAMESPACES', 'XMLPARSE', 'XMLPI',
            'XMLROOT', 'XMLSERIALIZE', 'XMLTABLE', 'YEAR', 'YES', 'ZONE', 'ROW_INDEX_ID', 'row_index_id']


# Restricted words
restricted_words = [
    'ABORT', 'ABS', 'ABSOLUTE', 'ACTION', 'ADD', 'ADMIN', 'AFTER', 'AGGREGATE', 'ALL', 'ALSO', 'ALTER', 'ALWAYS',
    'ANALYSE', 'ANALYZE', 'AND', 'ANY', 'ARRAY', 'AS', 'ASC', 'ASSERTION', 'ASSIGNMENT', 'ASYMMETRIC', 'AT',
    'ATTRIBUTE', 'AUTHORIZATION', 'BACKWARD', 'BEFORE', 'BEGIN', 'BETWEEN', 'BIGINT', 'BINARY', 'BIT',
    'BOOLEAN', 'BOTH', 'BY', 'CACHE', 'CALL', 'CALLED', 'CASCADE', 'CASCADED', 'CASE', 'CAST', 'CATALOG',
    'CHAIN', 'CHAR', 'CHARACTER', 'CHARACTERISTICS', 'CHECK', 'CHECKPOINT', 'CLASS', 'CLOSE', 'CLUSTER',
    'COALESCE', 'COLLATE', 'COLLATION', 'COLUMN', 'COLUMNS', 'COMMENT', 'COMMENTS', 'COMMIT', 'COMMITTED',
    'CONCURRENTLY', 'CONFIGURATION', 'CONFLICT', 'CONNECTION', 'CONSTRAINT', 'CONSTRAINTS', 'CONTENT',
    'CONTINUE', 'CONVERSION', 'COPY', 'COST', 'CREATE', 'CROSS', 'CSV', 'CUBE', 'CURRENT', 'CURRENT_CATALOG',
    'CURRENT_DATE', 'CURRENT_ROLE', 'CURRENT_SCHEMA', 'CURRENT_TIME', 'CURRENT_TIMESTAMP',
    'CURRENT_USER', 'CURSOR', 'CYCLE', 'DATA', 'DATABASE', 'DAY', 'DEALLOCATE', 'DEC', 'DECIMAL', 'DECLARE',
    'DEFAULT', 'DEFAULTS', 'DEFERRABLE', 'DEFERRED', 'DEFINED', 'DEFINER', 'DELETE', 'DELIMITER', 'DELIMITERS',
    'DEPENDS', 'DESC', 'DETACH', 'DICTIONARY', 'DISABLE', 'DISCARD', 'DISTINCT', 'DO', 'DOCUMENT', 'DOMAIN',
    'DOUBLE', 'DROP', 'EACH', 'ELSE', 'ENABLE', 'ENCODING', 'ENCRYPTED', 'END', 'ENUM', 'ESCAPE', 'EVENT',
    'EXCEPT', 'EXCLUDE', 'EXCLUDING', 'EXCLUSIVE', 'EXECUTE', 'EXISTS', 'EXPLAIN', 'EXTENSION', 'EXTERNAL',
    'EXTRACT', 'FALSE', 'FAMILY', 'FETCH', 'FILTER', 'FIRST', 'FLOAT', 'FOLLOWING', 'FOR', 'FORCE', 'FOREIGN',
    'FORWARD', 'FREEZE', 'FROM', 'FULL', 'FUNCTION', 'FUNCTIONS', 'GENERATED', 'GLOBAL', 'GRANT', 'GRANTED',
    'GREATEST', 'GROUP', 'GROUPING', 'GROUPS', 'HANDLER', 'HAVING', 'HEADER', 'HOLD', 'HOUR', 'IDENTITY', 'IF',
    'ILIKE', 'IMMEDIATE', 'IMMUTABLE', 'IMPLICIT', 'IMPORT', 'IN', 'INCLUDE', 'INCLUDING', 'INCREMENT',
    'INDEX', 'INDEXES', 'INHERIT', 'INHERITS', 'INITIALLY', 'INLINE', 'INNER', 'INOUT', 'INPUT', 'INSENSITIVE',
    'INSERT', 'INSTEAD', 'INT', 'INTEGER', 'INTERSECT', 'INTERVAL', 'INTO', 'INVOKER', 'IS', 'ISNULL',
    'ISOLATION', 'JOIN', 'KEY', 'LABEL', 'LANGUAGE', 'LARGE', 'LAST', 'LATERAL', 'LEADING', 'LEAKPROOF',
    'LEAST', 'LEFT', 'LEVEL', 'LIKE', 'LIMIT', 'LISTEN', 'LOAD', 'LOCAL', 'LOCALTIME', 'LOCALTIMESTAMP',
    'LOCATION', 'LOCK', 'LOCKED', 'LOGGED', 'MAPPING', 'MATCH', 'MATERIALIZED', 'MAXVALUE', 'METHOD', 'MINUTE',
    'MINVALUE', 'MODE', 'MONTH', 'MOVE', 'NAME', 'NAMES', 'NATIONAL', 'NATURAL', 'NCHAR', 'NEW', 'NEXT', 'NO',
    'NONE', 'NOT', 'NOTHING', 'NOTIFY', 'NOTNULL', 'NOWAIT', 'NULL', 'NULLIF', 'NULLS', 'NUMERIC', 'OBJECT',
    'OF', 'OFF', 'OFFSET', 'OIDS', 'OLD', 'ON', 'ONLY', 'OPERATOR', 'OPTION', 'OPTIONS', 'OR', 'ORDER',
    'ORDINALITY', 'OTHERS', 'OUT', 'OUTER', 'OVER', 'OVERLAPS', 'OVERLAY', 'OVERRIDING', 'OWNED', 'OWNER',
    'PARALLEL', 'PARSER', 'PARTIAL', 'PARTITION', 'PASSING', 'PASSWORD', 'PLACING', 'PLANS', 'POLICY',
    'POSITION', 'PRECEDING', 'PRECISION', 'PREPARE', 'PREPARED', 'PRESERVE', 'PRIMARY', 'PRIOR',
    'PRIVILEGES', 'PROCEDURAL', 'PROCEDURE', 'PROCEDURES', 'PROGRAM', 'PUBLICATION', 'QUOTE', 'RANGE', 'READ',
    'REAL', 'REASSIGN', 'RECHECK', 'RECURSIVE', 'REF', 'REFERENCES', 'REFERENCING', 'REFRESH', 'REINDEX',
    'RELATIVE', 'RELEASE', 'RENAME', 'REPEATABLE', 'REPLACE', 'REPLICA', 'REQUIRING', 'RESET', 'RESTART',
    'RESTRICT', 'RETURNING', 'RETURNS', 'REVOKE', 'RIGHT', 'ROLE', 'ROLLBACK', 'ROLLUP', 'ROUTINE', 'ROUTINES',
    'ROW', 'ROWS', 'RULE', 'SAVEPOINT', 'SCHEMA', 'SCHEMAS', 'SCROLL', 'SEARCH', 'SECOND', 'SECURITY', 'SELECT',
    'SEQUENCE', 'SEQUENCES', 'SERIALIZABLE', 'SERVER', 'SESSION', 'SESSION_USER', 'SET', 'SETOF', 'SETS',
    'SHARE', 'SHOW', 'SIMILAR', 'SIMPLE', 'SKIP', 'SMALLINT', 'SNAPSHOT', 'SOME', 'SQL', 'STABLE', 'STANDALONE',
    'START', 'STATEMENT', 'STATISTICS', 'STDIN', 'STDOUT', 'STORAGE', 'STORED', 'STRICT', 'STRIP',
    'SUBSCRIPTION', 'SUBSTRING', 'SYMMETRIC', 'SYSID', 'SYSTEM', 'TABLE', 'TABLES', 'TABLESAMPLE',
    'TABLESPACE', 'TEMP', 'TEMPLATE', 'TEMPORARY', 'TEXT', 'THEN', 'TIES', 'TIME', 'TIMESTAMP', 'TO',
    'TRAILING', 'TRANSACTION', 'TRANSFORM', 'TREAT', 'TRIGGER', 'TRIM', 'TRUE', 'TRUNCATE', 'TRUSTED',
    'TYPE', 'TYPES', 'UNBOUNDED', 'UNCOMMITTED', 'UNENCRYPTED', 'UNION', 'UNIQUE', 'UNKNOWN', 'UNLISTEN',
    'UNLOGGED', 'UNTIL', 'UPDATE', 'USER', 'USING', 'VACUUM', 'VALID', 'VALIDATE', 'VALIDATOR', 'VALUE',
    'VALUES', 'VARCHAR', 'VARIADIC', 'VARYING', 'VERBOSE', 'VERSION', 'VIEW', 'VIEWS', 'VOLATILE', 'WHEN',
    'WHERE', 'WHITESPACE', 'WINDOW', 'WITH', 'WITHIN', 'WITHOUT', 'WORK', 'WRAPPER', 'WRITE', 'XML',
    'XMLATTRIBUTES', 'XMLCONCAT', 'XMLELEMENT', 'XMLEXISTS', 'XMLFOREST', 'XMLNAMESPACES', 'XMLPARSE',
    'XMLPI', 'XMLROOT', 'XMLSERIALIZE', 'XMLTABLE', 'YEAR', 'YES', 'ZONE', 'ROW_INDEX_ID'
]


def check_params_simple(rule_engine, indicator_name, target_columns, definition_codes, regex_prefix_search):
    if not isinstance(rule_engine, RuleEngine):
        raise TypeError("The 'rule_engine' argument must be an instance of RuleEngine.")
    if not isinstance(indicator_name, str):
        raise TypeError("The 'indicator_name' argument must be of type str.")
    if indicator_name.upper() in restricted_words:
        raise ValueError("The 'indicator_name' argument cannot match any restricted word.")
    if not isinstance(target_columns, list) or not all(isinstance(col, str) for col in target_columns):
        raise TypeError("The 'target_columns' argument must be a list of strings.")
    invalid_columns = [col for col in target_columns if col not in rule_engine.columns]
    if invalid_columns:
        raise ValueError(
            f"Some columns in 'target_columns' are not defined in the original data frame: {', '.join(invalid_columns)}")
    if not isinstance(definition_codes, list) or not all(isinstance(code, str) for code in definition_codes):
        raise TypeError("The 'definition_codes' argument must be a list of strings.")
    if not isinstance(regex_prefix_search, bool):
        raise TypeError("The 'regex_prefix_search' argument must be a boolean.")

    # Verify data types of target columns
    target_columns_part = ", ".join([f"'{col}'" for col in target_columns])
    query = f"""
        SELECT COUNT(DISTINCT data_type) > 1 AS n_data_type
        FROM information_schema.columns
        WHERE table_name = 'dataframe_original' AND column_name IN ({target_columns_part})
    """
    result = rule_engine.conn.execute(query).fetchone()
    if result[0]:  # Assuming result[0] corresponds to `n_data_type`
        raise TypeError("Warning: The columns defined in 'target_columns' contain different data types.")


def check_params_where(rule_engine, indicator_name, target_columns, definition_codes, filter_columns,
                       regex_prefix_search):
    # Check if rule_engine is a valid RuleEngine object
    if not isinstance(rule_engine, RuleEngine):
        raise TypeError("The 'rule_engine' argument must be an instance of RuleEngine.")

    # Check if indicator_name is a string and not a restricted word
    if not isinstance(indicator_name, str):
        raise TypeError("The 'indicator_name' argument must be of type str.")
    if indicator_name.upper() in restricted_words:
        raise ValueError("The 'indicator_name' argument cannot match any restricted word.")

    # Validate target_columns as a list of strings
    if not isinstance(target_columns, list) or not all(isinstance(col, str) for col in target_columns):
        raise TypeError("The 'target_columns' argument must be a list of strings.")
    invalid_columns = [col for col in target_columns if col not in rule_engine.columns]
    if invalid_columns:
        raise ValueError(
            f"Some columns in 'target_columns' are not defined in the original data frame: {', '.join(invalid_columns)}")

    # Validate definition_codes as a list of strings
    if not isinstance(definition_codes, list) or not all(isinstance(code, str) for code in definition_codes):
        raise TypeError("The 'definition_codes' argument must be a list of strings.")

    # Validate regex_prefix_search as a boolean
    if not isinstance(regex_prefix_search, bool):
        raise TypeError("The 'regex_prefix_search' argument must be a boolean.")

    # Verify data types of target columns
    target_columns_part = ", ".join([f"'{col}'" for col in target_columns])
    query = f"""
        SELECT COUNT(DISTINCT data_type) > 1 AS n_data_type
        FROM information_schema.columns
        WHERE table_name = 'dataframe_original' AND column_name IN ({target_columns_part})
    """
    result = rule_engine.conn.execute(query).fetchone()
    if result and result[0]:  # Assuming result[0] corresponds to `n_data_type`
        print("Warning: The columns defined in 'target_columns' contain different data types.")

    # Validate filter_columns as a list of strings
    if not isinstance(filter_columns, list) or not all(isinstance(col, str) for col in filter_columns):
        raise TypeError("The 'filter_columns' argument must be a list of strings.")
    invalid_columns = [col for col in filter_columns if col not in rule_engine.columns]
    if invalid_columns:
        raise ValueError(
            f"Some columns in 'filter_columns' are not defined in the original data frame: {', '.join(invalid_columns)}")

    # Ensure target_columns and filter_columns have the same length
    if len(target_columns) != len(filter_columns):
        raise ValueError("The length of 'target_columns' must be equal to the length of 'filter_columns'.")


class MatchAny(SqlRuleIndicator):
    """
    A class that creates an SQL indicator to evaluate whether any of the target
    columns match the specified definition codes. The indicator returns `TRUE` if
    at least one match occurs.

    Args:
        rule_engine (RuleEngine): The rule engine containing the dataset where indicators will be applied.
        indicator_name (str): A string representing the name of the indicator.
        target_columns (list[str]): Column names where the match is evaluated. Searches are performed across all target columns.
        definition_codes (list[str]): A set of codes used to define the matching criteria for the target columns.
        regex_prefix_search (bool, optional): Indicates whether to perform prefix-based regex matches (`True`) or exact matches (`False`).
            Defaults to `False`.

    Examples:
        >>> hosp_dataframe = pd.DataFrame({
        >>>     "episode_id": [1, 2, 3],
        >>>     "age": [45, 60, 32],
        >>>     "diagnosis1": ["F10.10", "I20", "I60"],
        >>>     "diagnosis2": ["E11", "J45", "I25"],
        >>>     "diagnosis3": ["I60", "K35", "F10.120"]
        >>> })
        >>> target_columns = ["diagnosis1"]
        >>> definition_codes = ["F10.10", "F10.11", "F10.120", "F10.121"]
        >>> alcohol_indicator = MatchAny(
        >>>     reng,
        >>>     "alcohol_i",
        >>>     target_columns,
        >>>     definition_codes
        >>> )

    Returns:
        MatchAny: An instance of the MatchAny class with the generated SQL rule.
    """

    def __init__(self, rule_engine, indicator_name, target_columns, definition_codes, regex_prefix_search=False):
        # Eliminar elementos vacíos o nulos
        definition_codes = [code for code in definition_codes if code]
        if not definition_codes:
            raise ValueError("'definition_codes' must contain at least one non-empty, non-null element.")

        check_params_simple(rule_engine, indicator_name, target_columns, definition_codes, regex_prefix_search)

        self.name = indicator_name

        # Generar SQL según los argumentos
        columns_part = ", ".join(target_columns)
        if regex_prefix_search:
            codes_part = ", ".join([f"'{code}%'" for code in definition_codes])
            self.sql_rule = f"""
                WITH codes_to_compare AS (SELECT DISTINCT UNNEST([{codes_part}]) AS code_to_compare)
                SELECT DISTINCT a.row_index_id, TRUE AS {indicator_name}
                FROM (
                    SELECT * FROM (
                        SELECT row_index_id, UNNEST([{columns_part}]) AS list_diag
                        FROM dataframe_
                    ) a
                    WHERE list_diag IS NOT NULL
                ) a
                LEFT JOIN codes_to_compare b
                ON a.list_diag LIKE b.code_to_compare
                WHERE b.code_to_compare IS NOT NULL
            """
        else:
            codes_part = ", ".join([f"'{code}'" for code in definition_codes])
            self.sql_rule = f"""
                WITH codes_to_compare AS (SELECT DISTINCT UNNEST([{codes_part}]) AS code_to_compare)
                SELECT DISTINCT a.row_index_id, TRUE AS {indicator_name}
                FROM (
                    SELECT * FROM (
                        SELECT row_index_id, UNNEST([{columns_part}]) AS list_diag
                        FROM dataframe_
                    ) a
                    WHERE list_diag IS NOT NULL
                ) a
                LEFT JOIN codes_to_compare b
                ON a.list_diag = b.code_to_compare
                WHERE b.code_to_compare IS NOT NULL
            """


class MatchAnyWhere(SqlRuleIndicator):
    """
    A class that creates an SQL indicator to evaluate whether any of the target
    columns match the specified definition codes under the conditions defined by the
    filter columns and lookup values. The matching is applied only to the target columns
    that are in the same order as the filter columns and satisfy the conditions
    in lookup values. The indicator returns `TRUE` if at least one target column
    satisfies the matching criteria.

    Args:
        rule_engine (RuleEngine): The rule engine containing the dataset where the indicators will be applied.
        indicator_name (str): A string representing the name of the indicator.
        target_columns (list[str]): Column names where the values from `definition_codes` will be searched.
        definition_codes (list[str]): A set of codes used to define the matching criteria applied to `target_columns`.
        filter_columns (list[str]): Column names that define the conditions under which the `lookup_values` must hold.
        lookup_values (list[str]): A list of values used to define logical conditions linked to `filter_columns`.
        regex_prefix_search (bool, optional): Indicates whether to use regex-based prefix searches (`True`) or exact matches (`False`).
            Defaults to `False`.

    Examples:
         >>> hosp_dataframe = pd.DataFrame({
         >>>     "episode_id": [1, 2, 3],
         >>>     "age": [45, 60, 32],
         >>>     "diagnosis1": ["F10.10", "I20", "I60"],
         >>>     "diagnosis2": ["E11", "J45", "I25"],
         >>>     "diagnosis3": ["I60", "K35", "F10.120"],
         >>>     "present_on_admission_d1": [False, False, False],
         >>>     "present_on_admission_d2": ["No", "Yes", "No"],
         >>>     "present_on_admission_d3": [False, True, True],
         >>> })
         >>> reng = RuleEngine(hosp_dataframe, "episode_id")
         >>> target_columns = ["diagnosis2", "diagnosis3"]
         >>> definition_codes = ["F10.10", "F10.11", "F10.120", "F10.121"]
         >>> filter_columns = ["present_on_admission_d2", "present_on_admission_d3"]
         >>> lookup_values = ["Yes", "True"]
         >>> alcohol_indicator_poa = MatchAnyWhere(
         >>>     reng,
         >>>     "alcohol_i_poa",
         >>>     target_columns,
         >>>     definition_codes,
         >>>     filter_columns,
         >>>     lookup_values
         >>> )
         >>> alcohol_i_regex_poa = MatchAnyWhere(
         >>>     reng,
         >>>     "alcohol_i_regex_poa",
         >>>     target_columns,
         >>>     ["F10"],
         >>>     filter_columns,
         >>>     lookup_values,
         >>>     regex_prefix_search=True
         >>> )
         >>>
         >>> # Include the indicators in a list and apply them
         >>> indicators_list = [alcohol_indicator_poa, alcohol_i_regex_poa]
         >>> run_indicators(
         >>>     reng,
         >>>     indicators_list,
         >>>     append_results=False,
         >>>     csv_path="./results.csv"
         >>> )

    Returns:
        MatchAnyWhere: An instance of the MatchAnyWhere class with the generated SQL rule.

    """

    def __init__(self, rule_engine, indicator_name, target_columns, definition_codes,
                 filter_columns, lookup_values, regex_prefix_search=False):

        # Eliminar elementos vacíos o nulos
        definition_codes = [code for code in definition_codes if code]
        if not definition_codes:
            raise ValueError("'definition_codes' must contain at least one non-empty, non-null element.")

        check_params_where(rule_engine, indicator_name, target_columns, definition_codes, filter_columns,
                           regex_prefix_search)

        lookup_values = [val for val in lookup_values if val]
        if not lookup_values:
            raise ValueError("'lookup_values' must contain at least one non-empty, non-null element.")

        # Inicializar atributos
        self.name = indicator_name

        # Crear lógica `CASE WHEN` para lookup_values
        when_conditions = " ".join([f"WHEN x = '{val}' THEN TRUE" for val in lookup_values])
        case_when_part = f"CASE {when_conditions} ELSE FALSE END"

        # Generar query para `list_where`
        columns_part = ", ".join(target_columns)
        filter_columns_part = ", ".join(filter_columns)
        query_where = f"list_where([{columns_part}], list_transform([{filter_columns_part}], x -> ({case_when_part})))"

        if regex_prefix_search:
            codes_part = ", ".join([f"'{code}%'" for code in definition_codes])
            self.sql_rule = f"""
                WITH codes_to_compare AS (SELECT DISTINCT UNNEST([{codes_part}]) AS code_to_compare)
                SELECT DISTINCT row_index_id, TRUE AS {indicator_name}
                FROM (
                    SELECT row_index_id, UNNEST({query_where}) AS codes_where
                    FROM main.dataframe_
                    WHERE ARRAY_LENGTH({query_where}) > 0
                ) a
                LEFT JOIN codes_to_compare b
                ON a.codes_where LIKE b.code_to_compare
                WHERE b.code_to_compare IS NOT NULL
            """
        else:
            codes_part = ", ".join([f"'{code}'" for code in definition_codes])
            self.sql_rule = f"""
                WITH codes_to_compare AS (SELECT DISTINCT UNNEST([{codes_part}]) AS code_to_compare)
                SELECT DISTINCT row_index_id, TRUE AS {indicator_name}
                FROM (
                    SELECT row_index_id, UNNEST({query_where}) AS codes_where
                    FROM main.dataframe_
                    WHERE ARRAY_LENGTH({query_where}) > 0
                ) a
                LEFT JOIN codes_to_compare b
                ON a.codes_where = b.code_to_compare
                WHERE b.code_to_compare IS NOT NULL
            """


class MatchAll(SqlRuleIndicator):
    """
    A class that creates an SQL indicator to evaluate whether all of the target
    columns match the specified definition codes. The indicator returns `TRUE` only
    if every target column has a match.

    Args:
        rule_engine (RuleEngine): The rule engine containing the dataset where indicators will be applied.
        indicator_name (str): A string representing the name of the indicator.
        target_columns (list[str]): Column names where the match is evaluated. Searches are performed across all target columns.
        definition_codes (list[str]): A set of codes used to define the matching criteria for the target columns.
        regex_prefix_search (bool, optional): Indicates whether to perform prefix-based regex matches (`True`) or exact matches (`False`).
            Defaults to `False`.

    Examples:
        >>> hosp_dataframe = pd.DataFrame({
        >>>     "episode_id": [1, 2, 3],
        >>>     "age": [45, 60, 32],
        >>>     "diagnosis1": ["F10.10", "I20", "I60"],
        >>>     "diagnosis2": ["E11", "J45", "I25"],
        >>>     "diagnosis3": ["I60", "K35", "F10.120"]
        >>> })
        >>> reng = RuleEngine(hosp_dataframe, "episode_id")
        >>> target_columns = ["diagnosis1"]
        >>> definition_codes = ["F10.10", "F10.11", "F10.120", "F10.121"]
        >>> alcohol_indicator = MatchAll(
        >>>     reng,
        >>>     "alcohol_i",
        >>>     target_columns,
        >>>     definition_codes
        >>> )
        >>> # Include the indicators in a list and apply them
        >>> indicators_list = [alcohol_indicator]
        >>> result = run_indicators(
        >>>     reng,
        >>>     indicators_list,
        >>>     append_results=False
        >>> )

    Returns:
        MatchAll: An instance of the MatchAll class with the generated SQL rule.
    """

    def __init__(self, rule_engine, indicator_name, target_columns, definition_codes, regex_prefix_search=False):

        # Eliminar elementos vacíos o nulos
        definition_codes = [code for code in definition_codes if code]
        if not definition_codes:
            raise ValueError("'definition_codes' must contain at least one non-empty, non-null element.")

        check_params_simple(rule_engine, indicator_name, target_columns, definition_codes, regex_prefix_search)

        self.name = indicator_name

        # Generar SQL según los argumentos
        columns_part = ", ".join(target_columns)
        if regex_prefix_search:
            codes_part = ", ".join([f"'{code}%'" for code in definition_codes])
            self.sql_rule = f"""
                WITH codes_to_compare AS (SELECT DISTINCT UNNEST([{codes_part}]) AS code_to_compare)
                SELECT DISTINCT row_index_id, TRUE AS {indicator_name}
                FROM (
                    SELECT a.row_index_id, ARRAY_LENGTH(ARRAY_AGG(list_diag_)) AS n_diag_match,
                           FIRST(a.n_diag_no_null) AS n_diag_no_null
                    FROM (
                        SELECT * FROM (
                            SELECT row_index_id, UNNEST(list_diag) AS list_diag_, n_diag_no_null
                            FROM (
                                SELECT row_index_id, [{columns_part}] AS list_diag,
                                       ARRAY_LENGTH(ARRAY_FILTER(list_diag, x -> x IS NOT NULL)) AS n_diag_no_null
                                FROM dataframe_
                            )
                        ) WHERE list_diag_ IS NOT NULL
                    ) a
                    LEFT JOIN codes_to_compare b
                    ON a.list_diag_ LIKE b.code_to_compare
                    WHERE b.code_to_compare IS NOT NULL
                    GROUP BY a.row_index_id
                )
                WHERE n_diag_match = n_diag_no_null
            """
        else:
            codes_part = ", ".join([f"'{code}'" for code in definition_codes])
            self.sql_rule = f"""
                WITH codes_to_compare AS (SELECT DISTINCT UNNEST([{codes_part}]) AS code_to_compare)
                SELECT DISTINCT row_index_id, TRUE AS {indicator_name}
                FROM (
                    SELECT a.row_index_id, ARRAY_LENGTH(ARRAY_AGG(list_diag_)) AS n_diag_match,
                           FIRST(a.n_diag_no_null) AS n_diag_no_null
                    FROM (
                        SELECT * FROM (
                            SELECT row_index_id, UNNEST(list_diag) AS list_diag_, n_diag_no_null
                            FROM (
                                SELECT row_index_id, [{columns_part}] AS list_diag,
                                       ARRAY_LENGTH(ARRAY_FILTER(list_diag, x -> x IS NOT NULL)) AS n_diag_no_null
                                FROM dataframe_
                            )
                        ) WHERE list_diag_ IS NOT NULL
                    ) a
                    LEFT JOIN codes_to_compare b
                    ON a.list_diag_ = b.code_to_compare
                    WHERE b.code_to_compare IS NOT NULL
                    GROUP BY a.row_index_id
                )
                WHERE n_diag_match = n_diag_no_null
            """


class MatchAllWhere(SqlRuleIndicator):
    """
    A class that creates an SQL indicator to evaluate whether all of the target
    columns match the specified definition codes under the conditions defined by the
    filter columns and lookup values.

    Matching is applied only to the target columns that are in the same order as
    the filter columns and satisfy the conditions in lookup values. The indicator
    returns `TRUE` only if every such target column satisfies the matching criteria.

    Args:
        rule_engine (RuleEngine): The rule engine containing the dataset where the indicators will be applied.
        indicator_name (str): A string representing the name of the indicator.
        target_columns (list[str]): Column names where the values from `definition_codes` will be searched.
        definition_codes (list[str]): A set of codes used to define the matching criteria for `target_columns`.
        filter_columns (list[str]): Column names that define the conditions under which the `lookup_values` must hold.
        lookup_values (list[str]): A list of values used to define conditions linked to `filter_columns`.
        regex_prefix_search (bool, optional): Indicates whether to use regex-based prefix searches (`True`) or exact matches (`False`).
            Defaults to `False`.

    Returns:
        MatchAllWhere: An instance of the MatchAllWhere class with the generated SQL query.

    Examples:
        >>> hosp_dataframe = pd.DataFrame({
        >>>     "episode_id": [1, 2, 3],
        >>>     "age": [45, 60, 32],
        >>>     "diagnosis1": ["F10.10", "I20", "I60"],
        >>>     "diagnosis2": ["E11", "J45", "I25"],
        >>>     "diagnosis3": ["I60", "K35", "F10.120"],
        >>>     "present_on_admission_d1": [False, False, False],
        >>>     "present_on_admission_d2": ["No", "Yes", "No"],
        >>>     "present_on_admission_d3": [False, True, True],
        >>> })
        >>> reng = RuleEngine(hosp_dataframe, "episode_id")
        >>> target_columns = ["diagnosis2", "diagnosis3"]
        >>> definition_codes = ["F10.10", "F10.11", "F10.120", "F10.121"]
        >>> filter_columns = ["present_on_admission_d2", "present_on_admission_d3"]
        >>> lookup_values = ["Yes", "True"]
        >>> alcohol_indicator_poa = MatchAllWhere(
        >>>     reng,
        >>>     "alcohol_i_poa",
        >>>     target_columns,
        >>>     definition_codes,
        >>>     filter_columns,
        >>>     lookup_values
        >>> )
        >>> alcohol_i_regex_poa = MatchAllWhere(
        >>>     reng,
        >>>     "alcohol_i_regex_poa",
        >>>     target_columns,
        >>>     ["F10"],
        >>>     filter_columns,
        >>>     lookup_values,
        >>>     regex_prefix_search=True
        >>> )
        >>>
        >>> # Include the indicators in a list and apply them
        >>> indicators_list = [alcohol_indicator_poa, alcohol_i_regex_poa]
        >>> result = run_indicators(
        >>>     reng,
        >>>     indicators_list,
        >>>     append_results=False
        >>> )
    References:
        - DuckDB Query Syntax: https://duckdb.org/docs/stable/sql/query_syntax/where
    """

    def __init__(self, rule_engine, indicator_name, target_columns, definition_codes,
                 filter_columns, lookup_values, regex_prefix_search=False):

        definition_codes = [code for code in definition_codes if code]
        if not definition_codes:
            raise ValueError("'definition_codes' must contain at least one non-empty, non-null element.")

        check_params_where(rule_engine, indicator_name, target_columns, definition_codes, filter_columns,
                           regex_prefix_search)

        lookup_values = [val for val in lookup_values if val]
        if not lookup_values:
            raise ValueError("'lookup_values' must contain at least one non-empty, non-null element.")

        # Generar SQL según los argumentos
        self.name = indicator_name

        # Crear lógica `CASE WHEN` para lookup_values
        when_conditions = " ".join([f"WHEN x = '{val}' THEN TRUE" for val in lookup_values])
        case_when_part = f"CASE {when_conditions} ELSE FALSE END"

        # Generar query para `list_where`
        columns_part = ", ".join(target_columns)
        filter_columns_part = ", ".join(filter_columns)
        query_where = f"list_where([{columns_part}], list_transform([{filter_columns_part}], x -> ({case_when_part})))"

        if regex_prefix_search:
            codes_part = ", ".join([f"'{code}%'" for code in definition_codes])
            self.sql_rule = f"""
                WITH codes_to_compare AS (SELECT DISTINCT UNNEST([{codes_part}]) AS code_to_compare)
                SELECT DISTINCT row_index_id, TRUE AS {indicator_name}
                FROM (
                    SELECT a.row_index_id, ARRAY_LENGTH(ARRAY_AGG(codes_where)) AS n_diag_match,
                           FIRST(n_diag_no_null) AS n_diag_no_null
                    FROM (
                        SELECT row_index_id, UNNEST({query_where}) AS codes_where, ARRAY_LENGTH({query_where}) AS n_diag_no_null
                        FROM main.dataframe_
                        WHERE ARRAY_LENGTH({query_where}) > 0
                    ) a
                    LEFT JOIN codes_to_compare b
                    ON a.codes_where LIKE b.code_to_compare
                    WHERE b.code_to_compare IS NOT NULL
                    GROUP BY a.row_index_id
                )
                WHERE n_diag_match = n_diag_no_null
            """
        else:
            codes_part = ", ".join([f"'{code}'" for code in definition_codes])
            self.sql_rule = f"""
                WITH codes_to_compare AS (SELECT DISTINCT UNNEST([{codes_part}]) AS code_to_compare)
                SELECT DISTINCT row_index_id, TRUE AS {indicator_name}
                FROM (
                    SELECT a.row_index_id, ARRAY_LENGTH(ARRAY_AGG(codes_where)) AS n_diag_match,
                           FIRST(n_diag_no_null) AS n_diag_no_null
                    FROM (
                        SELECT row_index_id, UNNEST({query_where}) AS codes_where, ARRAY_LENGTH({query_where}) AS n_diag_no_null
                        FROM main.dataframe_
                        WHERE ARRAY_LENGTH({query_where}) > 0
                    ) a
                    LEFT JOIN codes_to_compare b
                    ON a.codes_where = b.code_to_compare
                    WHERE b.code_to_compare IS NOT NULL
                    GROUP BY a.row_index_id
                )
                WHERE n_diag_match = n_diag_no_null
            """


class CustomMatch(SqlRuleIndicator):
    """
    A class that creates a custom SQL indicator based on user-defined logic, allowing
    for flexible evaluation of conditions within a dataset.

    Args:
        indicator_name (str): A string representing the name of the indicator.
        sql_logic (str): A string containing the custom SQL logic to be applied for evaluation.

    Returns:
        CustomMatch: An instance of the CustomMatch class with the generated SQL query.

    Details:
        When a `CustomMatch` indicator depends on another previously calculated indicator,
        the required indicator must appear before the `CustomMatch` in the list of
        indicators provided to the `RuleEngine`.
        Additionally, the user must ensure that all variables referenced in the `CustomMatch`
        are present in the data frame.

    Examples:
        >>> import pandas as pd
        >>> from indicpy4health import RuleEngine, MatchAny, CustomMatch, run_indicators
        >>> hosp_dataframe = pd.DataFrame({
        >>>     "episode_id": [1, 2, 3],
        >>>     "age": [45, 60, 32],
        >>>     "sex": ["M", "F", "M"],
        >>>     "diagnosis1": ["F10.10", "I20", "I60"],
        >>>     "diagnosis2": ["E11", "J45", "I25"],
        >>>     "diagnosis3": ["I60", "K35", "F10.120"]
        >>> })
        >>>
        >>> reng = RuleEngine(hosp_dataframe, "episode_id")
        >>>
        >>> target_columns = ["diagnosis1"]
        >>>
        >>> definition_codes = ["F10.10", "F10.11", "F10.120", "F10.121"]
        >>>
        >>> alcohol_indicator = MatchAll(
        >>>     reng,
        >>>     "alcohol_i",
        >>>     target_columns,
        >>>     definition_codes
        >>> )
        >>> custom_alcohol_indicator = CustomMatch(
        >>>     "alcohol_i_plus40",  # Name of the indicator
        >>>     "alcohol_i AND age >= 40"  # Logic of the indicator
        >>> )
        >>> indicators_list = [alcohol_indicator, custom_alcohol_indicator]
        >>>
        >>> run_indicators(
        >>>     reng,
        >>>     indicators_list,
        >>>     append_results=False,
        >>>    csv_path="./results.csv"
        >>> )

    References:
        Explore all the logical operators you can use in DuckDB:
        https://duckdb.org/docs/stable/sql/query_syntax/where
    """

    def __init__(self, indicator_name: str, sql_logic: str):
        if not isinstance(indicator_name, str):
            raise TypeError("The 'indicator_name' argument must be of type str.")
        if not isinstance(sql_logic, str):
            raise TypeError("The 'sql_logic' argument must be of type str.")

        self.name = indicator_name
        self.sql_rule = f"""
            SELECT DISTINCT row_index_id, TRUE AS {indicator_name}
            FROM main.dataframe_
            WHERE {sql_logic}
        """
