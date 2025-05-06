import fnmatch
import hashlib
import logging
import re
from typing import Dict, List, Tuple, Union
from urllib.parse import ParseResult, parse_qsl, urlencode, urlparse

# Uses https://gist.github.com/Integralist/edcfb88c925658a13fc3e51f581fe4bc as a starting point
# Modified for more current rules regarding host/domain/tld naming.

# not stripping out fragments currently

ip_middle_octet = r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
ip_last_octet = r"(?:\.(?:[0-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"

regex = re.compile(
    r"^"
    # protocol identifier
    r"(?:(?:https?|ftp)://)"
    # user:pass authentication (updated to avoid catastrophic backtracking)
    r"(?:[a-zA-Z0-9._%+-]+(?::[^\s@]*)?@)?"
    r"(?:"
    r"(?P<private_ip>"
    # IP address exclusion
    # private & local networks
    r"(?:(?:10|127)" + ip_middle_octet + "{2}" + ip_last_octet + ")|"
    r"(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + ")|"
    r"(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + "))"
    r"|"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    r"(?P<public_ip>"
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"" + ip_middle_octet + "{2}"
    r"" + ip_last_octet + ")"
    r"|"
    # host name (modified: handles multiple hyphens, underscores in hostnames, and trailing hyphens)
    r"(?:(?:[a-z\-_\u00a1-\uffff0-9]-?)*[a-z_\u00a1-\uffff0-9\-]+)"
    # domain name (modified: handles multiple hyphens, and also underscores in domain names, and trailing hyphens)
    r"(?:\.(?:[a-z\-_\u00a1-\uffff0-9]-?)*[a-z_\u00a1-\uffff0-9\-]+)*"
    # TLD identifier (modified: handles oddities like site.xn--p1ai/)
    r"(?:\.(?:[a-z0-9\-\u00a1-\uffff]{2,}))"
    r")"
    # port number
    r"(?::\d{2,5})?"
    # resource path
    r"(?:/\S*)?"
    # query string
    r"(?:\?\S*)?"
    r"$",
    re.UNICODE | re.IGNORECASE,
)

pattern = re.compile(regex)


class InvalidUrlException(Exception):
    def __init__(self, message: str, original_exception: Exception) -> None:
        super().__init__(message)
        self.original_exception = original_exception


