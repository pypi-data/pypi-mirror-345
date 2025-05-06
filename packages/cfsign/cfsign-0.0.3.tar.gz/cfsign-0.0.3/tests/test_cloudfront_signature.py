import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import cfsign
from cfsign import CfSignConfig, CloudfrontSignature
from cfsign.exceptions import ConfigurationNotSetError
from cfsign.exceptions.cloudfront_signature_errors import WildcardUrlNotSupportedError


def test_cloudfront_signature_with_no_config() -> None:
    with pytest.raises(ConfigurationNotSetError):
        CloudfrontSignature(
            resource_url="https://example.com/test.txt",
            expires_in=timedelta(days=1),
        )


def test_cloudfront_signature_with_global_config(config: CfSignConfig) -> None:
    cfsign.configure(config.key_pair_id, config.private_key)
    now = datetime.now(tz=timezone.utc)
    signature = CloudfrontSignature(
        resource_url="https://example.com/test.txt",
        expires_in=timedelta(days=1),
    )
    then = datetime.now(tz=timezone.utc)
    assert signature._resource_url == "https://example.com/test.txt"
    assert signature._expiration_time > now + timedelta(days=1)
    assert signature._expiration_time < then + timedelta(days=1)

    assert signature.cookie_dict["CloudFront-Key-Pair-Id"] == config.key_pair_id

    def decode_b64_policy(policy: str) -> Any:
        return json.loads(base64.b64decode(policy).decode("utf-8"))

    assert decode_b64_policy(signature.cookie_dict["CloudFront-Policy"]) == {
        "Statement": [
            {
                "Resource": "https://example.com/test.txt",
                "Condition": {"DateLessThan": {"AWS:EpochTime": signature.expiration_ts}},
            }
        ]
    }


def test_cloudfront_signature_override_config(config: CfSignConfig) -> None:
    cfsign.configure(config.key_pair_id, config.private_key)
    new_config = CfSignConfig(
        key_pair_id="OVERRIDE",
        private_key=config.private_key,
    )

    signature = CloudfrontSignature(
        resource_url="https://example.com/test.txt",
        expires_in=timedelta(days=1),
        config=new_config,
    )

    assert signature._config is new_config
    assert signature.cookie_dict["CloudFront-Key-Pair-Id"] == "OVERRIDE"


def test_cloudfront_signature_cookie_string(config: CfSignConfig) -> None:
    cfsign.configure("TEST", config.private_key)
    signature = CloudfrontSignature(
        resource_url="https://example.com/test.txt",
        expires_in=timedelta(days=1),
    )
    expiration_time = datetime(2025, 4, 28, 12, 0, 0, 0, timezone.utc)
    signature._expiration_time = expiration_time

    assert (
        signature.cookie_str
        == "Cookie: CloudFront-Policy=eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6ICJodHRwczovL2V4YW1wbGUuY29tL3Rlc3QudHh0IiwgIkNvbmRpdGlvbiI6IHsiRGF0ZUxlc3NUaGFuIjogeyJBV1M6RXBvY2hUaW1lIjogMTc0NTg0MTYwMH19fV19; CloudFront-Signature=BPqEgkm8Mktcwx8LyCAU0vP+ydCH7rh/i/BFpITtOAYRS/1v5cZ85wx7qg0GqeEA7E8yQYYbUow+2qHrfakHE45YSD7qsMZ+qCTxTlA1cJS4TqVMzaxFK/afYDTIgrVZ+zV/3LHj0Boarj9wKDcqMg7Iw5bVvDYeH0O5mMUSINvZ7fgwU1S2kN6HWXpN0Y7BviD7G4QWrAoiB936fvkTPR1rvCAxF+zdksSAsf4gAwB6Botghi/b5UE2m7mGiOmblKTa20+BpK1PSURUFkFFe4AFY80XBvZWkIyKq6N1xNSI0RvlizFUZ7Um1OMRTTqWsyxxQ21LIztisXuM7PAMsQ==; CloudFront-Key-Pair-Id=TEST\r\n"
    )


