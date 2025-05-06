r"""
**IndicPy4Health** is a lightweight, fast, and intuitive package for indicator calculations in healthcare.

IndicPy4Health provides the four most commonly used logics for health data indicator calculations:

- **MatchAny**

- **MatchAll**

- **MatchAnyWhere**

- **MatchAllWhere**

Additionally, it offers a fifth logic, **CustomMatch**, which allows combining these logics with patient-related or episode-based rules.
"""


from .ruleEngine import RuleEngine, run_indicators, MatchAll, CustomMatch, MatchAny, MatchAllWhere, MatchAnyWhere

__all__ = ['RuleEngine', 'MatchAll', 'CustomMatch', 'MatchAny', 'MatchAllWhere', 'MatchAnyWhere', 'run_indicators']
