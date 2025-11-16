"""
Callback registration module.
Imports all callback modules to register them with the Dash app.
"""

from .upload import import_me as upload_import_me  # noqa: F401
from .metrics import import_me as metrics_import_me  # noqa: F401
from .gen_mix_ipps import import_me as gen_mix_ipps_import_me  # noqa: F401
from .plant_generation_profiles import import_me as plant_generation_profiles_import_me  # noqa: F401
from .analysis_chosen import import_me as analysis_chosen_import_me  # noqa: F401
from .consumer_analysis import import_me as consumer_analysis_import_me  # noqa: F401
from .time_series import import_me as time_series_import_me  # noqa: F401

def register_callbacks(app):
    """
    Register all application callbacks.

    Note: Callbacks are automatically registered when the module is imported,
    so this function currently serves as a placeholder for future explicit
    callback registration if needed.

    Args:
        app: The Dash application instance
    """
    pass


__all__ = ["register_callbacks"]
