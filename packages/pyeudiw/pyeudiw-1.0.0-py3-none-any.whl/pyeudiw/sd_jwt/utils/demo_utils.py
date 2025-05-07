import logging
import random
import sys
import yaml
from cryptojwt.jwk.jwk import key_from_jwk_dict

logger = logging.getLogger("sd_jwt")


def load_yaml_settings(file):
    with open(file, "r") as f:
        settings = yaml.safe_load(f)

    for property in ("identifiers", "key_settings"):
        if property not in settings:
            sys.exit(f"Settings file must define '{property}'.")

    # 'issuer_key' can be used instead of 'issuer_keys' in the key settings; will be converted to an array anyway
    if "issuer_key" in settings["key_settings"]:
        if "issuer_keys" in settings["key_settings"]:
            sys.exit("Settings file cannot define both 'issuer_key' and 'issuer_keys'.")

        settings["key_settings"]["issuer_keys"] = [
            settings["key_settings"]["issuer_key"]
        ]

    return settings


def get_jwk(jwk_kwargs: dict = {}, no_randomness: bool = False, random_seed: int = 0):
    """
    jwk_kwargs = {
        issuer_keys:list : [{}],
        holder_key:dict : {},
        key_size: int : 0,
        kty: str : "RSA"
    }

    returns static or random JWK
    """

    if no_randomness:
        random.seed(random_seed)
        issuer_keys = [key_from_jwk_dict(k) for k in jwk_kwargs["issuer_keys"]]
        holder_key = key_from_jwk_dict(jwk_kwargs["holder_key"])
    else:
        _kwargs = {"key_size": jwk_kwargs["key_size"], "kty": jwk_kwargs["kty"]}
        issuer_keys = [key_from_jwk_dict(_kwargs)]
        holder_key = key_from_jwk_dict(_kwargs)

    _issuer_public_keys = []
    _issuer_public_keys.extend([k.serialize() for k in issuer_keys])

    return dict(
        issuer_keys=[k.serialize(private=True) for k in issuer_keys],
        holder_key=holder_key.serialize(private=True),
        issuer_public_keys=_issuer_public_keys,
    )
