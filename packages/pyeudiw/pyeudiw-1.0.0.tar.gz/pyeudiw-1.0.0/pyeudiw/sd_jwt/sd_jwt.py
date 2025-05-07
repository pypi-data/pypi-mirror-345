import json
import logging
from hashlib import sha256
from typing import Any, Callable, TypeVar

from cryptojwt.jwk.ec import ECKey
from cryptojwt.jwk.rsa import RSAKey

from pyeudiw.jwt.jws_helper import JWSHelper
from pyeudiw.jwt.parse import DecodedJwt
from pyeudiw.jwt.utils import base64_urldecode, base64_urlencode
from pyeudiw.jwt.verification import verify_jws_with_key
from pyeudiw.sd_jwt.common import SDJWTCommon
from pyeudiw.sd_jwt.exceptions import InvalidKeyBinding, UnsupportedSdAlg, MissingConfirmationKey
from pyeudiw.sd_jwt.schema import (
    VerifierChallenge,
    is_sd_jwt_format,
)

from pyeudiw.sd_jwt import DEFAULT_SD_ALG, DIGEST_ALG_KEY, SD_DIGESTS_KEY, SD_LIST_PREFIX

_JsonTypes = dict | list | str | int | float | bool | None
_JsonTypes_T = TypeVar("_JsonTypes_T", bound=_JsonTypes)


FORMAT_SEPARATOR = SDJWTCommon.COMBINED_SERIALIZATION_FORMAT_SEPARATOR

SUPPORTED_SD_ALG_FN: dict[str, Callable[[str], str]] = {
    "sha-256": lambda s: base64_urlencode(sha256(s.encode("ascii")).digest())
}

logger = logging.getLogger(__name__)


class SdJwt:
    """
    SdJwt is an utility class to easily parse and verify sd jwt.
    All class attributes are intended to be read only
    """

    def __init__(self, token: str):
        if not is_sd_jwt_format(token):
            raise ValueError(
                f"input [token]={token} is not an sd-jwt with: maybe it is a regular jwt?"
            )
        self.token = token
        # precomputed values
        self.token_without_kb: str = ""
        self.issuer_jwt: DecodedJwt = DecodedJwt("", "", "", "")
        self.disclosures: list[str] = []
        self.holder_kb: DecodedJwt | None = None
        self._post_init_precomputed_values()

    def _post_init_precomputed_values(self):
        iss_jwt, *disclosures, kb_jwt = self.token.split(FORMAT_SEPARATOR)
        self.token_without_kb = (
            iss_jwt
            + FORMAT_SEPARATOR
            + "".join(disc + FORMAT_SEPARATOR for disc in disclosures)
        )
        self.issuer_jwt = DecodedJwt.parse(iss_jwt)
        self.disclosures = disclosures
        if kb_jwt:
            self.holder_kb = DecodedJwt.parse(kb_jwt)
        # TODO: schema validations(?)

    def get_confirmation_key(self) -> dict:
        """
        Get the confirmation key from the issuer payload claims.

        :raises MissingConfirmationKey: if the confirmation key is missing

        :return: the confirmation key
        :rtype: dict
        """

        cnf: dict = self.issuer_jwt.payload.get("cnf", {}).get("jwk", {})
        if not cnf:
            raise MissingConfirmationKey(
                "missing confirmation (cnf) key from issuer payload claims"
            )
        return cnf

    def get_disclosed_claims(self) -> dict:
        """
        Get the disclosed claims from the issuer payload

        :raises UnsupportedSdAlg: if the sd_alg is not supported
        :raises ValueError: if there are duplicate digests

        :return: the disclosed claims
        :rtype: dict
        """

        return _extract_claims_from_payload(
            self.issuer_jwt.payload,
            self.disclosures,
            SUPPORTED_SD_ALG_FN[self.get_sd_alg()],
        )

    def get_issuer_jwt(self) -> DecodedJwt:
        """
        Get the issuer jwt

        :return: the issuer jwt
        :rtype: DecodedJwt
        """
        return self.issuer_jwt

    def get_holder_key_binding_jwt(self) -> str:
        """
        Get the holder key binding jwt

        :return: the holder key binding jwt
        :rtype: str
        """

        return self.holder_kb.jwt

    def get_sd_alg(self) -> str:
        """
        Get the sd_alg from the issuer jwt

        :return: the sd_alg
        :rtype: str
        """
        return self.issuer_jwt.payload.get("_sd_alg", DEFAULT_SD_ALG)

    def has_key_binding(self) -> bool:
        """
        Check if the token has a key binding

        :return: True if the token has a key binding, False otherwise
        :rtype: bool
        """
        return self.holder_kb is not None

    def verify_issuer_jwt_signature(
        self, keys: list[ECKey | RSAKey | dict] | ECKey | RSAKey | dict
    ) -> None:
        """
        Verify the issuer jwt signature

        :param keys: the public key(s) to use to verify the issuer jwt signature
        :type keys: list[ECKey | RSAKey | dict] | ECKey | RSAKey | dict

        :raises JWSVerificationError: if the verification fails
        """
        jws_verifier = JWSHelper(keys)
        jws_verifier.verify(self.issuer_jwt.jwt)

    def verify_holder_kb_jwt(self, challenge: VerifierChallenge) -> None:
        """
        Checks validity of holder key binding.
        This procedure always passes when no key binding is used

        :raises UnsupportedSdAlg: if verification fails due to an unkown _sd_alg
        :raises InvalidKeyBinding: if the verification fails for an invalid key binding
        :raises ValueError: if the iat claim is missing or invalid
        :raises JWSVerificationError: if the verification fails
        """
        if not self.has_key_binding():
            return
        _verify_key_binding(
            self.token_without_kb, self.get_sd_alg(), self.holder_kb, challenge
        )
        self.verify_holder_kb_jwt_signature()

    def verify_holder_kb_jwt_signature(self) -> None:
        """
        Verify the holder key binding signature

        :raises JWSVerificationError: if the verification fails
        """
        if not self.has_key_binding():
            return
        cnf: dict = self.get_confirmation_key()
        verify_jws_with_key(self.holder_kb.jwt, cnf)


