from . import SD_DIGESTS_KEY

class InvalidKeyBinding(Exception):
    pass


class UnsupportedSdAlg(Exception):
    pass

class MissingConfirmationKey(Exception):
    """
    Raised when a given VP not contain a confirmation key
    """
    pass

class SDJWTHasSDClaimException(Exception):
    """Exception raised when input data contains the special _sd claim reserved for SD-JWT internal data."""

    def __init__(self, error_location: any):
        super().__init__(
            f"Input data contains the special claim '{SD_DIGESTS_KEY}' reserved for SD-JWT internal data. Location: {error_location!r}"
        )
