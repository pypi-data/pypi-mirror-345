from .tracker import init, log_run

# Make these functions available directly as module attributes
__all__ = ['init', 'log_run']

# Expose the functions at the module level
init = init
log_run = log_run