def _verify_challenge(hkb: DecodedJwt, challenge: VerifierChallenge) -> None:
    """
    Verify the challenge in the key binding

    :param hkb: the holder key binding
    :type hkb: DecodedJwt
    :param challenge: the challenge to verify
    :type challenge: VerifierChallenge

    :raises InvalidKeyBinding: if the challenge is invalid
    """

    if (obt := hkb.payload.get("aud", None)) != (exp := challenge["aud"]):
        raise InvalidKeyBinding(
            f"challenge audience {exp} does not match obtained audience {obt}"
        )
    if (obt := hkb.payload.get("nonce", None)) != (exp := challenge["nonce"]):
        raise InvalidKeyBinding(
            f"challenge nonce {exp} does not match obtained nonce {obt}"
        )


def _verify_sd_hash(token_without_hkb: str, sd_hash_alg: str, expected_digest: str) -> None:
    """
    Verify the sd-jwt hash

    :param token_without_hkb: the token without the holder key binding
    :type token_without_hkb: str
    :param sd_hash_alg: the algorithm to use to hash the token without the holder key binding
    :type sd_hash_alg: str
    :param expected_digest: the expected digest
    :type expected_digest: str

    :raises UnsupportedSdAlg: if the sd_alg is not supported
    :raises InvalidKeyBinding: if the key binding is invalid
    """

    hash_fn = SUPPORTED_SD_ALG_FN.get(sd_hash_alg, None)
    if not hash_fn:
        raise UnsupportedSdAlg(f"unsupported sd_alg: {sd_hash_alg}")
    if expected_digest != (obt_digest := hash_fn(token_without_hkb)):
        raise InvalidKeyBinding(
            f"sd-jwt digest {obt_digest} does not match expected digest {expected_digest}"
        )


