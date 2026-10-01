"""Hook names and what each one receives.

before_check(url, settings)          may return a CheckResult to replace the check
after_check(result, settings)        may return a changed CheckResult
before_report(results, summary)      may return a changed list of results
"""

BEFORE_CHECK = "before_check"
AFTER_CHECK = "after_check"
BEFORE_REPORT = "before_report"

HOOK_NAMES = (BEFORE_CHECK, AFTER_CHECK, BEFORE_REPORT)

DEFAULT_PRIORITY = 100
BUILTIN_PRIORITY = 900
