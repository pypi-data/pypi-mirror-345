from typing import Literal

from typing_extensions import TypedDict

__all__ = ("CfCookieDictKey", "CloudfrontSignatureDict", "CloudfrontSignatureQueryParams", "UrlQueryParamKey")

CfCookieDictKey = Literal["CloudFront-Policy", "CloudFront-Signature", "CloudFront-Key-Pair-Id"]
UrlQueryParamKey = Literal["Policy", "Signature", "Key-Pair-Id"]

CloudfrontSignatureDict = TypedDict(
    "CloudfrontSignatureDict",
    {
        "CloudFront-Policy": str,
        "CloudFront-Signature": str,
        "CloudFront-Key-Pair-Id": str,
    },
)

CloudfrontSignatureQueryParams = TypedDict(
    "CloudfrontSignatureQueryParams",
    {
        "Policy": str,
        "Signature": str,
        "Key-Pair-Id": str,
    },
)