def test_cloudfront_signature_query_params(config: CfSignConfig) -> None:
    cfsign.configure("TEST", config.private_key)
    signature = CloudfrontSignature(
        resource_url="https://example.com/test.txt",
        expires_in=timedelta(days=1),
    )
    expiration_time = datetime(2025, 4, 28, 12, 0, 0, 0, timezone.utc)
    signature._expiration_time = expiration_time

    assert signature.query_params == {
        "Policy": "eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6ICJodHRwczovL2V4YW1wbGUuY29tL3Rlc3QudHh0IiwgIkNvbmRpdGlvbiI6IHsiRGF0ZUxlc3NUaGFuIjogeyJBV1M6RXBvY2hUaW1lIjogMTc0NTg0MTYwMH19fV19",
        "Signature": "BPqEgkm8Mktcwx8LyCAU0vP+ydCH7rh/i/BFpITtOAYRS/1v5cZ85wx7qg0GqeEA7E8yQYYbUow+2qHrfakHE45YSD7qsMZ+qCTxTlA1cJS4TqVMzaxFK/afYDTIgrVZ+zV/3LHj0Boarj9wKDcqMg7Iw5bVvDYeH0O5mMUSINvZ7fgwU1S2kN6HWXpN0Y7BviD7G4QWrAoiB936fvkTPR1rvCAxF+zdksSAsf4gAwB6Botghi/b5UE2m7mGiOmblKTa20+BpK1PSURUFkFFe4AFY80XBvZWkIyKq6N1xNSI0RvlizFUZ7Um1OMRTTqWsyxxQ21LIztisXuM7PAMsQ==",
        "Key-Pair-Id": "TEST",
    }


def test_cloudfront_signature_signed_url(config: CfSignConfig) -> None:
    cfsign.configure("TEST", config.private_key)
    signature = CloudfrontSignature(
        resource_url="https://example.com/test.txt",
        expires_in=timedelta(days=1),
    )
    expiration_time = datetime(2025, 4, 28, 12, 0, 0, 0, timezone.utc)
    signature._expiration_time = expiration_time

    assert (
        signature.signed_url
        == "https://example.com/test.txt?Policy=eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6ICJodHRwczovL2V4YW1wbGUuY29tL3Rlc3QudHh0IiwgIkNvbmRpdGlvbiI6IHsiRGF0ZUxlc3NUaGFuIjogeyJBV1M6RXBvY2hUaW1lIjogMTc0NTg0MTYwMH19fV19&Signature=BPqEgkm8Mktcwx8LyCAU0vP%2BydCH7rh%2Fi%2FBFpITtOAYRS%2F1v5cZ85wx7qg0GqeEA7E8yQYYbUow%2B2qHrfakHE45YSD7qsMZ%2BqCTxTlA1cJS4TqVMzaxFK%2FafYDTIgrVZ%2BzV%2F3LHj0Boarj9wKDcqMg7Iw5bVvDYeH0O5mMUSINvZ7fgwU1S2kN6HWXpN0Y7BviD7G4QWrAoiB936fvkTPR1rvCAxF%2BzdksSAsf4gAwB6Botghi%2Fb5UE2m7mGiOmblKTa20%2BBpK1PSURUFkFFe4AFY80XBvZWkIyKq6N1xNSI0RvlizFUZ7Um1OMRTTqWsyxxQ21LIztisXuM7PAMsQ%3D%3D&Key-Pair-Id=TEST"
    )


def test_cloudfront_signature_query_string(config: CfSignConfig) -> None:
    cfsign.configure("TEST", config.private_key)
    signature = CloudfrontSignature(
        resource_url="https://example.com/test.txt",
        expires_in=timedelta(days=1),
    )
    expiration_time = datetime(2025, 4, 28, 12, 0, 0, 0, timezone.utc)
    signature._expiration_time = expiration_time

    assert (
        signature.query_string
        == "Policy=eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6ICJodHRwczovL2V4YW1wbGUuY29tL3Rlc3QudHh0IiwgIkNvbmRpdGlvbiI6IHsiRGF0ZUxlc3NUaGFuIjogeyJBV1M6RXBvY2hUaW1lIjogMTc0NTg0MTYwMH19fV19&Signature=BPqEgkm8Mktcwx8LyCAU0vP%2BydCH7rh%2Fi%2FBFpITtOAYRS%2F1v5cZ85wx7qg0GqeEA7E8yQYYbUow%2B2qHrfakHE45YSD7qsMZ%2BqCTxTlA1cJS4TqVMzaxFK%2FafYDTIgrVZ%2BzV%2F3LHj0Boarj9wKDcqMg7Iw5bVvDYeH0O5mMUSINvZ7fgwU1S2kN6HWXpN0Y7BviD7G4QWrAoiB936fvkTPR1rvCAxF%2BzdksSAsf4gAwB6Botghi%2Fb5UE2m7mGiOmblKTa20%2BBpK1PSURUFkFFe4AFY80XBvZWkIyKq6N1xNSI0RvlizFUZ7Um1OMRTTqWsyxxQ21LIztisXuM7PAMsQ%3D%3D&Key-Pair-Id=TEST"
    )


def test_cloudfront_signature_signed_url_with_wildcard(config: CfSignConfig) -> None:
    cfsign.configure("TEST", config.private_key)
    signature = CloudfrontSignature(
        resource_url="https://example.com/*",
        expires_in=timedelta(days=1),
    )
    with pytest.raises(WildcardUrlNotSupportedError):
        signature.signed_url  # noqa: B018