def _verify_iat(payload: dict) -> None:
    """
    Verify the iat claim in the payload

    :param payload: the payload of the issuer jwt
    :type payload: dict

    :raises ValueError: if the iat claim is missing or invalid
    """

    # we check that 'iat' claim exists, according to sd-jwt specs, but since its a standard claim,
    # its value is validated by the general purpose token verification tool JWSHelper accordidng to
    # its own rules
    
    iat: int | None = payload.get("iat", None)
    if not isinstance(iat, int):
        raise ValueError("missing or invalid parameter [iat] in kbjwt")


def _verify_key_binding(
    token_without_hkb: str,
    sd_hash_alg: str,
    hkb: DecodedJwt,
    challenge: VerifierChallenge,
) -> None:
    """
    Verify the key binding in the sd-jwt

    :param token_without_hkb: the token without the holder key binding
    :type token_without_hkb: str
    :param sd_hash_alg: the algorithm to use to hash the token without the holder key binding
    :type sd_hash_alg: str
    :param hkb: the holder key binding
    :type hkb: DecodedJwt
    :param challenge: the challenge to verify
    :type challenge: VerifierChallenge

    :raises InvalidKeyBinding: if the key binding is invalid
    :raises UnsupportedSdAlg: if the sd_alg is not supported
    :raises ValueError: if the iat claim is missing or invalid
    """

    _verify_challenge(hkb, challenge)
    _verify_sd_hash(
        token_without_hkb, sd_hash_alg, hkb.payload.get("sd_hash", "sha-256")
    )
    _verify_iat(hkb.payload)


def _disclosures_to_hash_mappings(
    disclosures: list[str], sd_alg: Callable[[str], str]
) -> tuple[dict[str, str], dict[str, Any]]:
    """
    Convert a list of disclosures to a map of digests to disclosures

    :param disclosures: a list of base64 encoded disclosures
    :type disclosures: list[str]
    :param sd_alg: the function to use to hash the disclosures
    :type sd_alg: Callable[[str], str]

    :raises ValueError: if there are duplicate digests

    :returns: in order
        (i)  hash_to_disclosure, a map: digest -> raw disclosure (base64 encoded)
        (ii) hash_to_dec_disclosure, a map: digest -> decoded disclosure
    :rtype: tuple[dict[str, str], dict[str, Any]]
    """
    hash_to_disclosure: dict[str, str] = {}
    hash_to_dec_disclosure: dict[str, Any] = {}

    for disclosure in disclosures:
        decoded_disclosure = json.loads(base64_urldecode(disclosure).decode("utf-8"))
        digest = sd_alg(disclosure)
    
        if digest in hash_to_dec_disclosure:
            raise ValueError(f"duplicate disclosure for digest {digest}")
    
        hash_to_dec_disclosure[digest] = decoded_disclosure
        hash_to_disclosure[digest] = disclosure
    
    return hash_to_disclosure, hash_to_dec_disclosure


def _extract_claims_from_payload(
    payload: dict, disclosures: list[str], sd_alg: Callable[[str], str]
) -> dict:
    """
    Extract the disclosed claims from the payload

    :param payload: the payload of the issuer jwt
    :type payload: dict
    :param disclosures: a list of base64 encoded disclosures
    :type disclosures: list[str]
    :param sd_alg: the function to use to hash the disclosures
    :type sd_alg: Callable[[str], str]

    :raises ValueError: if there are duplicate digests

    :returns: the disclosed claims
    :rtype: dict
    """

    _, hash_to_dec_disclosure = _disclosures_to_hash_mappings(
        disclosures, sd_alg
    )
    return _unpack_claims(payload, hash_to_dec_disclosure, sd_alg, [])


def _is_element_leaf(element: Any) -> bool:
    """
    Check if an element is a leaf in the json tree

    :param element: the element to check
    :type element: Any

    :returns: True if the element is a leaf, False otherwise
    :rtype: bool
    """
    return (
        type(element) is dict
        and len(element) == 1
        and SD_LIST_PREFIX in element
        and type(element[SD_LIST_PREFIX]) is str
    )


