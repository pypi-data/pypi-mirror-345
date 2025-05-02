import re
from secrets import choice
from string import ascii_letters, digits
from typing import Literal

import dns.resolver as resolver


class DomainValidator:
    """
    A class to validate domain names and generate verification codes.
    """

    def __init__(self, ascii_only: bool = False, domain_max_length: int = 255):
        # Unicode domain name pattern with support for Hindi characters
        self.domain_re = (
            r"^((?!-)[\w\u0900-\u097F-]{1,63}(?<!-)"
            r"\.(?!-)[\w\u0900-\u097F-]{1,63}(?<!-))*$"
        )
        self.ascii_only = ascii_only  # Flag to use only ASCII characters
        self.domain_max_length = domain_max_length  # Maximum length of the domain name

        if self.ascii_only:
            self.re_pattern = re.compile(self.domain_re, re.ASCII | re.IGNORECASE)
        else:
            self.re_pattern = re.compile(self.domain_re, re.UNICODE | re.IGNORECASE)

    def validate_domain_re(self, domain: str) -> bool:
        """
        Validate the given domain name matches the regular expression.

        Parameters:
            domain -- The domain name to validate.

        Returns:
            bool -- True if the domain name is a valid format, False otherwise.
        """
        if not domain:
            raise ValueError("Domain cannot be empty.")
        if not isinstance(domain, str):
            raise ValueError("Domain must be a string.")
        return bool(self.re_pattern.match(domain))

    def validate_domain_length(self, domain: str) -> bool:
        """
        Validate the length of the domain name.

        Parameters:
            domain -- The domain name to validate.

        Returns:
            bool -- True if the domain name length is valid, False otherwise.
        """
        if not domain:
            raise ValueError("Domain cannot be empty.")
        if not isinstance(domain, str):
            raise ValueError("Domain must be a string.")
        return len(domain) <= self.domain_max_length

    def validate_domain_dns(self, domain: str) -> bool:
        """
        Check if the domain name is valid by checking DNS resolution.

        Parameters:
            domain -- The domain name to validate.

        Returns:
            bool -- True if the domain name is valid, False otherwise.
        """
        try:
            resolver.resolve(domain, "NS")
            return True
        except (resolver.NXDOMAIN, resolver.NoAnswer):
            return False

    def validate_domain_name(self, domain: str) -> bool:
        """
        Validate the domain name by checking its format, length, and DNS resolution.

        Parameters:
            domain -- The domain name to validate.

        Returns:
            bool -- True if the domain name is valid, False otherwise.
        """
        if not self.validate_domain_re(domain):
            return False
        if not self.validate_domain_length(domain):
            return False
        if not self.validate_domain_dns(domain):
            return False
        return True

    def unicode_to_punycode(self, domain: str) -> str:
        """
        Convert a Unicode domain name to Punycode for ASCII compliance.

        Parameters:
            domain -- The Unicode domain name to convert.

        Returns:
            str -- The Punycode representation of the domain name.
        """
        if self.validate_domain_re(domain) is False:
            raise ValueError("Invalid domain name.")
        try:
            return domain.encode("idna").decode("ascii")
        except Exception as e:
            raise ValueError(f"Error converting to Punycode: {e}")

    def punycode_to_unicode(self, domain: str) -> str:
        """
        Convert a Punycode domain name to Unicode.

        Parameters:
            domain -- The Punycode domain name to convert.

        Returns:
            str -- The Unicode representation of the domain name.
        """
        if self.validate_domain_re(domain) is False:
            raise ValueError("Invalid domain name.")
        try:
            return domain.encode("ascii").decode("idna")
        except Exception as e:
            raise ValueError(f"Error converting to Unicode: {e}")

    def generate_txt_code(
        self, prefix: str, length: int = 26, sep: Literal["=", "-", "_", "|"] = "="
    ) -> str:
        """
        Generate a random verification code for TXT record with a prefix.

        Parameters:
            prefix -- Prefix to identify who generated the code.
            length -- Length of the random code to generate.
            sep -- Separator between the prefix and the code.

        Returns:
            str -- Generated string with TXT verification code.
        """
        if not prefix:
            raise ValueError("Prefix cannot be empty.")
        if not isinstance(prefix, str):
            raise ValueError("Prefix must be a string.")
        if not isinstance(length, int) or length <= 0:
            raise ValueError("Length must be a positive integer.")
        code = "".join(choice(ascii_letters + digits) for _ in range(length))
        return f"{prefix}{sep}{code}"

    def verify_txt_code(self, domain: str, txt_code: str) -> bool:
        """
        Verify the TXT records for the domain contain the provided code.

        Parameters:
            domain -- Domain being verified.
            txt_code -- Code string to verify in TXT record.

        Returns:
            bool -- True if a TXT record contains the code, False otherwise.
        """
        try:
            response = resolver.resolve(domain, "TXT")
            for rdata in response:
                if f"{txt_code}" == rdata.strings[0].decode("utf-8"):
                    return True
        except (resolver.NXDOMAIN, resolver.NoAnswer) as e:
            print(f"Error resolving TXT records: {e}")
        return False


domain_validator = DomainValidator()
