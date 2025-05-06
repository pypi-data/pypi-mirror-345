import warnings

# Show deprecation warning first
warnings.warn(
    "This package is deprecated. "
    "Please use 'agent-squad' instead (pip install agent-squad). "
    "Note: Class names have been changed to reflect the new package name, please refer to the documentation at: https://awslabs.github.io/agent-squad/"
    "https://pypi.org/project/agent-squad/",
    DeprecationWarning,
    stacklevel=2
)

# Keep existing functionality
from .shared import user_agent
user_agent.inject_user_agent()
