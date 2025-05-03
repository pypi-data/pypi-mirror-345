class AztpError(Exception):
    """Base exception for all AZTP client errors."""
    pass


class ConfigurationError(AztpError):
    """Raised when there is a configuration error."""
    pass


class AuthenticationError(AztpError):
    """Raised when authentication fails."""
    pass


class IdentityError(AztpError):
    """Raised when there is an error with identity operations."""
    pass


class CertificateError(AztpError):
    """Raised when there is an error with certificate operations."""
    pass


class NetworkError(AztpError):
    """Raised when there is a network-related error."""
    pass 