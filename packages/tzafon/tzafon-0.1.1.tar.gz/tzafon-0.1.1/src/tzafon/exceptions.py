class WaypointError(Exception):
    """Base for all SDK exceptions."""


class ScreenshotFailed(WaypointError):
    """Raised when screenshot returns success=False."""
