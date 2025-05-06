import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Union
from urllib.parse import urlencode

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from cfsign.config import CfSignConfig, GlobalConfig
from cfsign.exceptions import WildcardUrlNotSupportedError
from cfsign.types import CfCookieDictKey, CloudfrontSignatureDict, CloudfrontSignatureQueryParams, UrlQueryParamKey

__all__ = ("CloudfrontSignature",)


COOKIE_KEY_TO_URL_QUERY_PARAM_KEY: Dict[CfCookieDictKey, UrlQueryParamKey] = {
    "CloudFront-Policy": "Policy",
    "CloudFront-Signature": "Signature",
    "CloudFront-Key-Pair-Id": "Key-Pair-Id",
}


class CloudfrontSignature:
    _resource_url: str
    """The URL of the CloudFront resource to be accessed, can include wildcards (e.g. 'https://some-domain.telemetry.fm/video/*') or a specific URL (e.g. 'https://some-domain.telemetry.fm/video/some-video-id')"""

    _expiration_time: datetime
    """The time at which the cookie will expire, calculated as the current time plus the expires_in argument"""

    def __init__(
        self, resource_url: str, expires_in: timedelta = timedelta(minutes=30), config: Union[CfSignConfig, None] = None
    ) -> None:
        """
        Initializes the signed cookie generator.
        Args:
            resource_url (str): The URL of the resource for which the cookie is being generated (e.g. 'https://some-domain.telemetry.fm/video/*') or a specific URL (e.g. 'https://some-domain.telemetry.fm/video/some-video-id').
            expires_in (timedelta, optional): The duration for which the cookie is valid. Defaults to 30 minutes.
        Attributes:
            _resource_url (str): The URL of the resource for which the cookie is being generated.
            _expiration_time (datetime): The expiration time of the cookie.
        """
        if config:
            self._config = config
        else:
            self._config = GlobalConfig.get_config()
        self._resource_url = resource_url
        self._expiration_time = datetime.now(tz=timezone.utc) + expires_in
        self.__cookie_dict: Union[CloudfrontSignatureDict, None] = None

    @property
    def cookie_dict(self) -> CloudfrontSignatureDict:
        """Return a dictionary containing the signed cookie components.

        The dictionary contains three keys:
        - CloudFront-Policy: Base64-encoded policy document
        - CloudFront-Signature: Base64-encoded signature of the policy
        - CloudFront-Key-Pair-Id: The ID of the key pair used to sign the policy

        Returns:
            dict[CfCookieDictKey, str]: Dictionary containing the signed cookie components
        """
        if self.__cookie_dict is None:
            self.__cookie_dict = self.__generate_signed_cookie()
        return self.__cookie_dict

    @property
    def expiration_ts(self) -> int:
        """Return the expiration time as a Unix timestamp"""
        return int(self._expiration_time.timestamp())

    @property
    def cookie_str(self) -> str:
        """Return the cookies as a string suitable for use in an HTTP header or FFMPEG command"""
        cookies_header = "; ".join([f"{key}={value}" for key, value in self.cookie_dict.items()])
        return f"Cookie: {cookies_header}\r\n"

    @property
    def signed_url(self) -> str:
        """Return the signed URL as a string suitable for use in a browser or HTTP client.

        The signed URL includes the policy, signature, and key pair ID as query parameters.
        This method does not support wildcard URLs - use cookies, headers or query_params instead.

        Returns:
            str: The signed URL with authentication query parameters

        Raises:
            WildcardUrlNotSupportedError: If the resource URL contains a wildcard
        """

        if self._resource_url.endswith("/*"):
            raise WildcardUrlNotSupportedError(
                "Wildcard URLs are not supported with signed URLs use a specific URL instead or use cookies, headers, or `query_params`"
            )
        url_with_cookies = f"{self._resource_url}?{self.query_string}"
        return url_with_cookies

    @property
    def query_params(self) -> CloudfrontSignatureQueryParams:
        """Return the query parameters as a dictionary suitable for use in a URL.

        The dictionary contains three keys:
        - Policy: Base64-encoded policy document
        - Signature: Base64-encoded signature of the policy
        - Key-Pair-Id: The ID of the key pair used to sign the policy

        Returns:
            CloudfrontSignatureQueryParams: Dictionary containing the signed URL query parameters
        """
        return {COOKIE_KEY_TO_URL_QUERY_PARAM_KEY[key]: value for key, value in self.cookie_dict.items()}  # type: ignore

    @property
    def query_string(self) -> str:
        """Return the query string as a string suitable for use in a URL, e.g. `Policy=...&Signature=...&Key-Pair-Id=...`"""
        query_string = urlencode(self.query_params)
        return query_string

    def __rsa_signer(self, policy: bytes) -> bytes:
        """Sign the policy using RSA private key"""
        signature = self._config.private_key.sign(policy, padding.PKCS1v15(), hashes.SHA1())
        return signature

    def __generate_signed_cookie(self) -> CloudfrontSignatureDict:
        """Generate a signed cookie for CloudFront.

        This method creates a signed cookie that can be used to access protected CloudFront content.
        It generates a policy document, signs it with the private key, and returns the necessary
        cookie components.

        Returns:
            dict[CfCookieDictKey, str]: A dictionary containing the signed cookie components:
                - CloudFront-Policy: Base64 encoded policy document
                - CloudFront-Signature: Base64 encoded signature of the policy
                - CloudFront-Key-Pair-Id: The ID of the key pair used for signing
        """
        policy = self.__create_policy()

        # Sign the policy
        signed_policy = self.__rsa_signer(policy.encode("utf-8"))

        # Encode policy and signature to base64
        encoded_policy = base64.b64encode(policy.encode("utf-8")).decode("utf-8")
        encoded_signature = base64.b64encode(signed_policy).decode("utf-8")

        # Return the necessary cookies for CloudFront
        return {
            "CloudFront-Policy": encoded_policy,
            "CloudFront-Signature": encoded_signature,
            "CloudFront-Key-Pair-Id": self._config.key_pair_id,
        }

    def __create_policy(self) -> str:
        """Create a policy document for CloudFront signed URLs/cookies.

        The policy document specifies what the signed URL/cookie grants access to and when it expires.

        Returns:
            str: A JSON string containing the policy document with the resource URL and expiration time.
        """
        policy = {
            "Statement": [
                {"Resource": self._resource_url, "Condition": {"DateLessThan": {"AWS:EpochTime": self.expiration_ts}}}
            ]
        }
        return json.dumps(policy)
