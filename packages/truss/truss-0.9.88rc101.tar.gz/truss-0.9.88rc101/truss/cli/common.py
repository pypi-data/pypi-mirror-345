import sys

POLL_INTERVAL_SEC = 2


def check_is_interactive() -> bool:
    """Detects if CLI is operated interactively by human, so we can ask things,
    that we would want to skip for automated subprocess/CI contexts."""
    return sys.stdin.isatty() and sys.stdout.isatty()
