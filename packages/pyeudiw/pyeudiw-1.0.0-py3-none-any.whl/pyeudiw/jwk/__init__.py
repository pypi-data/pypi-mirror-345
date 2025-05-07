from __future__ import annotations

import json
from typing import Union

from cryptography.hazmat.primitives import serialization
from cryptojwt.jwk.ec import new_ec_key
from cryptojwt.jwk.jwk import key_from_jwk_dict
from cryptojwt.jwk.rsa import new_rsa_key

from pyeudiw.jwk.exceptions import InvalidKid, KidNotFoundError

KEY_TYPES_FUNC = dict(EC=new_ec_key, RSA=new_rsa_key)


class JWK:
    """
    The class representing a JWK istance
    """

    def __init__(
        self,
        key: Union[dict, None] = None,
        key_type: str = "EC",
        hash_func: str = "SHA-256",
        ec_crv: str = "P-256",
    ) -> None:
        """
        Creates an instance of JWK.

        :param key: An optional key in dict form.
        If no key is provided a randomic key will be generated.
        :type key: Union[dict, None]
        :param key_type: a string that represents the key type. Can be EC or RSA.
        :type key_type: str
        :param hash_func: a string that represents the hash function to use with the instance.
        :type hash_func: str
        :param ec_crv: a string that represents the curve to use with the instance.
        :type ec_crv: str

        :raises NotImplementedError: the key_type is not implemented
        """
        kwargs = {}
        self.kid = ""

        if key_type and not KEY_TYPES_FUNC.get(key_type, None):
            raise NotImplementedError(f"JWK key type {key_type} not found.")

        if key:
            if isinstance(key, dict):
                self.key = key_from_jwk_dict(key)
                key_type = key.get("kty", key_type)
                self.kid = key.get("kid", "")
            else:
                self.key = key
        else:
            # create new one
            if key_type in ["EC", None]:
                kwargs["crv"] = ec_crv
            self.key = KEY_TYPES_FUNC[key_type or "EC"](**kwargs)

        self.thumbprint = self.key.thumbprint(hash_function=hash_func)
        self.jwk = self.key.to_dict()
        self.jwk["kid"] = self.kid or self.thumbprint.decode()
        self.public_key = self.key.serialize()
        self.public_key["kid"] = self.jwk["kid"]

    def as_json(self) -> str:
        """
        Returns the JWK in format of json string.

        :returns: A json string that represents the key.
        :rtype: str
        """
        return json.dumps(self.jwk)

    def export_private_pem(self) -> str:
        """
        Returns the JWK in format of a private pem certificte.

        :returns: A private pem certificate that represents the key.
        :rtype: str
        """
        _k = key_from_jwk_dict(self.jwk)
        pk = _k.private_key()
        pem = pk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return pem.decode()

    def export_public_pem(self) -> str:
        """
        Returns the JWK in format of a public pem certificte.

        :returns: A public pem certificate that represents the key.
        :rtype: str
        """
        _k = key_from_jwk_dict(self.jwk)
        pk = _k.public_key()
        cert = pk.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return cert.decode()

    def as_dict(self) -> dict:
        """
        Returns the JWK in format of dict.

        :returns: The key in form of dict.
        :rtype: dict
        """
        return self.jwk

    def as_public_dict(self) -> dict:
        """
        Returns the public key in format of dict.
        :returns: The public key in form of dict.
        :rtype: dict
        """
        return self.public_key

    def __repr__(self) -> str:
        # private part!
        return self.as_json()
