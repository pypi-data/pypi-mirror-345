import inspect

from fi.evals.evaluator import EvalClient  # noqa: F401
from fi.evals.protect import ProtectClient  # noqa: F401
from fi.evals.templates import *  # noqa: F403, F401

# Dynamically generate __all__ from imported templates
_globals = globals()
evaluation_template_names = [
    name
    for name, obj in _globals.items()
    if inspect.isclass(obj) and obj.__module__ == "fi.evals.templates"
]

# Add the clients separately
client_names = ["EvalClient", "ProtectClient"]

# Combine and sort for consistency
__all__ = sorted(evaluation_template_names + client_names)