class URLNormalizer:
    # Define the list of query parameters to remove -- This should be removed if we're not using the canonicalized url
    query_params_to_remove: List[str] = [
        "utm_*",
        "gclid",
        "fbclid",
        "dclid",
        "_ga",
        "_gid",
        "_fbp",
        "_hjid",
        "msclkid",
        "aff_id",
        "affid",
        "referrer",
        "adgroupid",
        "srsltid",
    ]

    def __init__(self, url: str, log_errors: bool = True) -> None:
        try:
            url = url.strip()
            self.log_errors: bool = log_errors
            self.logger = logging.getLogger(__name__)
            self.original_url: str = url
            self.normalized_url: str
            self.canonicalized_url: str
            self.parent_canonical_url: str
            self.root_canonical_url: str
            self.unique_params: List[Tuple[str, str]]
            self.fragment: str
            (
                self.unique_params,
                self.normalized_url,
                self.canonicalized_url,
                self.parent_canonical_url,
                self.root_canonical_url,
                self.fragment,
            ) = self.normalize_url(url)
            self.url_hashes: Dict[str, str] = self.compute_hashes()
        except InvalidUrlException as e:
            if self.log_errors:
                self.logger.warning(f"{e}")
            raise e
        except Exception as e:
            m = f"Invalid URL (exception): {url}"
            if self.log_errors:
                self.logger.error(m)
            raise InvalidUrlException(m, e) from e

    def normalize_url(self, url: str) -> Tuple[str, str, str]:
        url = self.lowercase_url(url)
        parsed_url = self.parse_url(url)
        netloc, path, query, fragment = self.validate_url(parsed_url)
        netloc = self.remove_www_subdomain(netloc)
        path = self.remove_trailing_slash(path)
        query_params = self.parse_query_params(query)
        query_params = self.sort_query_params(query_params)
        unique_params = self.remove_duplicate_params(query_params)
        cleaned_query_params = self.remove_unwanted_params(unique_params)
        canonicalized_url = self.rebuild_url(netloc, path, cleaned_query_params)
        parent_canonical_url = self.get_parent_canonical_url(netloc)
        root_canonical_url = self.get_root_canonical_url(netloc)
        normalized_url = self.get_normalized_url(netloc, path)
        return unique_params, normalized_url, canonicalized_url, parent_canonical_url, root_canonical_url, fragment

    @staticmethod
    def lowercase_url(url: str) -> str:
        return url.lower() if url else url

    @staticmethod
    def parse_url(url: str) -> ParseResult:
        parsed_url: ParseResult = urlparse(url)

        # Handle URLs with neither scheme nor netloc
        if not parsed_url.scheme and not parsed_url.netloc:
            parsed_url = urlparse(f"http://{url}")

        return parsed_url

    @staticmethod
    def validate_url(parsed_url: ParseResult) -> Tuple[str, str, str]:
        # This will also capture localhost by its nature
        if "." not in parsed_url.netloc:
            raise InvalidUrlException(
                f"Invalid URL provided (no dots) '{parsed_url.geturl()}'",
                ValueError(f"URLs without a tld are forbidden. '{parsed_url.netloc}'"),
            )

        # Only http(s) urls are currently allowed; this means no file, ftp, etc.
        if not str(parsed_url.scheme).startswith("http"):
            raise InvalidUrlException(
                f"Invalid URL provided (non-HTTP) '{parsed_url.geturl()}'",
                ValueError(f"Only http(s) URLs are currently allowed, received: '{parsed_url.scheme}'"),
            )

        # Some oddball or broken URLs will be caught here
        if not parsed_url.scheme or not parsed_url.netloc:
            raise InvalidUrlException(
                f"Invalid URL provided: (empty) '{parsed_url.geturl()}'",
                ValueError(f"URL could not be parsed. '{parsed_url.netloc}'"),
            )

        # Check again the mega regular-expression
        if not pattern.match(parsed_url.geturl()):
            raise InvalidUrlException(
                f"Invalid URL provided (regex.fail) '{parsed_url.geturl()}'", ValueError("URL failed regex check.")
            )

        return parsed_url.netloc, parsed_url.path, parsed_url.query, parsed_url.fragment

    @staticmethod
    def remove_www_subdomain(netloc: str) -> str:
        return netloc[4:] if str(netloc).startswith("www.") else netloc

    @staticmethod
    def remove_trailing_slash(path: str) -> str:
        return path.rstrip("/")

    @staticmethod
    def parse_query_params(query: str) -> List[Tuple[str, str]]:
        return parse_qsl(query, keep_blank_values=True)

    def remove_unwanted_params(self, query_params: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        def is_unwanted_param(param: str) -> bool:
            return any(fnmatch.fnmatch(param, pattern) for pattern in self.query_params_to_remove)

        return [(k, v) for k, v in query_params if not is_unwanted_param(k)]

    @staticmethod
    def sort_query_params(query_params: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        return sorted(query_params, key=lambda x: (x[0], x[1]))

    @staticmethod
    def remove_duplicate_params(query_params: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        seen_params: set = set()
        unique_params: List[Tuple[str, str]] = []
        for param in query_params:
            if param not in seen_params:
                seen_params.add(param)
                unique_params.append(param)
        return unique_params

    @staticmethod
    def rebuild_url(netloc: str, path: str, query_params: List[Tuple[str, str]]) -> str:
        query_string: str = urlencode(query_params)
        return f"{netloc}{path}?{query_string}" if query_string else f"{netloc}{path}"

    @staticmethod
    def get_parent_canonical_url(netloc: str) -> str:
        return netloc

    @staticmethod
    def get_root_canonical_url(netloc: str) -> str:
        return ".".join(netloc.split(".")[-2:])

    @staticmethod
    def get_normalized_url(netloc: str, path: str) -> str:
        return f"{netloc}{path}"

    def compute_hashes(self) -> Dict[str, str]:
        def sha256_hash(value: str) -> str:
            return hashlib.sha256(value.encode()).hexdigest()

        return {
            "normalized_url_hash": sha256_hash(self.normalized_url),
            "canonicalized_url_hash": sha256_hash(self.canonicalized_url),
            "parent_canonical_url_hash": sha256_hash(self.parent_canonical_url),
            "root_canonical_url_hash": sha256_hash(self.root_canonical_url),
        }

    def get_canonicalized_url(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return {
            "canonicalized_url": self.canonicalized_url,
            "parent_canonical_url": self.parent_canonical_url,
            "root_canonical_url": self.root_canonical_url,
            "normalized_url": self.normalized_url,
            "unique_params": self.unique_params,
            "fragment": self.fragment,
            "original_url": self.original_url,
            **self.url_hashes,
        }


def normalize_this(url: str) -> str:
    """
    This is specifically for the snowflake UDF.
    Normalize a URL and return the normalized URL.
    """
    try:
        normalizer = URLNormalizer(url)
        return normalizer.get_canonicalized_url()["normalized_url"]
    except InvalidUrlException:
        return None


if __name__ == "__main__":  # pragma: no cover
    url1 = "http://www.Example.com/some-sub-folder/or_page.html?b=2&a=1&a=1&b=2&c=3&bad_param=some_value"
    url2 = "http://blog.example.com/some-folder/some-page.html?b=2&a=1&a=1&b=2&c=3&bad_param=another_value"
    url3 = "http://www.example.com/some-sub-folder/or_page.html?b=2&a=1&a=1&b=2&c=3&bad_param=some_value#fragment"

    try:
        normalizer1 = URLNormalizer(url1)
        print(normalizer1.get_canonicalized_url())
    except InvalidUrlException as e:
        print(f"Error: {e}")

    try:
        normalizer2 = URLNormalizer(url2)
        print(normalizer2.get_canonicalized_url())
    except InvalidUrlException as e:
        print(f"Error: {e}")

    try:
        normalizer3 = URLNormalizer(url3)
        print(normalizer3.get_canonicalized_url())
    except InvalidUrlException as e:
        print(f"Error: {e}")

    print(normalize_this("http://new page, url tbd"))
