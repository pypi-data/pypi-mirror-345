#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements a PEG (Parsing Expression Grammar) to parse
#    syntax, i add rules to parse URL, HTTP request and response easily
#    with security and some format like hexadecimal, base32, base64,
#    base85...
#    Copyright (C) 2025  PegParser

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements a PEG (Parsing Expression Grammar) to parse
syntax, i add rules to parse URL, HTTP request and response easily
with security and some format like hexadecimal, base32, base64,
base85...

Tests:
~# python3 -m doctest PegParser.py
~# python3 -m doctest -v PegParser.py

36 items had no tests:
    PegParser
    PegParser.HttpRequest
    PegParser.HttpRequest.__eq__
    PegParser.HttpRequest.__init__
    PegParser.HttpRequest.__repr__
    PegParser.HttpResponse
    PegParser.HttpResponse.__eq__
    PegParser.HttpResponse.__init__
    PegParser.HttpResponse.__repr__
    PegParser.MatchList
    PegParser.MatchList.__init__
    PegParser.PegParser
    PegParser.PegParser.and_predicate
    PegParser.PegParser.not_predicate
    PegParser.PegParser.one_or_more
    PegParser.PegParser.ordered_choice
    PegParser.PegParser.sequence
    PegParser.PegParser.zero_or_more
    PegParser.StandardMatch
    PegParser.StandardMatch.check_char
    PegParser.StandardMatch.or_check_chars
    PegParser.StandardRules
    PegParser.StandardRules.Format
    PegParser.StandardRules.Http
    PegParser.StandardRules.Network
    PegParser.StandardRules.Types
    PegParser.StandardRules.Url
    PegParser.StandardRules.Url._base_path
    PegParser.StandardRules.Url._character_subdelims_colon_commat
    PegParser.StandardRules.Url._character_subdelims_colon_commat_slot_quest
    PegParser.StandardRules.Url._characters
    PegParser.StandardRules.Url._characters_subdelims_colon
    PegParser.StandardRules.Url._characters_subdelims_colon_commat
    PegParser.StandardRules.Url._optional_characters_subdelims_colon_commat
    PegParser.StandardRules.Url._optional_characters_subdelims_colon_commat_slot_quest
    PegParser.get_http_content
60 items passed all tests:
   3 tests in PegParser.HttpRequest.__bytes__
   3 tests in PegParser.HttpResponse.__bytes__
   3 tests in PegParser.StandardMatch.is_blank
   4 tests in PegParser.StandardMatch.is_digit
   5 tests in PegParser.StandardMatch.is_hex
   4 tests in PegParser.StandardMatch.is_letter
   4 tests in PegParser.StandardMatch.is_lower
   5 tests in PegParser.StandardMatch.is_octal
   6 tests in PegParser.StandardMatch.is_printable
   4 tests in PegParser.StandardMatch.is_special
   4 tests in PegParser.StandardMatch.is_upper
   9 tests in PegParser.StandardRules.Format.base32
   8 tests in PegParser.StandardRules.Format.base64
   6 tests in PegParser.StandardRules.Format.base85
   6 tests in PegParser.StandardRules.Format.hex
   6 tests in PegParser.StandardRules.Format.integer
   6 tests in PegParser.StandardRules.Format.octal
   5 tests in PegParser.StandardRules.Format.word
   2 tests in PegParser.StandardRules.Http.field_name
   2 tests in PegParser.StandardRules.Http.field_value
   2 tests in PegParser.StandardRules.Http.header
   1 tests in PegParser.StandardRules.Http.headers
   5 tests in PegParser.StandardRules.Http.is_text_char
   2 tests in PegParser.StandardRules.Http.magic
   2 tests in PegParser.StandardRules.Http.protocol_version
   2 tests in PegParser.StandardRules.Http.reason
   2 tests in PegParser.StandardRules.Http.request
   1 tests in PegParser.StandardRules.Http.response
   2 tests in PegParser.StandardRules.Http.response_start
   2 tests in PegParser.StandardRules.Http.status_code
   2 tests in PegParser.StandardRules.Http.text
   2 tests in PegParser.StandardRules.Http.token
   8 tests in PegParser.StandardRules.Http.verb
   2 tests in PegParser.StandardRules.Http.version
   7 tests in PegParser.StandardRules.Network.fqdn
   9 tests in PegParser.StandardRules.Network.host
   9 tests in PegParser.StandardRules.Network.host_port
   7 tests in PegParser.StandardRules.Network.hostname
  12 tests in PegParser.StandardRules.Network.ipv4
  16 tests in PegParser.StandardRules.Network.ipv6
   8 tests in PegParser.StandardRules.Network.ipv6_zoneid
   7 tests in PegParser.StandardRules.Network.ipvfuture
   3 tests in PegParser.StandardRules.Network.user_info
   6 tests in PegParser.StandardRules.Types.bool
   6 tests in PegParser.StandardRules.Types.digits
   6 tests in PegParser.StandardRules.Types.float
   5 tests in PegParser.StandardRules.Types.hex_integer
   8 tests in PegParser.StandardRules.Types.octal_integer
  10 tests in PegParser.StandardRules.Types.string
   8 tests in PegParser.StandardRules.Url.form_data
   4 tests in PegParser.StandardRules.Url.fragment
  10 tests in PegParser.StandardRules.Url.full
   9 tests in PegParser.StandardRules.Url.parameters
  11 tests in PegParser.StandardRules.Url.path
   4 tests in PegParser.StandardRules.Url.path_rootless
   9 tests in PegParser.StandardRules.Url.query
   6 tests in PegParser.StandardRules.Url.scheme
   1 tests in PegParser.get_matchs
   1 tests in PegParser.parse_http_request
   1 tests in PegParser.parse_http_response
313 tests in 96 items.
313 passed and 0 failed.
Test passed.
"""

__version__ = "0.0.2"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements a PEG (Parsing Expression Grammar) to parse
syntax, i add rules to parse URL, HTTP request and response easily
with security and some format like hexadecimal, base32, base64,
base85...
"""
__url__ = "https://github.com/mauricelambert/PegParser"

__all__ = [
    "HttpResponse",
    "HttpRequest",
    "MatchList",
    "PegParser",
    "StandardMatch",
    "StandardRules",
    "get_matchs",
    "parse_http_request",
    "parse_http_response",
]

__license__ = "GPL-3.0 License"
__copyright__ = """
PegParser  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

print(copyright)

from typing import Callable, List, Iterable, Union, Tuple, Dict
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class HttpResponse:
    magic: bytes
    version: float
    code: int
    reason: str
    headers: List[Tuple[str, str]]
    body: bytes
    content_length: int = 0
    content_type: str = None

    def __bytes__(self) -> bytes:
        r"""
        This magic method returns bytes for the full response
        in the HTTP format.

        >>> bytes(HttpResponse(b'HTTP', 1.0, 200, 'OK', [], b'body content'))
        b"HTTP/1.0 200 OK\r\nContent-Length: 12\r\nServer: Maurice Lambert's HTTP server\r\n\r\nbody content"
        >>> bytes(HttpResponse(b'HTTP', 1.1, 201, 'Created', [('Content-Length', '12'), ('Content-Type', 'application/json'), ('Server', 'TestServer')], b'', 10, 'plain/text'))
        b'HTTP/1.1 201 Created\r\nContent-Length: 12\r\nContent-Type: application/json\r\nServer: TestServer\r\n\r\n'
        >>> bytes(HttpResponse(b'HTTP', 1.0, 202, 'Accepted', [], b'body content', 10, 'plain/text'))
        b"HTTP/1.0 202 Accepted\r\nContent-Type: plain/text\r\nContent-Length: 10\r\nServer: Maurice Lambert's HTTP server\r\n\r\nbody content"
        >>>
        """

        content_length = len(self.body)
        set_content_length = False
        set_content_type = False
        set_server = False
        headers = bytearray()

        for header, value in self.headers:
            header = header.title().encode("ascii")
            if header == b"Content-Length":
                set_content_length = True
            elif header == b"Content-Type":
                set_content_type = True
            elif header == b"Server":
                set_server = True
            headers.extend(header + b": " + value.encode("ascii") + b"\r\n")

        if self.body and not set_content_type and self.content_type:
            headers.extend(
                b"Content-Type: " + self.content_type.encode("ascii") + b"\r\n"
            )

        if content_length and not set_content_length:
            if self.content_length:
                headers.extend(
                    b"Content-Length: "
                    + str(self.content_length).encode("ascii")
                    + b"\r\n"
                )
            else:
                headers.extend(
                    b"Content-Length: "
                    + str(content_length).encode("ascii")
                    + b"\r\n"
                )

        if not set_server:
            headers.extend(
                b"Server: "
                + __author__.encode("ascii")
                + b"'s HTTP server\r\n"
            )

        return (
            self.magic
            + b"/"
            + str(self.version).encode("ascii")
            + b" "
            + str(self.code).encode("ascii")
            + b" "
            + self.reason.encode("ascii")
            + b"\r\n"
            + headers
            + b"\r\n"
            + self.body
        )


@dataclass
class HttpRequest:
    verb: str
    uri: str
    magic: bytes
    version: float
    headers: List[Tuple[str, str]]
    body: bytes
    content_length: int = 0
    content_type: str = None
    host: str = None

    def __bytes__(self) -> bytes:
        r"""
        This magic method returns bytes for the full request
        in the HTTP format.

        >>> bytes(HttpRequest('GET', '/', b'HTTP', 1.0, [], b'body content'))
        b"GET / HTTP/1.0\r\nContent-Length: 12\r\nUser-Agent: Maurice Lambert's HTTP client\r\n\r\nbody content"
        >>> bytes(HttpRequest('POST', '/upload', b'HTTP', 1.1, [('Content-Length', '12'), ('Content-Type', 'application/json'), ('User-Agent', 'TestClient')], b'', 10, 'plain/text'))
        b'POST /upload HTTP/1.1\r\nContent-Length: 12\r\nContent-Type: application/json\r\nUser-Agent: TestClient\r\n\r\n'
        >>> bytes(HttpRequest('HEAD', '/wp-admin?user=admin', b'HTTP', 1.0, [], b'body content', 10, 'plain/text'))
        b"HEAD /wp-admin?user=admin HTTP/1.0\r\nContent-Type: plain/text\r\nContent-Length: 10\r\nUser-Agent: Maurice Lambert's HTTP client\r\n\r\nbody content"
        >>>
        """

        content_length = len(self.body)
        set_content_length = False
        set_content_type = False
        set_user_agent = False
        headers = bytearray()

        for header, value in self.headers:
            header = header.title().encode("ascii")
            if header == b"Content-Length":
                set_content_length = True
            elif header == b"Content-Type":
                set_content_type = True
            elif header == b"User-Agent":
                set_user_agent = True
            headers.extend(header + b": " + value.encode("ascii") + b"\r\n")

        if self.body and not set_content_type and self.content_type:
            headers.extend(
                b"Content-Type: " + self.content_type.encode("ascii") + b"\r\n"
            )

        if content_length and not set_content_length:
            if self.content_length:
                headers.extend(
                    b"Content-Length: "
                    + str(self.content_length).encode("ascii")
                    + b"\r\n"
                )
            else:
                headers.extend(
                    b"Content-Length: "
                    + str(content_length).encode("ascii")
                    + b"\r\n"
                )

        if not set_user_agent:
            headers.extend(
                b"User-Agent: "
                + __author__.encode("ascii")
                + b"'s HTTP client\r\n"
            )

        return (
            self.verb.encode("ascii")
            + b" "
            + self.uri.encode("ascii")
            + b" "
            + self.magic
            + b"/"
            + str(self.version).encode("ascii")
            + b"\r\n"
            + headers
            + b"\r\n"
            + self.body
        )


class MatchList(list):
    """
    Simple list with hidden argument to identify match.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._match_name = None


class PegParser:
    """
    This class implements methods for a PEG parser.
    """

    def sequence(
        rules: Iterable[Callable], data: bytes, position: int
    ) -> Tuple[int, Union[None, List[bytes]]]:
        """
        This method implements the PEG `sequence`
        ("match 2 elements").
        """

        backup_position = position
        results = MatchList()

        for rule in rules:
            position, result = rule(data, position)
            if result is None:
                return backup_position, None
            results.append(result)

        return position, results

    def ordered_choice(
        rules: Iterable[Callable], data: bytes, position: int
    ) -> Tuple[int, Union[None, bytes]]:
        """
        This method implements the PEG `ordered choice`
        ("OR" operator, like "|" in regex).
        """

        backup_position = position

        for rule in rules:
            position, result = rule(data, position)
            if result is not None:
                return position, result

        return backup_position, None

    def and_predicate(
        first: Callable, data: bytes, position: int
    ) -> Tuple[int, Union[None, bytes]]:
        """
        This method implements the PEG `and predicate`
        ("match without consume data" | position is always the same).
        """

        return position, first(data, position)[1] is not None or None

    def not_predicate(
        first: Callable, data: bytes, position: int
    ) -> Tuple[int, Union[None, bool]]:
        """
        This method implements the PEG `not predicate`
        ("don't match without consume data" | position is always the same).
        """

        return position, first(data, position)[1] is None or None

    def zero_or_more(
        first: Callable, data: bytes, position: int
    ) -> Tuple[int, List[bytes]]:
        """
        This method implements the PEG `zero or more` or `optional`
        (like "*" in regex).
        """

        results = MatchList()
        position_first, result_first = first(data, position)

        while result_first:
            position = position_first
            results.append(result_first)
            position_first, result_first = first(data, position)

        return position, results

    def one_or_more(
        first: Callable, data: bytes, position: int
    ) -> Tuple[int, Union[None, List[bytes]]]:
        """
        This method implements the PEG `one or more`
        (like "+" in regex).
        """

        position, result = PegParser.zero_or_more(first, data, position)
        return (position, result or None)