def _unpack_json_array(
    claims: list,
    decoded_disclosures_by_digest: dict[str, Any],
    sd_alg: Callable[[str], str],
    processed_digests: list[str],
) -> list:
    """
    Unpack the disclosed claims in the payload

    :param claims: the claims to unpack
    :type claims: list
    :param decoded_disclosures_by_digest: a map of digests to decoded disclosures
    :type decoded_disclosures_by_digest: dict[str, Any]
    :param sd_alg: the function to use to hash the disclosures
    :type sd_alg: Callable[[str], str]
    :param processed_digests: a list of processed digests
    :type processed_digests: list[str]

    :raises ValueError: if there are duplicate digests

    :returns: the unpacked claims
    :rtype: list
    """

    result = []
    for element in claims:
        if _is_element_leaf(element):
            digest: str = element[SD_LIST_PREFIX]
            if digest in decoded_disclosures_by_digest:
                _, value = decoded_disclosures_by_digest[digest]
                result.append(
                    _unpack_claims(
                        value, decoded_disclosures_by_digest, sd_alg, processed_digests
                    )
                )
        else:
            result.append(
                _unpack_claims(
                    element, decoded_disclosures_by_digest, sd_alg, processed_digests
                )
            )
    return result


def _unpack_json_dict(
    claims: dict,
    decoded_disclosures_by_digest: dict[str, Any],
    sd_alg: Callable[[str], str],
    proceessed_digests: list[str],
) -> dict:
    """
    Unpack the disclosed claims in the payload

    :param claims: the claims to unpack
    :type claims: dict
    :param decoded_disclosures_by_digest: a map of digests to decoded disclosures
    :type decoded_disclosures_by_digest: dict[str, Any]
    :param sd_alg: the function to use to hash the disclosures
    :type sd_alg: Callable[[str], str]
    :param proceessed_digests: a list of processed digests
    :type proceessed_digests: list[str]

    :raises ValueError: if there are duplicate digests

    :returns: the unpacked claims
    :rtype: dict
    """

    # First, try to figure out if there are any claims to be
    # disclosed in this dict. If so, replace them by their
    # disclosed values.
    filtered_unpacked_claims = {}
    for k, v in claims.items():
        if k != SD_DIGESTS_KEY and k != DIGEST_ALG_KEY:
            filtered_unpacked_claims[k] = _unpack_claims(
                v, decoded_disclosures_by_digest, sd_alg, proceessed_digests
            )

    for disclosed_digests in claims.get(SD_DIGESTS_KEY, []):
        if disclosed_digests in proceessed_digests:
            raise ValueError(f"duplicate hash found in SD-JWT: {disclosed_digests}")
        proceessed_digests.append(disclosed_digests)

        if disclosed_digests in decoded_disclosures_by_digest:
            _, key, value = decoded_disclosures_by_digest[disclosed_digests]
            if key in filtered_unpacked_claims:
                raise ValueError(
                    f"duplicate key found when unpacking disclosed claim: '{key}' in {filtered_unpacked_claims}; this is not allowed."
                )
            unpacked_value = _unpack_claims(
                value, decoded_disclosures_by_digest, sd_alg, proceessed_digests
            )
            filtered_unpacked_claims[key] = unpacked_value
    return filtered_unpacked_claims


def _unpack_claims(
    claims: _JsonTypes_T,
    decoded_disclosures_by_digest: dict[str, Any],
    sd_alg: Callable[[str], str],
    proceessed_digests: list[str],
) -> _JsonTypes_T:
    """
    Unpack the disclosed claims in the payload

    :param claims: the claims to unpack
    :type claims: _JsonTypes_T
    :param decoded_disclosures_by_digest: a map of digests to decoded disclosures
    :type decoded_disclosures_by_digest: dict[str, Any]
    :param sd_alg: the function to use to hash the disclosures
    :type sd_alg: Callable[[str], str]
    :param proceessed_digests: a list of processed digests
    :type proceessed_digests: list[str]

    :raises ValueError: if there are duplicate digests

    :returns: the unpacked claims
    :rtype: _JsonTypes_T
    """

    if type(claims) is list:
        return _unpack_json_array(
            claims, decoded_disclosures_by_digest, sd_alg, proceessed_digests
        )
    elif type(claims) is dict:
        return _unpack_json_dict(
            claims, decoded_disclosures_by_digest, sd_alg, proceessed_digests
        )
    else:
        return claims
