class LightspeedError(Exception):
    """Base exception for all Lightspeed-related errors."""


class LightspeedConnectionError(LightspeedError):
    """Raised when the WebSocket connection fails or is unavailable."""


class OrderRejectedError(LightspeedError):
    """Raised when an order is rejected by the API."""


class InvalidOrderError(LightspeedError):
    """Raised when required fields or values are missing in the order."""
