class CustomError(Exception):
    """Base class for package exceptions"""

class GeocoderError(CustomError):
    """Raised when a geocoding error occurs"""
