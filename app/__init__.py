from app.ice_manager import ice_manager, get_ice_meta

__all__ = ["ice_manager", "get_ice_meta"]

def __getattr__(name: str):
    """
    Lazy module attribute resolution for backward compatibility.
    Allows `from app import meta` without connecting to Ice on import.
    """
    if name == "meta":
        return ice_manager.get_meta()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
