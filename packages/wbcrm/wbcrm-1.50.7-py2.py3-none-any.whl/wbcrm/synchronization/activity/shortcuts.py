from dynamic_preferences.registries import global_preferences_registry
from wbcore.utils.importlib import import_from_dotted_path


def get_backend():
    from wbcrm.synchronization.activity.controller import ActivityController

    if backend := global_preferences_registry.manager()["wbactivity_sync__sync_backend_calendar"]:
        backend = import_from_dotted_path(backend)
        return ActivityController(backend=backend)