class StandardMatch:
    """
    This class implements method for standard match element.
    """

    def is_letter(
        data: bytes, position: int
    ) -> Tuple[int, Union[None, bytes]]:
        """
        This method checks a position for an ASCII letter (upper or lower case).

        >>> StandardMatch.is_letter(b"a1Bc", 0)
        (1, b'a')
        >>> StandardMatch.is_letter(b"a1Bc", 1)
        (1, None)
        >>> StandardMatch.is_letter(b"a1Bc", 2)
        (3, b'B')
        >>> len([x for x in range(256) if StandardMatch.is_letter(bytes((x,)), 0)[1] is not None])
        52
        >>>
        """

        result = StandardMatch.is_lower(data, position)

        if result[1] is None:
            return StandardMatch.is_upper(data, position)

        return result

    def is_lower(data: bytes, position: int) -> Tuple[int, Union[None, bytes]]:
        """
        This method checks a position for an ASCII lower case letter.

        >>> StandardMatch.is_lower(b"a1Bc", 0)
        (1, b'a')
        >>> StandardMatch.is_lower(b"a1Bc", 1)
        (1, None)
        >>> StandardMatch.is_lower(b"a1Bc", 2)
        (2, None)
        >>> len([x for x in range(256) if StandardMatch.is_lower(bytes((x,)), 0)[1] is not None])
        26
        >>>
        """

        if len(data) == position:
            return position, None

        char = data[position]
        if 97 <= char <= 122:
            return position + 1, bytes((char,))
        return position, None

    def is_upper(data: bytes, position: int) -> Tuple[int, Union[None, bytes]]:
        """
        This method checks a position for an ASCII upper case letter.

        >>> StandardMatch.is_upper(b"a1Bc", 0)
        (0, None)
        >>> StandardMatch.is_upper(b"a1Bc", 1)
        (1, None)
        >>> StandardMatch.is_upper(b"a1Bc", 2)
        (3, b'B')
        >>> len([x for x in range(256) if StandardMatch.is_upper(bytes((x,)), 0)[1] is not None])
        26
        >>>
        """

        if len(data) == position:
            return position, None

        char = data[position]
        if 65 <= char <= 90:
            return position + 1, bytes((char,))
        return position, None

    def is_digit(data: bytes, position: int) -> Tuple[int, Union[None, bytes]]:
        """
        This method checks a position for an ASCII digit character.

        >>> StandardMatch.is_digit(b"a1Bc", 0)
        (0, None)
        >>> StandardMatch.is_digit(b"a1Bc", 1)
        (2, b'1')
        >>> StandardMatch.is_digit(b"a1Bc", 2)
        (2, None)
        >>> len([x for x in range(256) if StandardMatch.is_digit(bytes((x,)), 0)[1] is not None])
        10
        >>>
        """

        if len(data) == position:
            return position, None

        char = data[position]
        if 48 <= char <= 57:
            return position + 1, bytes((char,))
        return position, None

    def is_hex(data: bytes, position: int) -> Tuple[int, Union[None, bytes]]:
        """
        This method checks a position for an ASCII hexadecimal character.

        >>> StandardMatch.is_hex(b"a1Bc", 0)
        (1, b'a')
        >>> StandardMatch.is_hex(b"a1Bc", 1)
        (2, b'1')
        >>> StandardMatch.is_hex(b"a1Bc", 2)
        (3, b'B')
        >>> StandardMatch.is_hex(b"a1Bg", 3)
        (3, None)
        >>> len([x for x in range(256) if StandardMatch.is_hex(bytes((x,)), 0)[1] is not None])
        22
        >>>
        """

        if len(data) == position:
            return position, None

        char = data[position]
        if 48 <= char <= 57 or 65 <= char <= 70 or 97 <= char <= 102:
            return position + 1, bytes((char,))
        return position, None

    def is_octal(data: bytes, position: int) -> Tuple[int, Union[None, bytes]]:
        """
        This method checks a position for an ASCII octal character.

        >>> StandardMatch.is_octal(b"01234567", 0)
        (1, b'0')
        >>> StandardMatch.is_octal(b"789", 0)
        (1, b'7')
        >>> StandardMatch.is_octal(b"a123", 0)
        (0, None)
        >>> StandardMatch.is_octal(b";+123", 0)
        (0, None)
        >>> len([x for x in range(256) if StandardMatch.is_octal(bytes((x,)), 0)[1] is not None])
        8
        >>>
        """

        if len(data) == position:
            return position, None

        char = data[position]
        if 48 <= char <= 55:
            return position + 1, bytes((char,))
        return position, None

    def is_printable(
        data: bytes, position: int
    ) -> Tuple[int, Union[None, bytes]]:
        r"""
        This method checks a position for an ASCII printable character.

        >>> StandardMatch.is_printable(b"a1Bc", 0)
        (1, b'a')
        >>> StandardMatch.is_printable(b"a1Bc", 1)
        (2, b'1')
        >>> StandardMatch.is_printable(b"a1Bc", 2)
        (3, b'B')
        >>> StandardMatch.is_printable(b"a1B\0", 3)
        (3, None)
        >>> from string import printable
        >>> len([x for x in range(256) if StandardMatch.is_printable(bytes((x,)), 0)[1] is not None]) == len(printable)
        True
        >>>
        """

        if len(data) == position:
            return position, None

        char = data[position]
        if 32 <= char <= 126 or 9 <= char <= 13:
            return position + 1, bytes((char,))
        return position, None

    def is_blank(data: bytes, position: int) -> Tuple[int, Union[None, bytes]]:
        """
        This method checks a position for an ASCII special character.

        >>> StandardMatch.is_blank(b" 1Bc", 0)
        (1, b' ')
        >>> StandardMatch.is_blank(b" 1Bc", 1)
        (1, None)
        >>> len([x for x in range(256) if StandardMatch.is_blank(bytes((x,)), 0)[1] is not None])
        6
        >>>
        """

        if len(data) == position:
            return position, None

        char = data[position]
        if 9 <= char <= 13 or char == 32:
            return position + 1, bytes((char,))
        return position, None

    def is_special(
        data: bytes, position: int
    ) -> Tuple[int, Union[None, bytes]]:
        """
        This method checks a position for an ASCII special character.

        >>> StandardMatch.is_special(b";1Bc", 0)
        (1, b';')
        >>> StandardMatch.is_special(b" 1Bc", 1)
        (1, None)
        >>> from string import printable
        >>> len([x for x in range(256) if StandardMatch.is_special(bytes((x,)), 0)[1] is not None]) == len(printable) - 26 * 2 - 10 - 6
        True
        >>>
        """

        if len(data) == position:
            return position, None

        char = data[position]
        if (
            33 <= char <= 47
            or 58 <= char <= 64
            or 91 <= char <= 96
            or 123 <= char <= 126
        ):
            return position + 1, bytes((char,))
        return position, None

    def check_char(char: int) -> Callable:
        """
        Generic method to generate a check for a specific character.
        """

        def check(
            data: bytes, position: int
        ) -> Tuple[int, Union[None, bytes]]:
            if len(data) == position:
                return position, None

            checked_char = data[position]
            if checked_char == char:
                return position + 1, bytes((char,))
            return position, None

        return check

    def or_check_chars(*chars: int) -> Callable:
        """
        Generic method to generate wrapper for `check_char` with `ordered_choice`.
        """

        def checks(
            data: bytes, position: int
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            return PegParser.ordered_choice(
                [StandardMatch.check_char(x) for x in chars],
                data,
                position,
            )

        return checks


class StandardRules:
    """
    This class implements standard rules.
    """

    class Types:
        """
        This sub-class implements standard types parsing rules.
        """

        def digits(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method checks multiples digits.

            >>> StandardRules.Types.digits(b"0123456789")
            (10, [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9'])
            >>> StandardRules.Types.digits(b"abc0123")
            (0, None)
            >>> StandardRules.Types.digits(b"0123abc")
            (4, [b'0', b'1', b'2', b'3'])
            >>> StandardRules.Types.digits(b"+123")
            (0, None)
            >>> StandardRules.Types.digits(b"0B2;")
            (1, [b'0'])
            >>> StandardRules.Types.digits(b"a ")
            (0, None)
            >>>
            """

            return PegParser.one_or_more(
                StandardMatch.is_digit,
                data,
                position,
            )

        def float(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method checks multiples digits.

            >>> StandardRules.Types.float(b"1.525")
            (5, [[b'1'], b'.', [b'5', b'2', b'5']])
            >>> StandardRules.Types.float(b"4521.5")
            (6, [[b'4', b'5', b'2', b'1'], b'.', [b'5']])
            >>> StandardRules.Types.float(b"0.2356")
            (6, [[b'0'], b'.', [b'2', b'3', b'5', b'6']])
            >>> StandardRules.Types.float(b"5624.0")
            (6, [[b'5', b'6', b'2', b'4'], b'.', [b'0']])
            >>> StandardRules.Types.float(b".0256")
            (0, None)
            >>> StandardRules.Types.float(b"0256.")
            (0, None)
            >>>
            """

            return PegParser.sequence(
                [
                    StandardRules.Types.digits,
                    StandardMatch.check_char(46),
                    StandardRules.Types.digits,
                ],
                data,
                position,
            )

        def bool(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method checks multiples digits.

            >>> StandardRules.Types.bool(b"true")
            (4, [b't', b'r', b'u', b'e'])
            >>> StandardRules.Types.bool(b"false")
            (5, [b'f', b'a', b'l', b's', b'e'])
            >>> StandardRules.Types.bool(b"True")
            (0, None)
            >>> StandardRules.Types.bool(b"False")
            (0, None)
            >>> StandardRules.Types.bool(b"test")
            (0, None)
            >>> StandardRules.Types.bool(b"tru")
            (0, None)
            >>>
            """

            return PegParser.ordered_choice(
                [
                    lambda d, p: PegParser.sequence(
                        [
                            StandardMatch.check_char(116),
                            StandardMatch.check_char(114),
                            StandardMatch.check_char(117),
                            StandardMatch.check_char(101),
                        ],
                        d,
                        p,
                    ),
                    lambda d, p: PegParser.sequence(
                        [
                            StandardMatch.check_char(102),
                            StandardMatch.check_char(97),
                            StandardMatch.check_char(108),
                            StandardMatch.check_char(115),
                            StandardMatch.check_char(101),
                        ],
                        d,
                        p,
                    ),
                ],
                data,
                position,
            )

        def hex_integer(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method checks hexadecimal integer.

            >>> StandardRules.Types.hex_integer(b"0x123")
            (5, [b'0', b'x', [b'1', b'2', b'3']])
            >>> StandardRules.Types.hex_integer(b"0Xa1c")
            (5, [b'0', b'X', [b'a', b'1', b'c']])
            >>> StandardRules.Types.hex_integer(b"0xg23")
            (0, None)
            >>> StandardRules.Types.hex_integer(b"0x1;")
            (3, [b'0', b'x', [b'1']])
            >>> StandardRules.Types.hex_integer(b"0x 1")
            (0, None)
            >>>
            """

            return PegParser.sequence(
                [
                    StandardMatch.check_char(48),
                    StandardMatch.or_check_chars(88, 120),
                    StandardRules.Format.hex,
                ],
                data,
                position,
            )

        def octal_integer(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method checks hexadecimal integer.

            >>> StandardRules.Types.octal_integer(b"0o123")
            (5, [b'0', b'o', [b'1', b'2', b'3']])
            >>> StandardRules.Types.octal_integer(b"0O123")
            (5, [b'0', b'O', [b'1', b'2', b'3']])
            >>> StandardRules.Types.octal_integer(b"0o891")
            (0, None)
            >>> StandardRules.Types.octal_integer(b"0O891")
            (0, None)
            >>> StandardRules.Types.octal_integer(b"0Oabc")
            (0, None)
            >>> StandardRules.Types.octal_integer(b"0Oabc")
            (0, None)
            >>> StandardRules.Types.octal_integer(b"123")
            (0, None)
            >>> StandardRules.Types.octal_integer(b"+0o123")
            (0, None)
            >>>
            """

            return PegParser.sequence(
                [
                    StandardMatch.check_char(48),
                    StandardMatch.or_check_chars(79, 111),
                    StandardRules.Format.octal,
                ],
                data,
                position,
            )

        def string(data: bytes, position: int = 0):
            """
            This method checks for string.

            >>> StandardRules.Types.string(b'"test"')
            (6, [b'"', [b't', b'e', b's', b't'], b'"'])
            >>> StandardRules.Types.string(b"'test2.,'")
            (9, [b"'", [b't', b'e', b's', b't', b'2', b'.', b','], b"'"])
            >>> StandardRules.Types.string(b"'\\\\x56\\\\t\\\\r\\\\7\\\\45\\\\111'")
            (0, None)
            >>> StandardRules.Types.string(b"test")
            (0, None)
            >>> StandardRules.Types.string(b"'\\\\98'")
            (0, None)
            >>> StandardRules.Types.string(b"'\\\\xgf'")
            (0, None)
            >>> StandardRules.Types.string(b"'\\\\N{NAME -TEST1}'")
            (17, [b"'", [[b'\\\\', b'N', b'{', [b'N', b'A', b'M', b'E', b' ', b'-', b'T', b'E', b'S', b'T', b'1'], b'}']], b"'"])
            >>> StandardRules.Types.string(b"'\\\\u0020'")
            (0, None)
            >>> StandardRules.Types.string(b"'\\\\U00000020'")
            (0, None)
            >>> StandardRules.Types.string(b'"test')
            (0, None)
            >>>
            """

            def wrapper_simple_character(x: int):
                def simple_character(data: bytes, position: int):
                    if len(data) == position:
                        return position, None

                    char = data[position]
                    if (
                        32 <= char <= 126 and char != 92 and char != x
                    ) or 9 <= char <= 10:
                        return position + 1, bytes((char,))
                    return position, None

                return simple_character

            def hex_special(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(92),
                        StandardMatch.or_check_chars(88, 120),
                        StandardMatch.is_hex,
                        StandardMatch.is_hex,
                    ],
                    data,
                    position,
                )

            def octal3_special(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.is_octal,
                        StandardMatch.is_octal,
                        StandardMatch.is_octal,
                    ],
                    data,
                    position,
                )

            def octal2_special(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.is_octal,
                        StandardMatch.is_octal,
                    ],
                    data,
                    position,
                )

            def octal_number_special(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        octal3_special,
                        octal2_special,
                        StandardMatch.is_octal,
                    ],
                    data,
                    position,
                )

            def octal_special(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(92),
                        StandardMatch.or_check_chars(79, 111),
                        octal_number_special,
                    ],
                    data,
                    position,
                )

            def unicode4(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(92),
                        StandardMatch.check_char(117),
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                    ],
                    data,
                    position,
                )

            def unicode8(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(92),
                        StandardMatch.check_char(85),
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                        StandardRules.Format.hex,
                    ],
                    data,
                    position,
                )

            def named_unicode(data: bytes, position: int):
                def name_char(data: bytes, position: int):
                    return PegParser.ordered_choice(
                        [
                            StandardMatch.is_letter,
                            StandardMatch.is_digit,
                            StandardMatch.or_check_chars(0x20, 0x2D),
                        ],
                        data,
                        position,
                    )

                def name_chars(data: bytes, position: int):
                    return PegParser.zero_or_more(name_char, data, position)

                return PegParser.sequence(
                    [
                        StandardMatch.check_char(92),
                        StandardMatch.check_char(78),
                        StandardMatch.check_char(123),
                        name_chars,
                        StandardMatch.check_char(125),
                    ],
                    data,
                    position,
                )

            def letter_special(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(92),
                        StandardMatch.or_check_chars(
                            34, 39, 92, 97, 98, 102, 110, 114, 116, 118
                        ),
                    ],
                    data,
                    position,
                )

            def special_character(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        hex_special,
                        octal_special,
                        unicode4,
                        unicode8,
                        named_unicode,
                        letter_special,
                    ],
                    data,
                    position,
                )

            def wrapper_character(x: int):
                def character(data: bytes, position: int):
                    return PegParser.ordered_choice(
                        [
                            wrapper_simple_character(x),
                            special_character,
                        ],
                        data,
                        position,
                    )

                return character

            def wrapper_characters(x: int):
                def characters(data: bytes, position: int):
                    return PegParser.zero_or_more(
                        wrapper_character(x),
                        data,
                        position,
                    )

                return characters

            def string_format1(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(34),
                        wrapper_characters(34),
                        StandardMatch.check_char(34),
                    ],
                    data,
                    position,
                )

            def string_format2(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(39),
                        wrapper_characters(39),
                        StandardMatch.check_char(39),
                    ],
                    data,
                    position,
                )

            return PegParser.ordered_choice(
                [
                    string_format1,
                    string_format2,
                ],
                data,
                position,
            )

    class Format:
        """
        This sub-class implements standard data formats parsing rules.
        """

        def integer(
            data: bytes, position: int = 0
        ) -> Tuple[
            int, Union[None, Iterable[Union[bool, bytes, Iterable[bytes]]]]
        ]:
            """
            This method checks signed integer.

            >>> StandardRules.Format.integer(b"+1")
            (2, [b'+', [b'1']])
            >>> StandardRules.Format.integer(b"-123")
            (4, [b'-', [b'1', b'2', b'3']])
            >>> StandardRules.Format.integer(b"123")
            (3, [True, [b'1', b'2', b'3']])
            >>> StandardRules.Format.integer(b"1a3")
            (1, [True, [b'1']])
            >>> StandardRules.Format.integer(b"+a")
            (0, None)
            >>> StandardRules.Format.integer(b"-abc")
            (0, None)
            >>>
            """

            def check_sign(data, position):
                return PegParser.ordered_choice(
                    [
                        StandardMatch.check_char(45),
                        StandardMatch.check_char(43),
                        lambda data, position: PegParser.and_predicate(
                            StandardMatch.is_digit, data, position
                        ),
                    ],
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    check_sign,
                    StandardRules.Types.digits,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "sign_integer"

            return result

        def word(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method checks for a word.

            >>> StandardRules.Format.word(b"abc")
            (3, [b'a', b'b', b'c'])
            >>> StandardRules.Format.word(b"abc;")
            (3, [b'a', b'b', b'c'])
            >>> StandardRules.Format.word(b"+123")
            (0, None)
            >>> StandardRules.Format.word(b"1abc")
            (0, None)
            >>> StandardRules.Format.word(b"a ")
            (1, [b'a'])
            >>>
            """

            result = PegParser.one_or_more(
                StandardMatch.is_letter,
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "word"

            return result

        def hex(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method checks for a word.

            >>> StandardRules.Format.hex(b"abcdef")
            (6, [b'a', b'b', b'c', b'd', b'e', b'f'])
            >>> StandardRules.Format.hex(b"abc0123")
            (7, [b'a', b'b', b'c', b'0', b'1', b'2', b'3'])
            >>> StandardRules.Format.hex(b"0123abc")
            (7, [b'0', b'1', b'2', b'3', b'a', b'b', b'c'])
            >>> StandardRules.Format.hex(b"+123")
            (0, None)
            >>> StandardRules.Format.hex(b"0B2;")
            (3, [b'0', b'B', b'2'])
            >>> StandardRules.Format.hex(b"a ")
            (1, [b'a'])
            >>>
            """

            result = PegParser.one_or_more(
                StandardMatch.is_hex,
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "hex"

            return result

        def octal(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method checks for a word.

            >>> StandardRules.Format.octal(b"01234567")
            (8, [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7'])
            >>> StandardRules.Format.octal(b"789")
            (1, [b'7'])
            >>> StandardRules.Format.octal(b"abc123")
            (0, None)
            >>> StandardRules.Format.octal(b"+123")
            (0, None)
            >>> StandardRules.Format.octal(b"0;B2;")
            (1, [b'0'])
            >>> StandardRules.Format.octal(b"a ")
            (0, None)
            >>>
            """

            result = PegParser.one_or_more(
                StandardMatch.is_octal,
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "octal"

            return result

        def base32(
            data: bytes, position: int = 0
        ) -> Tuple[
            int, Iterable[Union[bool, Iterable[Union[bytes, Iterable[bytes]]]]]
        ]:
            """
            This method checks for base32 format.

            >>> StandardRules.Format.base32(b"AB======")
            (8, [[], [b'A', b'B', b'=', b'=', b'=', b'=', b'=', b'=']])
            >>> StandardRules.Format.base32(b"ABC2====")
            (8, [[], [b'A', b'B', b'C', b'2', b'=', b'=', b'=', b'=']])
            >>> StandardRules.Format.base32(b"ABC23===")
            (8, [[], [b'A', b'B', b'C', b'2', b'3', b'=', b'=', b'=']])
            >>> StandardRules.Format.base32(b"ABC23ZT=")
            (8, [[], [b'A', b'B', b'C', b'2', b'3', b'Z', b'T', b'=']])
            >>> StandardRules.Format.base32(b"ABC23ZT7")
            (8, [[[b'A', b'B', b'C', b'2', b'3', b'Z', b'T', b'7']], True])
            >>> StandardRules.Format.base32(b"AB")
            (0, [[], True])
            >>> StandardRules.Format.base32(b"A1======")
            (0, [[], True])
            >>> StandardRules.Format.base32(b"A ======")
            (0, [[], True])
            >>> StandardRules.Format.base32(b"ABC23ZT7KF======")
            (16, [[[b'A', b'B', b'C', b'2', b'3', b'Z', b'T', b'7']], [b'K', b'F', b'=', b'=', b'=', b'=', b'=', b'=']])
            >>>
            """

            def base32_char(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        StandardMatch.is_upper,
                        StandardMatch.or_check_chars(50, 51, 52, 53, 54, 55),
                    ],
                    data,
                    position,
                )

            def base32_chars(data: bytes, position: int):
                return PegParser.sequence(
                    [base32_char] * 8,
                    data,
                    position,
                )

            def sequence(data: bytes, position: int):
                return PegParser.zero_or_more(
                    base32_chars,
                    data,
                    position,
                )

            def wrapper_padding(x: int):
                def end_padding(data: bytes, position: int):
                    return PegParser.sequence(
                        [base32_char] * (8 - x)
                        + [StandardMatch.check_char(61)] * x,
                        data,
                        position,
                    )

                return end_padding

            def end(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        wrapper_padding(1),
                        wrapper_padding(3),
                        wrapper_padding(4),
                        wrapper_padding(6),
                        lambda d, p: PegParser.not_predicate(
                            base32_chars, d, p
                        ),
                    ],
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    sequence,
                    end,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "base32"

            return result

        def base64(
            data: bytes, position: int = 0
        ) -> Tuple[
            int, Iterable[Union[bool, Iterable[Union[bytes, Iterable[bytes]]]]]
        ]:
            """
            This method checks for base64 format.

            >>> StandardRules.Format.base64(b'Y5==')
            (4, [[], [b'Y', b'5', b'=', b'=']])
            >>> StandardRules.Format.base64(b'Y5+=')
            (4, [[], [b'Y', b'5', b'+', b'=']])
            >>> StandardRules.Format.base64(b"Y5+/")
            (4, [[[b'Y', b'5', b'+', b'/']], True])
            >>> StandardRules.Format.base64(b"09AZaz+/")
            (8, [[[b'0', b'9', b'A', b'Z'], [b'a', b'z', b'+', b'/']], True])
            >>> StandardRules.Format.base64(b"++==")
            (4, [[], [b'+', b'+', b'=', b'=']])
            >>> StandardRules.Format.base64(b"///=")
            (4, [[], [b'/', b'/', b'/', b'=']])
            >>> StandardRules.Format.base64(b"a=")
            (0, [[], True])
            >>> StandardRules.Format.base64(b"a ==")
            (0, [[], True])
            >>>
            """

            def base64_char(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        StandardMatch.is_letter,
                        StandardMatch.is_digit,
                        StandardMatch.or_check_chars(43, 47),
                    ],
                    data,
                    position,
                )

            def base64_chars(data: bytes, position: int):
                return PegParser.sequence(
                    [base64_char] * 4,
                    data,
                    position,
                )

            def sequence(data: bytes, position: int):
                return PegParser.zero_or_more(
                    base64_chars,
                    data,
                    position,
                )

            def wrapper_padding(x: int):
                def end_padding(data: bytes, position: int):
                    return PegParser.sequence(
                        [base64_char] * (4 - x)
                        + [StandardMatch.check_char(61)] * x,
                        data,
                        position,
                    )

                return end_padding

            def end(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        wrapper_padding(1),
                        wrapper_padding(2),
                        lambda d, p: PegParser.not_predicate(
                            base64_chars, d, p
                        ),
                    ],
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    sequence,
                    end,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "base64"

            return result

        def base85(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[Iterable[bytes]]]]:
            """
            This method checks for base85 format.

            >>> StandardRules.Format.base85(b'VPRomVE')
            (5, [[b'V', b'P', b'R', b'o', b'm']])
            >>> StandardRules.Format.base85(b'VPRomVPO')
            (5, [[b'V', b'P', b'R', b'o', b'm']])
            >>> StandardRules.Format.base85(b"VPRomVPRn")
            (5, [[b'V', b'P', b'R', b'o', b'm']])
            >>> StandardRules.Format.base85(b"VPRomVPRom")
            (10, [[b'V', b'P', b'R', b'o', b'm'], [b'V', b'P', b'R', b'o', b'm']])
            >>> StandardRules.Format.base85(b"VPRomVPRom``+|}{;<=>")
            (20, [[b'V', b'P', b'R', b'o', b'm'], [b'V', b'P', b'R', b'o', b'm'], [b'`', b'`', b'+', b'|', b'}'], [b'{', b';', b'<', b'=', b'>']])
            >>> StandardRules.Format.base85(b"VPRo mVPRom``+|}{;<=>")
            (0, None)
            >>>
            """

            def base85_char(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        StandardMatch.is_letter,
                        StandardMatch.is_digit,
                        StandardMatch.or_check_chars(
                            33,
                            35,
                            36,
                            37,
                            38,
                            40,
                            41,
                            42,
                            43,
                            45,
                            59,
                            60,
                            61,
                            62,
                            63,
                            64,
                            94,
                            95,
                            96,
                            123,
                            124,
                            125,
                            126,
                        ),
                    ],
                    data,
                    position,
                )

            def base85_chars(data: bytes, position: int):
                return PegParser.sequence(
                    [base85_char] * 5,
                    data,
                    position,
                )

            result = PegParser.one_or_more(
                base85_chars,
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "base85"

            return result

    class Url:
        """
        This class implements methods to parse an URL.
        """

        def _characters(data, position):
            def check_url_encoding(data, position):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(37),
                        StandardMatch.is_hex,
                        StandardMatch.is_hex,
                    ],
                    data,
                    position,
                )

            def check_url_char(data, position):
                return PegParser.ordered_choice(
                    [
                        StandardMatch.is_letter,
                        StandardMatch.is_digit,
                        StandardMatch.check_char(126),
                        StandardMatch.check_char(95),
                        StandardMatch.check_char(45),
                        StandardMatch.check_char(46),
                        StandardMatch.check_char(43),
                        check_url_encoding,
                    ],
                    data,
                    position,
                )

            return PegParser.zero_or_more(
                check_url_char,
                data,
                position,
            )

        def _characters_subdelims_colon(data, position):
            return PegParser.ordered_choice(
                [
                    StandardMatch.or_check_chars(
                        33, 36, 38, 39, 40, 41, 42, 43, 44, 58, 59, 61
                    ),
                    StandardRules.Url._characters,
                ],
                data,
                position,
            )

        def _character_subdelims_colon_commat(data, position):
            return PegParser.ordered_choice(
                [
                    StandardMatch.or_check_chars(
                        33, 36, 38, 39, 40, 41, 42, 43, 44, 58, 61, 64
                    ),
                    StandardRules.Url._characters,
                ],
                data,
                position,
            )

        def _character_subdelims_colon_commat_slot_quest(data, position):
            return PegParser.ordered_choice(
                [
                    StandardMatch.or_check_chars(
                        33,
                        36,
                        38,
                        39,
                        40,
                        41,
                        42,
                        43,
                        44,
                        58,
                        59,
                        61,
                        64,
                        47,
                        63,
                    ),
                    StandardRules.Url._characters,
                ],
                data,
                position,
            )

        def _characters_subdelims_colon_commat(data, position):
            return PegParser.one_or_more(
                StandardRules.Url._character_subdelims_colon_commat,
                data,
                position,
            )

        def _optional_characters_subdelims_colon_commat(data, position):
            return PegParser.zero_or_more(
                StandardRules.Url._character_subdelims_colon_commat,
                data,
                position,
            )

        def _optional_characters_subdelims_colon_commat_slot_quest(
            data, position
        ):
            return PegParser.zero_or_more(
                StandardRules.Url._character_subdelims_colon_commat_slot_quest,
                data,
                position,
            )

        def _base_path(data: int, position: int):
            return PegParser.sequence(
                [
                    StandardMatch.check_char(47),
                    StandardRules.Url._optional_characters_subdelims_colon_commat,
                ],
                data,
                position,
            )

        def path_rootless(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                None,
                Iterable[
                    Iterable[Iterable[Union[bytes, Iterable[Iterable[bytes]]]]]
                ],
            ],
        ]:
            """
            This method checks path root-less.

            >>> StandardRules.Url.path_rootless(b"abc/def.")
            (8, [[[b'a', b'b', b'c']], [[b'/', [[b'd', b'e', b'f', b'.']]]]])
            >>> StandardRules.Url.path_rootless(b"abc?/def")
            (3, [[[b'a', b'b', b'c']], []])
            >>> StandardRules.Url.path_rootless(b"a-bc#/def")
            (4, [[[b'a', b'-', b'b', b'c']], []])
            >>> StandardRules.Url.path_rootless(b"a_bc%25/def")
            (11, [[[b'a', b'_', b'b', b'c', [b'%', b'2', b'5']]], [[b'/', [[b'd', b'e', b'f']]]]])
            >>>
            """

            result = PegParser.sequence(
                [
                    StandardRules.Url._characters_subdelims_colon_commat,
                    lambda d, p: PegParser.zero_or_more(
                        StandardRules.Url._base_path, d, p
                    ),
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "path"

            return result

        def path(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                None,
                Iterable[
                    Iterable[
                        Union[
                            bytes,
                            Iterable[
                                Union[
                                    bytes,
                                    Iterable[Union[bytes, Iterable[bytes]]],
                                ]
                            ],
                        ]
                    ]
                ],
            ],
        ]:
            """
            This method checks URL path.

            >>> StandardRules.Url.path(b"/abc/def.")
            (9, [[b'/', [[b'a', b'b', b'c']]], [b'/', [[b'd', b'e', b'f', b'.']]]])
            >>> StandardRules.Url.path(b"/abc?/def")
            (4, [[b'/', [[b'a', b'b', b'c']]]])
            >>> StandardRules.Url.path(b"/a-bc#/def")
            (5, [[b'/', [[b'a', b'-', b'b', b'c']]]])
            >>> StandardRules.Url.path(b"/a_bc%25/def")
            (12, [[b'/', [[b'a', b'_', b'b', b'c', [b'%', b'2', b'5']]]], [b'/', [[b'd', b'e', b'f']]]])
            >>> StandardRules.Url.path(b"/a~bc%2F/def")
            (12, [[b'/', [[b'a', b'~', b'b', b'c', [b'%', b'2', b'F']]]], [b'/', [[b'd', b'e', b'f']]]])
            >>> StandardRules.Url.path(b"//def")
            (5, [[b'/', []], [b'/', [[b'd', b'e', b'f']]]])
            >>> StandardRules.Url.path(b"/abc%2/def")
            (4, [[b'/', [[b'a', b'b', b'c']]]])
            >>> StandardRules.Url.path(b"/abc%/def")
            (4, [[b'/', [[b'a', b'b', b'c']]]])
            >>> StandardRules.Url.path(b"/")
            (1, [[b'/', []]])
            >>> StandardRules.Url.path(b"/c=test")
            (7, [[b'/', [[b'c'], b'=', [b't', b'e', b's', b't']]]])
            >>> StandardRules.Url.path(b"")
            (0, None)
            >>>
            """

            result = PegParser.one_or_more(
                StandardRules.Url._base_path,
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "path"

            return result

        def form_data(data: bytes, position: int = 0) -> Tuple[
            int,
            Iterable[
                Iterable[Union[bytes, Iterable[Union[bytes, Iterable[bytes]]]]]
            ],
        ]:
            """
            This method checks the form data format used in POST body and GET query.

            >>> StandardRules.Url.form_data(b"abc=def&def=abc")
            (15, [[[b'a', b'b', b'c'], b'=', [b'd', b'e', b'f']], [[b'&', [[b'd', b'e', b'f'], b'=', [b'a', b'b', b'c']]]]])
            >>> StandardRules.Url.form_data(b"abc")
            (3, [[b'a', b'b', b'c'], []])
            >>> StandardRules.Url.form_data(b"abc&def")
            (7, [[b'a', b'b', b'c'], [[b'&', [b'd', b'e', b'f']]]])
            >>> StandardRules.Url.form_data(b"&def=abc")
            (8, [[], [[b'&', [[b'd', b'e', b'f'], b'=', [b'a', b'b', b'c']]]]])
            >>> StandardRules.Url.form_data(b"&def?=abc")
            (4, [[], [[b'&', [b'd', b'e', b'f']]]])
            >>> StandardRules.Url.form_data(b"&def;")
            (4, [[], [[b'&', [b'd', b'e', b'f']]]])
            >>> StandardRules.Url.form_data(b"/abc%/def")
            (0, [[], []])
            >>> StandardRules.Url.form_data(b"+")
            (1, [[b'+'], []])
            >>>
            """

            def named_value(data, position):
                return PegParser.sequence(
                    [
                        StandardRules.Url._characters,
                        StandardMatch.check_char(61),
                        StandardRules.Url._characters,
                    ],
                    data,
                    position,
                )

            def value_or_named_value(data, position):
                return PegParser.ordered_choice(
                    [
                        named_value,
                        StandardRules.Url._characters,
                    ],
                    data,
                    position,
                )

            def separator_and_value(data, position):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(38),
                        value_or_named_value,
                    ],
                    data,
                    position,
                )

            def separators_and_values(data, position):
                return PegParser.zero_or_more(
                    separator_and_value,
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    value_or_named_value,
                    separators_and_values,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "form_data"

            return result

        def query(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                bool,
                Iterable[
                    Union[
                        bytes,
                        Iterable[
                            Union[
                                bytes, Iterable[Union[bytes, Iterable[bytes]]]
                            ]
                        ],
                    ]
                ],
            ],
        ]:
            """
            This method checks URL query.

            >>> StandardRules.Url.query(b"?abc=def&def=abc")
            (16, [b'?', [[b'a', b'b', b'c'], b'=', [b'd', b'e', b'f'], b'&', [b'd', b'e', b'f'], b'=', [b'a', b'b', b'c']]])
            >>> StandardRules.Url.query(b"?abc%25")
            (7, [b'?', [[b'a', b'b', b'c', [b'%', b'2', b'5']]]])
            >>> StandardRules.Url.query(b"?abc&def")
            (8, [b'?', [[b'a', b'b', b'c'], b'&', [b'd', b'e', b'f']]])
            >>> StandardRules.Url.query(b"?")
            (1, [b'?', []])
            >>> StandardRules.Url.query(b"?&def=abc")
            (9, [b'?', [b'&', [b'd', b'e', b'f'], b'=', [b'a', b'b', b'c']]])
            >>> StandardRules.Url.query(b"?&def?=abc")
            (10, [b'?', [b'&', [b'd', b'e', b'f'], b'?', b'=', [b'a', b'b', b'c']]])
            >>> StandardRules.Url.query(b"&def;")
            (0, True)
            >>> StandardRules.Url.query(b"/abc%/def")
            (0, True)
            >>> StandardRules.Url.query(b"+")
            (0, True)
            >>>
            """

            def check_query(data, position):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(63),
                        StandardRules.Url._optional_characters_subdelims_colon_commat_slot_quest,
                    ],
                    data,
                    position,
                )

            result = PegParser.ordered_choice(
                [
                    check_query,
                    lambda d, p: PegParser.not_predicate(
                        StandardMatch.check_char(63), d, p
                    ),
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "query"

            return result

        def parameters(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                bool,
                Iterable[
                    Union[
                        bytes,
                        Iterable[
                            Iterable[
                                Union[
                                    bytes,
                                    Iterable[
                                        Union[
                                            bytes,
                                            Iterable[
                                                Union[bytes, Iterable[bytes]]
                                            ],
                                        ]
                                    ],
                                ]
                            ]
                        ],
                    ]
                ],
            ],
        ]:
            """
            This method checks URL parameters.

            >>> StandardRules.Url.parameters(b";abc=def&def=abc")
            (16, [b';', [[[b'a', b'b', b'c'], b'=', [b'd', b'e', b'f']], [[b'&', [[b'd', b'e', b'f'], b'=', [b'a', b'b', b'c']]]]]])
            >>> StandardRules.Url.parameters(b";abc")
            (4, [b';', [[b'a', b'b', b'c'], []]])
            >>> StandardRules.Url.parameters(b";abc&def")
            (8, [b';', [[b'a', b'b', b'c'], [[b'&', [b'd', b'e', b'f']]]]])
            >>> StandardRules.Url.parameters(b";")
            (1, [b';', [[], []]])
            >>> StandardRules.Url.parameters(b";&def=abc")
            (9, [b';', [[], [[b'&', [[b'd', b'e', b'f'], b'=', [b'a', b'b', b'c']]]]]])
            >>> StandardRules.Url.parameters(b";&def;=abc")
            (5, [b';', [[], [[b'&', [b'd', b'e', b'f']]]]])
            >>> StandardRules.Url.parameters(b"&def;")
            (0, True)
            >>> StandardRules.Url.parameters(b"/abc%/def")
            (0, True)
            >>> StandardRules.Url.parameters(b"+")
            (0, True)
            >>>
            """

            def check_parameters(data, position):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(59),
                        StandardRules.Url.form_data,
                    ],
                    data,
                    position,
                )

            result = PegParser.ordered_choice(
                [
                    check_parameters,
                    lambda d, p: PegParser.not_predicate(
                        StandardMatch.check_char(59), d, p
                    ),
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "parameters"

            return result

        def fragment(
            data: bytes, position: int = 0
        ) -> Tuple[
            int, Union[bool, Iterable[Union[bytes, Iterable[Iterable[bytes]]]]]
        ]:
            """
            This method checks URL fragment.

            >>> StandardRules.Url.fragment(b"#AZaz09-_.~+")
            (12, [b'#', [[b'A', b'Z', b'a', b'z', b'0', b'9', b'-', b'_', b'.', b'~', b'+']]])
            >>> StandardRules.Url.fragment(b"AZaz09-_.~")
            (0, True)
            >>> StandardRules.Url.fragment(b"!$&'()*,;=:@/?")
            (0, True)
            >>> StandardRules.Url.fragment(b"#")
            (1, [b'#', []])
            >>>
            """

            def check_fragment(data, position):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(35),
                        StandardRules.Url._optional_characters_subdelims_colon_commat_slot_quest,
                    ],
                    data,
                    position,
                )

            result = PegParser.ordered_choice(
                [
                    check_fragment,
                    lambda d, p: PegParser.not_predicate(
                        StandardMatch.check_char(35), d, p
                    ),
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "fragment"

            return result

        def full(data: bytes, position: int = 0):
            """
            This method parses the full URL.

            >>> StandardRules.Url.full(b"https://my.full.url/with/path;and=parameters?query=too#fragment")
            (63, [[b'h', [b't', b't', b'p', b's']], b':', [b'/', b'/', [[b'm', [b'y']], [[b'.', [b'f', [b'u', b'l', b'l']]], [b'.', [b'u', [b'r', b'l']]]]], [[b'/', [[b'w', b'i', b't', b'h']]], [b'/', [[b'p', b'a', b't', b'h']]]]], [b';', [[[b'a', b'n', b'd'], b'=', [b'p', b'a', b'r', b'a', b'm', b'e', b't', b'e', b'r', b's']], []]], [b'?', [[b'q', b'u', b'e', b'r', b'y'], b'=', [b't', b'o', b'o']]], [b'#', [[b'f', b'r', b'a', b'g', b'm', b'e', b'n', b't']]]])
            >>> StandardRules.Url.full(b"http://www.ics.uci.edu/pub/ietf/uri/#Related")
            (44, [[b'h', [b't', b't', b'p']], b':', [b'/', b'/', [[b'w', [b'w', b'w']], [[b'.', [b'i', [b'c', b's']]], [b'.', [b'u', [b'c', b'i']]], [b'.', [b'e', [b'd', b'u']]]]], [[b'/', [[b'p', b'u', b'b']]], [b'/', [[b'i', b'e', b't', b'f']]], [b'/', [[b'u', b'r', b'i']]], [b'/', []]]], True, True, [b'#', [[b'R', b'e', b'l', b'a', b't', b'e', b'd']]]])
            >>> StandardRules.Url.full(b"ftp://ftp.is.co.za/rfc/rfc1808.txt")
            (34, [[b'f', [b't', b'p']], b':', [b'/', b'/', [[b'f', [b't', b'p']], [[b'.', [b'i', [b's']]], [b'.', [b'c', [b'o']]], [b'.', [b'z', [b'a']]]]], [[b'/', [[b'r', b'f', b'c']]], [b'/', [[b'r', b'f', b'c', b'1', b'8', b'0', b'8', b'.', b't', b'x', b't']]]]], True, True, True])
            >>> StandardRules.Url.full(b"http://www.ietf.org/rfc/rfc2396.txt")
            (35, [[b'h', [b't', b't', b'p']], b':', [b'/', b'/', [[b'w', [b'w', b'w']], [[b'.', [b'i', [b'e', b't', b'f']]], [b'.', [b'o', [b'r', b'g']]]]], [[b'/', [[b'r', b'f', b'c']]], [b'/', [[b'r', b'f', b'c', b'2', b'3', b'9', b'6', b'.', b't', b'x', b't']]]]], True, True, True])
            >>> StandardRules.Url.full(b"ldap://[2001:db8::7]/c=GB?objectClass?one")
            (41, [[b'l', [b'd', b'a', b'p']], b':', [b'/', b'/', [b'[', [[[b'2', b'0', b'0', b'1'], b':'], [b'd', b'b', b'8'], b':', b':', b'7'], b']'], [[b'/', [[b'c'], b'=', [b'G', b'B']]]]], True, [b'?', [[b'o', b'b', b'j', b'e', b'c', b't', b'C', b'l', b'a', b's', b's'], b'?', [b'o', b'n', b'e']]], True])
            >>> StandardRules.Url.full(b"mailto:John.Doe@example.com")
            (27, [[b'm', [b'a', b'i', b'l', b't', b'o']], b':', [[[b'J', b'o', b'h', b'n', b'.', b'D', b'o', b'e'], b'@', [b'e', b'x', b'a', b'm', b'p', b'l', b'e', b'.', b'c', b'o', b'm']], []], True, True, True])
            >>> StandardRules.Url.full(b"news:comp.infosystems.www.servers.unix")
            (38, [[b'n', [b'e', b'w', b's']], b':', [[[b'c', b'o', b'm', b'p', b'.', b'i', b'n', b'f', b'o', b's', b'y', b's', b't', b'e', b'm', b's', b'.', b'w', b'w', b'w', b'.', b's', b'e', b'r', b'v', b'e', b'r', b's', b'.', b'u', b'n', b'i', b'x']], []], True, True, True])
            >>> StandardRules.Url.full(b"tel:+1-816-555-1212")
            (19, [[b't', [b'e', b'l']], b':', [[b'+', [b'1', b'-', b'8', b'1', b'6', b'-', b'5', b'5', b'5', b'-', b'1', b'2', b'1', b'2']], []], True, True, True])
            >>> StandardRules.Url.full(b"telnet://192.0.2.16:80/")
            (23, [[b't', [b'e', b'l', b'n', b'e', b't']], b':', [b'/', b'/', [[[b'1', [b'9', b'2']], [[b'.', [b'0', []]], [b'.', [b'2', []]], [b'.', [b'1', [b'6']]]]], b':', [b'8', b'0']], [[b'/', []]]], True, True, True])
            >>> StandardRules.Url.full(b"urn:oasis:names:specification:docbook:dtd:xml:4.1.2")
            (51, [[b'u', [b'r', b'n']], b':', [[[b'o', b'a', b's', b'i', b's'], b':', [b'n', b'a', b'm', b'e', b's'], b':', [b's', b'p', b'e', b'c', b'i', b'f', b'i', b'c', b'a', b't', b'i', b'o', b'n'], b':', [b'd', b'o', b'c', b'b', b'o', b'o', b'k'], b':', [b'd', b't', b'd'], b':', [b'x', b'm', b'l'], b':', [b'4', b'.', b'1', b'.', b'2']], []], True, True, True])
            >>>
            """

            def autority(data, position):
                return PegParser.ordered_choice(
                    [
                        lambda d, p: PegParser.sequence(
                            [
                                StandardRules.Network.user_info,
                                StandardMatch.check_char(64),
                                StandardRules.Network.host_port,
                            ],
                            d,
                            p,
                        ),
                        lambda d, p: PegParser.sequence(
                            [
                                StandardRules.Network.user_info,
                                StandardMatch.check_char(64),
                                StandardRules.Network.host,
                            ],
                            d,
                            p,
                        ),
                        StandardRules.Network.host_port,
                        StandardRules.Network.host,
                    ],
                    data,
                    position,
                )

            def autority_path(data, position):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(47),
                        StandardMatch.check_char(47),
                        autority,
                        StandardRules.Url.path,
                    ],
                    data,
                    position,
                )

            def hier_part(data, position):
                return PegParser.ordered_choice(
                    [
                        autority_path,
                        StandardRules.Url.path,
                        StandardRules.Url.path_rootless,
                        lambda d, p: PegParser.not_predicate(47, d, p),
                    ],
                    data,
                    position,
                )

            def _full_choice(*methods):
                def choice(data, position):
                    return PegParser.sequence(
                        [
                            StandardRules.Url.scheme,
                            StandardMatch.check_char(58),
                            hier_part,
                            *methods,
                        ],
                        data,
                        position,
                    )

                return choice

            result = PegParser.ordered_choice(
                [
                    _full_choice(
                        StandardRules.Url.parameters,
                        StandardRules.Url.query,
                        StandardRules.Url.fragment,
                    ),
                    _full_choice(
                        StandardRules.Url.parameters, StandardRules.Url.query
                    ),
                    _full_choice(
                        StandardRules.Url.parameters,
                        StandardRules.Url.fragment,
                    ),
                    _full_choice(StandardRules.Url.parameters),
                    _full_choice(
                        StandardRules.Url.query, StandardRules.Url.fragment
                    ),
                    _full_choice(StandardRules.Url.query),
                    _full_choice(StandardRules.Url.fragment),
                    _full_choice(),
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "url"

            return result

        def scheme(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[Union[bytes, Iterable[bytes]]]]]:
            """
            This method checks URL scheme.

            >>> StandardRules.Url.scheme(b"http")
            (4, [b'h', [b't', b't', b'p']])
            >>> StandardRules.Url.scheme(b"git+ssh")
            (7, [b'g', [b'i', b't', b'+', b's', b's', b'h']])
            >>> StandardRules.Url.scheme(b"gopher")
            (6, [b'g', [b'o', b'p', b'h', b'e', b'r']])
            >>> StandardRules.Url.scheme(b"itms-services")
            (13, [b'i', [b't', b'm', b's', b'-', b's', b'e', b'r', b'v', b'i', b'c', b'e', b's']])
            >>> StandardRules.Url.scheme(b"TEST.0tEst9")
            (11, [b'T', [b'E', b'S', b'T', b'.', b'0', b't', b'E', b's', b't', b'9']])
            >>> StandardRules.Url.scheme(b"TEST,0tEst9")
            (4, [b'T', [b'E', b'S', b'T']])
            >>>
            """

            def character(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        StandardMatch.is_letter,
                        StandardMatch.is_digit,
                        StandardMatch.or_check_chars(43, 45, 46),
                    ],
                    data,
                    position,
                )

            def characters(data: bytes, position: int):
                return PegParser.zero_or_more(
                    character,
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    StandardMatch.is_letter,
                    characters,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "scheme"

            return result

    class Network:
        """
        This class implements methods to parse Network formats and data.
        """

        def hostname(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                None,
                Iterable[
                    Union[
                        bytes,
                        Iterable[
                            Union[
                                bytes, Iterable[Union[bytes, Iterable[bytes]]]
                            ]
                        ],
                    ]
                ],
            ],
        ]:
            """
            This method parses hostnames value.

            >>> StandardRules.Network.hostname(b"test")
            (4, [b't', [b'e', b's', b't']])
            >>> StandardRules.Network.hostname(b"test-abc")
            (8, [b't', [b'e', b's', b't', [[b'-'], b'a'], b'b', b'c']])
            >>> StandardRules.Network.hostname(b"a")
            (1, [b'a', []])
            >>> StandardRules.Network.hostname(b"test-ABC456")
            (11, [b't', [b'e', b's', b't', [[b'-'], b'A'], b'B', b'C', b'4', b'5', b'6']])
            >>> StandardRules.Network.hostname(b"6test")
            (5, [b'6', [b't', b'e', b's', b't']])
            >>> StandardRules.Network.hostname(b"6test-")
            (5, [b'6', [b't', b'e', b's', b't']])
            >>> StandardRules.Network.hostname(b"-6test")
            (0, None)
            >>>
            """

            def first_last(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        StandardMatch.is_letter,
                        StandardMatch.is_digit,
                    ],
                    data,
                    position,
                )

            def minus(data: bytes, position: int):
                return PegParser.one_or_more(
                    StandardMatch.check_char(45),
                    data,
                    position,
                )

            def minus_match(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        minus,
                        first_last,
                    ],
                    data,
                    position,
                )

            def character(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        first_last,
                        minus_match,
                    ],
                    data,
                    position,
                )

            def characters(data: bytes, position: int):
                return PegParser.zero_or_more(
                    character,
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    first_last,
                    characters,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "hostname"

            return result

        def fqdn(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                None,
                Iterable[
                    Iterable[
                        Union[
                            bytes,
                            Iterable[
                                Union[
                                    bytes,
                                    Iterable[
                                        Union[
                                            bytes,
                                            Iterable[
                                                Union[
                                                    bytes,
                                                    Iterable[
                                                        Union[
                                                            bytes,
                                                            Iterable[bytes],
                                                        ]
                                                    ],
                                                ]
                                            ],
                                        ]
                                    ],
                                ]
                            ],
                        ]
                    ]
                ],
            ],
        ]:
            """
            This method parses the FQDN format.

            >>> StandardRules.Network.fqdn(b"test012.abc.com")
            (15, [[b't', [b'e', b's', b't', b'0', b'1', b'2']], [[b'.', [b'a', [b'b', b'c']]], [b'.', [b'c', [b'o', b'm']]]]])
            >>> StandardRules.Network.fqdn(b"test012.abc-def.com")
            (19, [[b't', [b'e', b's', b't', b'0', b'1', b'2']], [[b'.', [b'a', [b'b', b'c', [[b'-'], b'd'], b'e', b'f']]], [b'.', [b'c', [b'o', b'm']]]]])
            >>> StandardRules.Network.fqdn(b".test012.abc-def.com")
            (0, None)
            >>> StandardRules.Network.fqdn(b"test012.abc-def.com.")
            (19, [[b't', [b'e', b's', b't', b'0', b'1', b'2']], [[b'.', [b'a', [b'b', b'c', [[b'-'], b'd'], b'e', b'f']]], [b'.', [b'c', [b'o', b'm']]]]])
            >>> StandardRules.Network.fqdn(b"-test012.abc-def.com")
            (0, None)
            >>> StandardRules.Network.fqdn(b"test012.abc-def.com-")
            (19, [[b't', [b'e', b's', b't', b'0', b'1', b'2']], [[b'.', [b'a', [b'b', b'c', [[b'-'], b'd'], b'e', b'f']]], [b'.', [b'c', [b'o', b'm']]]]])
            >>> StandardRules.Network.fqdn(b"012test.abc-def.com-")
            (19, [[b'0', [b'1', b'2', b't', b'e', b's', b't']], [[b'.', [b'a', [b'b', b'c', [[b'-'], b'd'], b'e', b'f']]], [b'.', [b'c', [b'o', b'm']]]]])
            >>>
            """

            def dot_hostname(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(46),
                        StandardRules.Network.hostname,
                    ],
                    data,
                    position,
                )

            def dot_hostnames(data: bytes, position: int):
                return PegParser.one_or_more(
                    dot_hostname,
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    StandardRules.Network.hostname,
                    dot_hostnames,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "fqdn"

            return result

        def ipv6(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                None,
                Iterable[
                    Union[bytes, Iterable[Union[bytes, Iterable[bytes]]]]
                ],
            ],
        ]:
            """
            This method parses IPv6 formats.

            >>> StandardRules.Network.ipv6(b":1:")
            (0, None)
            >>> StandardRules.Network.ipv6(b"2:1:3")
            (0, None)
            >>> StandardRules.Network.ipv6(b"5:4:2:1:3")
            (0, None)
            >>> StandardRules.Network.ipv6(b"::")
            (2, [b':', b':'])
            >>> StandardRules.Network.ipv6(b"::1")
            (3, [b':', b':', b'1'])
            >>> StandardRules.Network.ipv6(b"::1:2")
            (5, [b':', b':', [b'1', b':'], b'2'])
            >>> StandardRules.Network.ipv6(b"::1:2:3")
            (7, [b':', b':', [b'1', b':'], [b'2', b':'], b'3'])
            >>> StandardRules.Network.ipv6(b"1::2:3:4:5")
            (10, [b'1', b':', b':', [b'2', b':'], [b'3', b':'], [b'4', b':'], b'5'])
            >>> StandardRules.Network.ipv6(b"1:2::3:4:5")
            (10, [[b'1', b':'], b'2', b':', b':', [b'3', b':'], [b'4', b':'], b'5'])
            >>> StandardRules.Network.ipv6(b"1:2:3::4:5")
            (10, [[b'1', b':'], [b'2', b':'], b'3', b':', b':', [b'4', b':'], b'5'])
            >>> StandardRules.Network.ipv6(b"1:2:3:4::5")
            (10, [[b'1', b':'], [b'2', b':'], [b'3', b':'], b'4', b':', b':', b'5'])
            >>> StandardRules.Network.ipv6(b"1:2:3:4:5::")
            (11, [[b'1', b':'], [b'2', b':'], [b'3', b':'], [b'4', b':'], b'5', b':', b':'])
            >>> StandardRules.Network.ipv6(b"f09f:9af9:a09a::0af0:0b2c")
            (25, [[[b'f', b'0', b'9', b'f'], b':'], [[b'9', b'a', b'f', b'9'], b':'], [b'a', b'0', b'9', b'a'], b':', b':', [[b'0', b'a', b'f', b'0'], b':'], [b'0', b'b', b'2', b'c']])
            >>> StandardRules.Network.ipv6(b"0090:9009:0090::0000:0000")
            (25, [[[b'0', b'0', b'9', b'0'], b':'], [[b'9', b'0', b'0', b'9'], b':'], [b'0', b'0', b'9', b'0'], b':', b':', [[b'0', b'0', b'0', b'0'], b':'], [b'0', b'0', b'0', b'0']])
            >>> StandardRules.Network.ipv6(b"0:9:0::0:0")
            (10, [[b'0', b':'], [b'9', b':'], b'0', b':', b':', [b'0', b':'], b'0'])
            >>> StandardRules.Network.ipv6(b"2001:0db8:0000:0000:0000:ff00:0042:8329")
            (39, [[[b'2', b'0', b'0', b'1'], b':'], [[b'0', b'd', b'b', b'8'], b':'], [[b'0', b'0', b'0', b'0'], b':'], [[b'0', b'0', b'0', b'0'], b':'], [[b'0', b'0', b'0', b'0'], b':'], [[b'f', b'f', b'0', b'0'], b':'], [[b'0', b'0', b'4', b'2'], b':'], [b'8', b'3', b'2', b'9']])
            >>>
            """

            def hex_generator(x: int):
                def hex(data: bytes, position: int):
                    return PegParser.sequence(
                        [StandardMatch.is_hex] * x,
                        data,
                        position,
                    )

                return hex

            def hex_group(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        hex_generator(4),
                        hex_generator(3),
                        hex_generator(2),
                        StandardMatch.is_hex,
                    ],
                    data,
                    position,
                )

            def hex_dots(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        hex_group,
                        StandardMatch.check_char(58),
                    ],
                    data,
                    position,
                )

            def groups_generator(x: int, y: int):
                def groups(data: bytes, position: int):
                    return PegParser.sequence(
                        (([hex_dots] * (x - 1) + [hex_group]) if x else [])
                        + (
                            []
                            if x == 8
                            else [
                                StandardMatch.check_char(58),
                                StandardMatch.check_char(58),
                            ]
                        )
                        + (([hex_dots] * (y - 1) + [hex_group]) if y else []),
                        data,
                        position,
                    )

                return groups

            def generate_groups():
                groups = [groups_generator(8, 0)]
                for a in range(7, -1, -1):
                    b = 7 - a
                    while b >= 0:
                        groups.append(groups_generator(a, b))
                        # groups.append(groups_generator(b, a))
                        b -= 1
                return groups

            result = PegParser.ordered_choice(
                generate_groups(),
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "ipv6"

            return result

        def ipv6_zoneid(data: bytes, position: int = 0) -> Tuple[
            int,
            Iterable[
                Union[
                    bytes,
                    Iterable[
                        Union[bytes, Iterable[Union[bytes, Iterable[bytes]]]]
                    ],
                ]
            ],
        ]:
            """
            This method parses IPv6 with Zone ID.

            >>> StandardRules.Network.ipv6_zoneid(b"::1%eth0")
            (8, [[b':', b':', b'1'], b'%', [[b'e', b't', b'h', b'0']]])
            >>> StandardRules.Network.ipv6_zoneid(b"::1%0")
            (5, [[b':', b':', b'1'], b'%', [[b'0']]])
            >>> StandardRules.Network.ipv6_zoneid(b"::1%9")
            (5, [[b':', b':', b'1'], b'%', [[b'9']]])
            >>> StandardRules.Network.ipv6_zoneid(b"::1%259")
            (7, [[b':', b':', b'1'], [b'%', b'2', b'5'], [[b'9']]])
            >>> StandardRules.Network.ipv6_zoneid(b"::1%250")
            (7, [[b':', b':', b'1'], [b'%', b'2', b'5'], [[b'0']]])
            >>> StandardRules.Network.ipv6_zoneid(b"::1%25eth0")
            (10, [[b':', b':', b'1'], [b'%', b'2', b'5'], [[b'e', b't', b'h', b'0']]])
            >>> StandardRules.Network.ipv6_zoneid(b"::1%eth0-_~.test")
            (16, [[b':', b':', b'1'], b'%', [[b'e', b't', b'h', b'0', b'-', b'_', b'~', b'.', b't', b'e', b's', b't']]])
            >>> StandardRules.Network.ipv6_zoneid(b"::1%eth0-_~.#test")
            (12, [[b':', b':', b'1'], b'%', [[b'e', b't', b'h', b'0', b'-', b'_', b'~', b'.']]])
            >>>
            """

            def start(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        lambda d, p: PegParser.sequence(
                            [
                                StandardMatch.check_char(37),
                                StandardMatch.check_char(50),
                                StandardMatch.check_char(53),
                            ],
                            d,
                            p,
                        ),
                        StandardMatch.check_char(37),
                    ],
                    data,
                    position,
                )

            def character(data: bytes, position: int):
                return PegParser.one_or_more(
                    StandardRules.Url._characters,
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    StandardRules.Network.ipv6,
                    start,
                    character,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "ipv6_zoneid"

            return result

        def ipv4(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[Union[bytes, Iterable[bytes]]]]]:
            """
            This method parses IPv4 format.

            >>> StandardRules.Network.ipv4(b"256.256.256.256")
            (0, None)
            >>> StandardRules.Network.ipv4(b"310.200.200.200")
            (0, None)
            >>> StandardRules.Network.ipv4(b"255.255.255.255")
            (15, [[b'2', b'5', b'5'], b'.', [b'2', b'5', b'5'], b'.', [b'2', b'5', b'5'], b'.', [b'2', b'5', b'5']])
            >>> StandardRules.Network.ipv4(b"249.230.225.212")
            (15, [[b'2', b'4', b'9'], b'.', [b'2', b'3', b'0'], b'.', [b'2', b'2', b'5'], b'.', [b'2', b'1', b'2']])
            >>> StandardRules.Network.ipv4(b"199.130.125.112")
            (15, [[b'1', b'9', b'9'], b'.', [b'1', b'3', b'0'], b'.', [b'1', b'2', b'5'], b'.', [b'1', b'1', b'2']])
            >>> StandardRules.Network.ipv4(b"1.1.1.1")
            (7, [b'1', b'.', b'1', b'.', b'1', b'.', b'1'])
            >>> StandardRules.Network.ipv4(b"0.0.0.0")
            (7, [b'0', b'.', b'0', b'.', b'0', b'.', b'0'])
            >>> StandardRules.Network.ipv4(b"10.20.80.90")
            (11, [[b'1', b'0'], b'.', [b'2', b'0'], b'.', [b'8', b'0'], b'.', [b'9', b'0']])
            >>> StandardRules.Network.ipv4(b".20.80.90")
            (0, None)
            >>> StandardRules.Network.ipv4(b"10.20.80.")
            (0, None)
            >>> StandardRules.Network.ipv4(b"10.20..80.90")
            (0, None)
            >>> StandardRules.Network.ipv4(b"10.20.80.1110")
            (12, [[b'1', b'0'], b'.', [b'2', b'0'], b'.', [b'8', b'0'], b'.', [b'1', b'1', b'1']])
            >>>
            """

            def digit250(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(50),
                        StandardMatch.check_char(53),
                        StandardMatch.or_check_chars(48, 49, 50, 51, 52, 53),
                    ],
                    data,
                    position,
                )

            def digit200(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(50),
                        StandardMatch.or_check_chars(48, 49, 50, 51, 52),
                        StandardMatch.is_digit,
                    ],
                    data,
                    position,
                )

            def digit100(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(49),
                        StandardMatch.is_digit,
                        StandardMatch.is_digit,
                    ],
                    data,
                    position,
                )

            def digit3(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        digit250,
                        digit200,
                        digit100,
                    ],
                    data,
                    position,
                )

            def digit2(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.is_digit,
                        StandardMatch.is_digit,
                    ],
                    data,
                    position,
                )

            def digits(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        digit3,
                        digit2,
                        StandardMatch.is_digit,
                    ],
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    digits,
                    StandardMatch.check_char(46),
                    digits,
                    StandardMatch.check_char(46),
                    digits,
                    StandardMatch.check_char(46),
                    digits,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "ipv4"

            return result

        def ipvfuture(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[Union[bytes, Iterable[bytes]]]]]:
            """
            This method parses the IPvFuture.

            >>> StandardRules.Network.ipvfuture(b"v0123456789abcdef.any_characters-including&$(exploit)'&&exploit")
            (63, [b'v', [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'a', b'b', b'c', b'd', b'e', b'f'], b'.', [[b'a', b'n', b'y', b'_', b'c', b'h', b'a', b'r', b'a', b'c', b't', b'e', b'r', b's', b'-', b'i', b'n', b'c', b'l', b'u', b'd', b'i', b'n', b'g'], b'&', b'$', b'(', [b'e', b'x', b'p', b'l', b'o', b'i', b't'], b')', b"'", b'&', b'&', [b'e', b'x', b'p', b'l', b'o', b'i', b't']]])
            >>> StandardRules.Network.ipvfuture(b"0123456789abcdef.any_characters-including&$(exploit)'&&exploit")
            (0, None)
            >>> StandardRules.Network.ipvfuture(b"v.any_characters-including&$(exploit)'&&exploit")
            (0, None)
            >>> StandardRules.Network.ipvfuture(b"v0123456789abcdefany_characters-including&$(exploit)'&&exploit")
            (0, None)
            >>> StandardRules.Network.ipvfuture(b"v0123456789abcdef.?any_characters-including&$(exploit)'&&exploit")
            (0, None)
            >>> StandardRules.Network.ipvfuture(b"v0123456789abcdef.%25")
            (21, [b'v', [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'a', b'b', b'c', b'd', b'e', b'f'], b'.', [[[b'%', b'2', b'5']]]])
            >>> StandardRules.Network.ipvfuture(b"v0123456789abcdef.%2")
            (0, None)
            >>>
            """

            def characters(data, position):
                return PegParser.one_or_more(
                    StandardRules.Url._characters_subdelims_colon,
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    StandardMatch.check_char(118),
                    StandardRules.Format.hex,
                    StandardMatch.check_char(46),
                    characters,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "ipvfuture"

            return result

        def host(data: bytes, position: int = 0) -> Tuple[
            int,
            Iterable[
                Union[
                    bytes,
                    Iterable[
                        Iterable[
                            Union[
                                bytes, Iterable[Union[bytes, Iterable[bytes]]]
                            ]
                        ]
                    ],
                ]
            ],
        ]:
            """
            This method parses the network host value.

            >>> StandardRules.Network.host(b"test-hostname")
            (13, [b't', [b'e', b's', b't', [[b'-'], b'h'], b'o', b's', b't', b'n', b'a', b'm', b'e']])
            >>> StandardRules.Network.host(b"test.fqdn")
            (9, [[b't', [b'e', b's', b't']], [[b'.', [b'f', [b'q', b'd', b'n']]]]])
            >>> StandardRules.Network.host(b"127.0.0.1")
            (9, [[b'1', [b'2', b'7']], [[b'.', [b'0', []]], [b'.', [b'0', []]], [b'.', [b'1', []]]]])
            >>> StandardRules.Network.host(b"[::1]")
            (5, [b'[', [b':', b':', b'1'], b']'])
            >>> StandardRules.Network.host(b"[::dead:beef%eth1]")
            (18, [b'[', [[b':', b':', [[b'd', b'e', b'a', b'd'], b':'], [b'b', b'e', b'e', b'f']], b'%', [[b'e', b't', b'h', b'1']]], b']'])
            >>> StandardRules.Network.host(b"[v0123456789abcdef.%25]")
            (23, [b'[', [b'v', [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'a', b'b', b'c', b'd', b'e', b'f'], b'.', [[[b'%', b'2', b'5']]]], b']'])
            >>> StandardRules.Network.host(b"dead::beef")
            (4, [b'd', [b'e', b'a', b'd']])
            >>> StandardRules.Network.host(b"dead::beef%25test|")
            (4, [b'd', [b'e', b'a', b'd']])
            >>> StandardRules.Network.host(b"v0123456789abcdef.%25")
            (17, [b'v', [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'a', b'b', b'c', b'd', b'e', b'f']])
            >>>
            """

            def address_literal(data: bytes, position: int):
                return PegParser.ordered_choice(
                    [
                        StandardRules.Network.ipvfuture,
                        StandardRules.Network.ipv6_zoneid,
                        StandardRules.Network.ipv6,
                    ],
                    data,
                    position,
                )

            def ip_literal(data: bytes, position: int):
                return PegParser.sequence(
                    [
                        StandardMatch.check_char(91),
                        address_literal,
                        StandardMatch.check_char(93),
                    ],
                    data,
                    position,
                )

            result = PegParser.ordered_choice(
                [
                    ip_literal,
                    StandardRules.Network.fqdn,
                    StandardRules.Network.ipv4,
                    StandardRules.Network.hostname,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "host"

            return result

        def host_port(data: bytes, position: int = 0) -> Tuple[
            int,
            Iterable[
                Union[
                    bytes,
                    Iterable[
                        Union[
                            bytes,
                            Iterable[
                                Iterable[
                                    Union[
                                        bytes,
                                        Iterable[
                                            Union[bytes, Iterable[bytes]]
                                        ],
                                    ]
                                ]
                            ],
                        ]
                    ],
                ]
            ],
        ]:
            """
            This method parses the network host value with a port.

            >>> StandardRules.Network.host_port(b"test-hostname:4545")
            (18, [[b't', [b'e', b's', b't', [[b'-'], b'h'], b'o', b's', b't', b'n', b'a', b'm', b'e']], b':', [b'4', b'5', b'4', b'5']])
            >>> StandardRules.Network.host_port(b"test.fqdn:8080")
            (14, [[[b't', [b'e', b's', b't']], [[b'.', [b'f', [b'q', b'd', b'n']]]]], b':', [b'8', b'0', b'8', b'0']])
            >>> StandardRules.Network.host_port(b"127.0.0.1:65535")
            (15, [[[b'1', [b'2', b'7']], [[b'.', [b'0', []]], [b'.', [b'0', []]], [b'.', [b'1', []]]]], b':', [b'6', b'5', b'5', b'3', b'5']])
            >>> StandardRules.Network.host_port(b"[::1]:1234")
            (10, [[b'[', [b':', b':', b'1'], b']'], b':', [b'1', b'2', b'3', b'4']])
            >>> StandardRules.Network.host_port(b"[::dead:beef%eth1]:7845")
            (23, [[b'[', [[b':', b':', [[b'd', b'e', b'a', b'd'], b':'], [b'b', b'e', b'e', b'f']], b'%', [[b'e', b't', b'h', b'1']]], b']'], b':', [b'7', b'8', b'4', b'5']])
            >>> StandardRules.Network.host_port(b"[v0123456789abcdef.%25]:8989")
            (28, [[b'[', [b'v', [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'a', b'b', b'c', b'd', b'e', b'f'], b'.', [[[b'%', b'2', b'5']]]], b']'], b':', [b'8', b'9', b'8', b'9']])
            >>> StandardRules.Network.host_port(b"[dead::beef]:abc")
            (0, None)
            >>> StandardRules.Network.host_port(b"[dead::beef%25t]:+4578")
            (0, None)
            >>> StandardRules.Network.host_port(b"[v0123456789abcdef.%25]4542")
            (0, None)
            >>>
            """

            result = PegParser.sequence(
                [
                    StandardRules.Network.host,
                    StandardMatch.check_char(58),
                    StandardRules.Types.digits,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "host_port"

            return result

        def user_info(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[Union[bytes, Iterable[bytes]]]]]:
            """
            This method parses the network host value with a port.

            >>> StandardRules.Network.user_info(b"toto:123")
            (8, [[b't', b'o', b't', b'o'], b':', [b'1', b'2', b'3']])
            >>> StandardRules.Network.user_info(b"test:p@ssword")
            (6, [[b't', b'e', b's', b't'], b':', [b'p']])
            >>> StandardRules.Network.user_info(b"test123:p+~._-ssword%25")
            (23, [[b't', b'e', b's', b't', b'1', b'2', b'3'], b':', [b'p', b'+', b'~', b'.', b'_', b'-', b's', b's', b'w', b'o', b'r', b'd', [b'%', b'2', b'5']]])
            >>>
            """

            result = PegParser.one_or_more(
                StandardRules.Url._characters_subdelims_colon,
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "user_info"

            return result

    class Http:
        """
        This class implements a complete parser for http.
        """

        def verb(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method returns `verb` bytes for the protocol.

            >>> StandardRules.Http.verb(b'GET')
            (3, [b'G', b'E', b'T'])
            >>> StandardRules.Http.verb(b'POST')
            (4, [b'P', b'O', b'S', b'T'])
            >>> StandardRules.Http.verb(b'put')
            (3, [b'p', b'u', b't'])
            >>> StandardRules.Http.verb(b'delete')
            (6, [b'd', b'e', b'l', b'e', b't', b'e'])
            >>> StandardRules.Http.verb(b'Options')
            (7, [b'O', b'p', b't', b'i', b'o', b'n', b's'])
            >>> StandardRules.Http.verb(b'hEAD')
            (4, [b'h', b'E', b'A', b'D'])
            >>> StandardRules.Http.verb(b'PaTcH')
            (5, [b'P', b'a', b'T', b'c', b'H'])
            >>> StandardRules.Http.verb(b'tRaCe')
            (5, [b't', b'R', b'a', b'C', b'e'])
            >>>
            """

            result = StandardRules.Http.token(data, position)

            if isinstance(result[1], MatchList):
                result[1]._match_name = "verb"

            return result

        def magic(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method returns `magic` bytes for the protocol.

            >>> StandardRules.Http.magic(b'http')
            (4, [b'h', b't', b't', b'p'])
            >>> StandardRules.Http.magic(b'HTTP')
            (4, [b'H', b'T', b'T', b'P'])
            >>>
            """

            result = StandardRules.Format.word(data, position)

            if isinstance(result[1], MatchList):
                result[1]._match_name = "magic"

            return result

        def version(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[Union[bytes, Iterable[bytes]]]]]:
            """
            This method returns `version` bytes for the protocol.

            >>> StandardRules.Http.version(b'1.0')
            (3, [[b'1'], b'.', [b'0']])
            >>> StandardRules.Http.version(b'1.1')
            (3, [[b'1'], b'.', [b'1']])
            >>>
            """

            result = StandardRules.Types.float(data, position)

            if isinstance(result[1], MatchList):
                result[1]._match_name = "version"

            return result

        def protocol_version(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                None,
                Iterable[
                    Union[bytes, Iterable[Union[bytes, Iterable[bytes]]]]
                ],
            ],
        ]:
            """
            This method returns `version` bytes for the protocol.

            >>> StandardRules.Http.protocol_version(b'HTTP/1.0')
            (8, [[b'H', b'T', b'T', b'P'], b'/', [[b'1'], b'.', [b'0']]])
            >>> StandardRules.Http.protocol_version(b'http/1.1')
            (8, [[b'h', b't', b't', b'p'], b'/', [[b'1'], b'.', [b'1']]])
            >>>
            """

            result = PegParser.sequence(
                [
                    StandardRules.Http.magic,
                    StandardMatch.check_char(47),
                    StandardRules.Http.version,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "http_version"

            return result

        def status_code(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method returns `status code` bytes for the response.

            >>> StandardRules.Http.status_code(b'200')
            (3, [b'2', b'0', b'0'])
            >>> StandardRules.Http.status_code(b'404')
            (3, [b'4', b'0', b'4'])
            >>>
            """

            result = StandardRules.Types.digits(data, position)

            if isinstance(result[1], MatchList):
                result[1]._match_name = "status_code"

            return result

        def is_text_char(
            data: bytes, position: int
        ) -> Tuple[int, Union[None, bytes]]:
            r"""
            This method checks a position for an HTTP TEXT character.

            >>> StandardRules.Http.is_text_char(b"a1Bc", 0)
            (1, b'a')
            >>> StandardRules.Http.is_text_char(b"a1Bc", 1)
            (2, b'1')
            >>> StandardRules.Http.is_text_char(b"a1Bc", 2)
            (3, b'B')
            >>> StandardRules.Http.is_text_char(b"a1B\0", 3)
            (3, None)
            >>> len([x for x in range(256) if StandardRules.Http.is_text_char(bytes((x,)), 0)[1] is not None])
            96
            >>>
            """

            if len(data) == position:
                return position, None

            char = data[position]
            if 32 <= char <= 126 or char == 9:
                return position + 1, bytes((char,))
            return position, None

        def text(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method parses HTTP TEXT format.

            >>> StandardRules.Http.text(b'HTTp Text 200 !')
            (15, [b'H', b'T', b'T', b'p', b' ', b'T', b'e', b'x', b't', b' ', b'2', b'0', b'0', b' ', b'!'])
            >>> StandardRules.Http.text(b'Another text to test 5.5, other things ?":@#')
            (44, [b'A', b'n', b'o', b't', b'h', b'e', b'r', b' ', b't', b'e', b'x', b't', b' ', b't', b'o', b' ', b't', b'e', b's', b't', b' ', b'5', b'.', b'5', b',', b' ', b'o', b't', b'h', b'e', b'r', b' ', b't', b'h', b'i', b'n', b'g', b's', b' ', b'?', b'"', b':', b'@', b'#'])
            >>>
            """

            return PegParser.one_or_more(
                StandardRules.Http.is_text_char,
                data,
                position,
            )

        def reason(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method returns `reason` bytes for the response status.

            >>> StandardRules.Http.reason(b'OK')
            (2, [b'O', b'K'])
            >>> StandardRules.Http.reason(b'Internal Server Error')
            (21, [b'I', b'n', b't', b'e', b'r', b'n', b'a', b'l', b' ', b'S', b'e', b'r', b'v', b'e', b'r', b' ', b'E', b'r', b'r', b'o', b'r'])
            >>>
            """

            result = StandardRules.Http.text(data, position)

            if isinstance(result[1], MatchList):
                result[1]._match_name = "reason"

            return result

        def field_value(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method returns `field_value` bytes for HTTP.

            >>> StandardRules.Http.field_value(b'application/json; charset="utf8"')
            (32, [b'a', b'p', b'p', b'l', b'i', b'c', b'a', b't', b'i', b'o', b'n', b'/', b'j', b's', b'o', b'n', b';', b' ', b'c', b'h', b'a', b'r', b's', b'e', b't', b'=', b'"', b'u', b't', b'f', b'8', b'"'])
            >>> StandardRules.Http.field_value(b'Fri, 02 May 2025 14:02:56 GMT')
            (29, [b'F', b'r', b'i', b',', b' ', b'0', b'2', b' ', b'M', b'a', b'y', b' ', b'2', b'0', b'2', b'5', b' ', b'1', b'4', b':', b'0', b'2', b':', b'5', b'6', b' ', b'G', b'M', b'T'])
            >>>
            """

            result = StandardRules.Http.text(data, position)

            if isinstance(result[1], MatchList):
                result[1]._match_name = "field_value"

            return result

        def response_start(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                None,
                Iterable[
                    Union[
                        bytes,
                        Iterable[
                            Union[
                                bytes, Iterable[Union[bytes, Iterable[bytes]]]
                            ]
                        ],
                    ]
                ],
            ],
        ]:
            r"""
            This method parses the first line for HTTP response.

            >>> StandardRules.Http.response_start(b'HTTP/1.1 200 OK\r\n')
            (17, [[[b'H', b'T', b'T', b'P'], b'/', [[b'1'], b'.', [b'1']]], b' ', [b'2', b'0', b'0'], b' ', [b'O', b'K'], b'\r', b'\n'])
            >>> StandardRules.Http.response_start(b'HTTP/1.0 500 Internal Server Error\r\n')
            (36, [[[b'H', b'T', b'T', b'P'], b'/', [[b'1'], b'.', [b'0']]], b' ', [b'5', b'0', b'0'], b' ', [b'I', b'n', b't', b'e', b'r', b'n', b'a', b'l', b' ', b'S', b'e', b'r', b'v', b'e', b'r', b' ', b'E', b'r', b'r', b'o', b'r'], b'\r', b'\n'])
            >>>
            """

            return PegParser.sequence(
                [
                    StandardRules.Http.protocol_version,
                    StandardMatch.check_char(32),
                    StandardRules.Http.status_code,
                    StandardMatch.check_char(32),
                    StandardRules.Http.reason,
                    StandardMatch.check_char(13),
                    StandardMatch.check_char(10),
                ],
                data,
                position,
            )

        def token(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method parses the first line for HTTP response.

            >>> StandardRules.Http.token(b'Content-Type')
            (12, [b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'T', b'y', b'p', b'e'])
            >>> StandardRules.Http.token(b'Content-Length')
            (14, [b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'L', b'e', b'n', b'g', b't', b'h'])
            >>>
            """

            def character(data, position):
                return PegParser.ordered_choice(
                    [
                        StandardMatch.is_letter,
                        StandardMatch.is_digit,
                        StandardMatch.or_check_chars(
                            33,
                            35,
                            36,
                            37,
                            38,
                            39,
                            42,
                            43,
                            45,
                            46,
                            94,
                            95,
                            96,
                            124,
                            126,
                        ),
                    ],
                    data,
                    position,
                )

            return PegParser.one_or_more(
                character,
                data,
                position,
            )

        def field_name(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[bytes]]]:
            """
            This method returns `field_name` bytes for HTTP.

            >>> StandardRules.Http.field_name(b'Content-Type')
            (12, [b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'T', b'y', b'p', b'e'])
            >>> StandardRules.Http.field_name(b'Content-Length')
            (14, [b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'L', b'e', b'n', b'g', b't', b'h'])
            >>>
            """

            result = StandardRules.Http.token(data, position)

            if isinstance(result[1], MatchList):
                result[1]._match_name = "field_name"

            return result

        def header(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[Union[bytes, Iterable[bytes]]]]]:
            r"""
            This method parses a HTTP header.

            >>> StandardRules.Http.header(b'Content-Type: application/json\r\n')
            (32, [[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'T', b'y', b'p', b'e'], b':', b' ', [b'a', b'p', b'p', b'l', b'i', b'c', b'a', b't', b'i', b'o', b'n', b'/', b'j', b's', b'o', b'n'], b'\r', b'\n'])
            >>> StandardRules.Http.header(b'Content-Length: 12\r\n')
            (20, [[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'L', b'e', b'n', b'g', b't', b'h'], b':', b' ', [b'1', b'2'], b'\r', b'\n'])
            >>>
            """

            result = PegParser.sequence(
                [
                    StandardRules.Http.field_name,
                    StandardMatch.check_char(58),
                    StandardMatch.check_char(32),
                    StandardRules.Http.field_value,
                    StandardMatch.check_char(13),
                    StandardMatch.check_char(10),
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "header"

            return result

        def headers(
            data: bytes, position: int = 0
        ) -> Tuple[int, Union[None, Iterable[Union[bytes, Iterable[bytes]]]]]:
            r"""
            This method parses HTTP headers.

            >>> StandardRules.Http.headers(b'Content-Type: application/json\r\nContent-Length: 12\r\n\r\n')
            (54, [[[[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'T', b'y', b'p', b'e'], b':', b' ', [b'a', b'p', b'p', b'l', b'i', b'c', b'a', b't', b'i', b'o', b'n', b'/', b'j', b's', b'o', b'n'], b'\r', b'\n'], [[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'L', b'e', b'n', b'g', b't', b'h'], b':', b' ', [b'1', b'2'], b'\r', b'\n']], b'\r', b'\n'])
            >>>
            """

            def _headers(data, position):
                return PegParser.one_or_more(
                    StandardRules.Http.header,
                    data,
                    position,
                )

            result = PegParser.sequence(
                [
                    _headers,
                    StandardMatch.check_char(13),
                    StandardMatch.check_char(10),
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "headers"

            return result

        def response(data: bytes, position: int = 0) -> Tuple[
            int,
            Union[
                None,
                Iterable[
                    Iterable[
                        Union[
                            bytes,
                            Iterable[
                                Union[
                                    bytes,
                                    Iterable[Union[bytes, Iterable[bytes]]],
                                ]
                            ],
                        ]
                    ]
                ],
            ],
        ]:
            r"""
            This method parses HTTP response.

            >>> StandardRules.Http.response(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 12\r\n\r\n')
            (71, [[[[b'H', b'T', b'T', b'P'], b'/', [[b'1'], b'.', [b'1']]], b' ', [b'2', b'0', b'0'], b' ', [b'O', b'K'], b'\r', b'\n'], [[[[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'T', b'y', b'p', b'e'], b':', b' ', [b'a', b'p', b'p', b'l', b'i', b'c', b'a', b't', b'i', b'o', b'n', b'/', b'j', b's', b'o', b'n'], b'\r', b'\n'], [[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'L', b'e', b'n', b'g', b't', b'h'], b':', b' ', [b'1', b'2'], b'\r', b'\n']], b'\r', b'\n']])
            >>>
            """

            result = PegParser.sequence(
                [
                    StandardRules.Http.response_start,
                    StandardRules.Http.headers,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "response"

            return result

        def request(data: bytes, position: int = 0):
            r"""
            This method parses HTTP request.

            >>> StandardRules.Http.request(b'POST http://test.test/test;test=test?test=test HTTP/1.0\r\nHost: myhost\r\nContent-Type: application/json; charset="utf-8"\r\nContent-Length: 12\r\n\r\nabcdefabcdef')
            (142, [[b'P', b'O', b'S', b'T'], b' ', [[b'h', [b't', b't', b'p']], b':', [b'/', b'/', [[b't', [b'e', b's', b't']], [[b'.', [b't', [b'e', b's', b't']]]]], [[b'/', [[b't', b'e', b's', b't']]]]], [b';', [[[b't', b'e', b's', b't'], b'=', [b't', b'e', b's', b't']], []]], [b'?', [[b't', b'e', b's', b't'], b'=', [b't', b'e', b's', b't']]], True], b' ', [[b'H', b'T', b'T', b'P'], b'/', [[b'1'], b'.', [b'0']]], b'\r', b'\n', [[[[b'H', b'o', b's', b't'], b':', b' ', [b'm', b'y', b'h', b'o', b's', b't'], b'\r', b'\n'], [[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'T', b'y', b'p', b'e'], b':', b' ', [b'a', b'p', b'p', b'l', b'i', b'c', b'a', b't', b'i', b'o', b'n', b'/', b'j', b's', b'o', b'n', b';', b' ', b'c', b'h', b'a', b'r', b's', b'e', b't', b'=', b'"', b'u', b't', b'f', b'-', b'8', b'"'], b'\r', b'\n'], [[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'L', b'e', b'n', b'g', b't', b'h'], b':', b' ', [b'1', b'2'], b'\r', b'\n']], b'\r', b'\n']])
            >>> StandardRules.Http.request(b'POST /test;test=test?test=test HTTP/1.0\r\nHost: myhost\r\nContent-Type: application/json; charset="utf-8"\r\nContent-Length: 12\r\n\r\nabcdefabcdef')
            (126, [[b'P', b'O', b'S', b'T'], b' ', [[[b'/', [[b't', b'e', b's', b't']]]], [b';', [[[b't', b'e', b's', b't'], b'=', [b't', b'e', b's', b't']], []]], [b'?', [[b't', b'e', b's', b't'], b'=', [b't', b'e', b's', b't']]]], b' ', [[b'H', b'T', b'T', b'P'], b'/', [[b'1'], b'.', [b'0']]], b'\r', b'\n', [[[[b'H', b'o', b's', b't'], b':', b' ', [b'm', b'y', b'h', b'o', b's', b't'], b'\r', b'\n'], [[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'T', b'y', b'p', b'e'], b':', b' ', [b'a', b'p', b'p', b'l', b'i', b'c', b'a', b't', b'i', b'o', b'n', b'/', b'j', b's', b'o', b'n', b';', b' ', b'c', b'h', b'a', b'r', b's', b'e', b't', b'=', b'"', b'u', b't', b'f', b'-', b'8', b'"'], b'\r', b'\n'], [[b'C', b'o', b'n', b't', b'e', b'n', b't', b'-', b'L', b'e', b'n', b'g', b't', b'h'], b':', b' ', [b'1', b'2'], b'\r', b'\n']], b'\r', b'\n']])
            >>>
            """

            def uri(data, position):
                result = PegParser.ordered_choice(
                    [
                        lambda d, p: PegParser.sequence(
                            [
                                StandardRules.Url.path,
                                StandardRules.Url.parameters,
                                StandardRules.Url.query,
                            ],
                            d,
                            p,
                        ),
                        lambda d, p: PegParser.sequence(
                            [StandardRules.Url.path, StandardRules.Url.query],
                            d,
                            p,
                        ),
                        lambda d, p: PegParser.sequence(
                            [
                                StandardRules.Url.path,
                                StandardRules.Url.parameters,
                            ],
                            d,
                            p,
                        ),
                        StandardRules.Url.full,
                    ],
                    data,
                    position,
                )
                if isinstance(result[1], MatchList):
                    result[1]._match_name = "uri"
                return result

            result = PegParser.sequence(
                [
                    StandardRules.Http.verb,
                    StandardMatch.check_char(32),
                    uri,
                    StandardMatch.check_char(32),
                    StandardRules.Http.protocol_version,
                    StandardMatch.check_char(13),
                    StandardMatch.check_char(10),
                    StandardRules.Http.headers,
                ],
                data,
                position,
            )

            if isinstance(result[1], MatchList):
                result[1]._match_name = "request"

            return result


def get_matchs(
    data: Iterable[Union[bytes, bool, Iterable]]
) -> Dict[str, List[bytearray]]:
    """
    This function returns the structured matches into a dict.

    >>> get_matchs(StandardRules.Url.full(b"https://my.full.url/with/path;and=parameters?query=too#fragment")[1])
    defaultdict(<class 'list'>, {'url': [bytearray(b'https://my.full.url/with/path;and=parameters?query=too#fragment')], 'scheme': [bytearray(b'https')], 'host': [bytearray(b'my.full.url')], 'hostname': [bytearray(b'my'), bytearray(b'full'), bytearray(b'url')], 'path': [bytearray(b'/with/path')], 'parameters': [bytearray(b';and=parameters')], 'form_data': [bytearray(b'and=parameters')], 'query': [bytearray(b'?query=too')], 'fragment': [bytearray(b'#fragment')]})
    >>>
    """

    match_dict = defaultdict(list)

    def process_element(element):
        if isinstance(element, bool):
            return None

        if isinstance(element, MatchList):
            if getattr(element, "_match_name", None):
                match_dict[element._match_name].append(flatten_bytes(element))

            for sub_element in element:
                process_element(sub_element)

    def flatten_bytes(element):
        byte_data = bytearray()
        for sublist in element:
            if isinstance(sublist, bytes):
                byte_data.extend(sublist)
            elif isinstance(sublist, MatchList):
                byte_data.extend(flatten_bytes(sublist))
        return byte_data

    process_element(data)
    return match_dict


def get_http_content(data: Iterable[Union[bytes, Iterable]]) -> Tuple[
    Dict[str, List[bytearray]],
    List[Tuple[str, str]],
    int,
    Union[None, str],
    Union[None, str],
]:
    """
    This function takes parsed HTTP response or request and use the parsing
    to transform into useful python object.
    """

    matches = get_matchs(data)
    headers = []
    values = matches["field_value"]
    host = None
    content_type = None
    content_length = 0

    for i, name in enumerate(matches["field_name"]):
        name = name.decode("ascii")
        value = values[i].decode("ascii")
        headers.append((name, value))
        if name.casefold() == "content-length":
            content_length = int(value)
        elif name.casefold() == "content-type":
            content_type = value
        elif name.casefold() == "host":
            host = value

    return matches, headers, content_length, content_type, host


def parse_http_request(data: bytes) -> HttpRequest:
    r"""
    This function takes HTTP request bytes as arguments,
    parses it and generates the HttpRequest object.

    >>> parse_http_request(b'POST /test;test=test?test=test HTTP/1.0\r\nHost: myhost\r\nContent-Type: application/json; charset="utf-8"\r\nContent-Length: 12\r\n\r\nabcdefabcdef')
    HttpRequest(verb='POST', uri='/test;test=test?test=test', magic=b'HTTP', version=1.0, headers=[('Host', 'myhost'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '12')], body=b'abcdefabcdef', content_length=12, content_type='application/json; charset="utf-8"', host='myhost')
    >>>
    """

    content_start, request = StandardRules.Http.request(data)

    if not request:
        raise ValueError("Invalid HTTP request")

    request_matches, headers, content_length, content_type, host = (
        get_http_content(request)
    )

    return HttpRequest(
        request_matches["verb"][0].decode("ascii"),
        request_matches["uri"][0].decode("ascii"),
        bytes(request_matches["magic"][0]),
        float(request_matches["version"][0].decode("ascii")),
        headers,
        data[content_start:],
        content_length,
        content_type,
        host,
    )


def parse_http_response(data: bytes) -> HttpResponse:
    r"""
    This function takes HTTP response bytes as arguments,
    parses it and generates the HttpResponse object.

    >>> parse_http_response(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 12\r\n\r\nabcdefabcdef')
    HttpResponse(magic=b'HTTP', version=1.1, code=200, reason='OK', headers=[('Content-Type', 'application/json'), ('Content-Length', '12')], body=b'abcdefabcdef', content_length=12, content_type='application/json')
    >>>
    """

    body_start, response = StandardRules.Http.response(data)

    if not response:
        raise ValueError("Invalid HTTP response")

    response_matches, headers, content_length, content_type, _ = (
        get_http_content(response)
    )

    return HttpResponse(
        bytes(response_matches["magic"][0]),
        float(response_matches["version"][0].decode("ascii")),
        int(response_matches["status_code"][0].decode("ascii")),
        response_matches["reason"][0].decode("ascii"),
        headers,
        data[body_start:],
        content_length,
        content_type,
    )


StandardRules_Url = StandardRules.Url
StandardRules_Http = StandardRules.Http
StandardRules_Types = StandardRules.Types
StandardRules_Format = StandardRules.Format
StandardRules_Network = StandardRules.Network

if __name__ == "__main__":
    from doctest import testmod

    testmod()
