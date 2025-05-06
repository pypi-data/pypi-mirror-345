"""
MIT License

Copyright (c) 20234 Isabelle Phoebe <izzy@uwu.gal>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any, Final, TypedDict

from httpcord.enums import (
    ApplicationCommandOptionType,
    InteractionResponseType,
)
from httpcord.interaction import User


__all__: Final[tuple[str, ...]] = (
    "JSONResponseError",
    "JSONResponseType",
    "TYPE_CONVERSION_TABLE",
    "Integer",
    "Float",
    "String",
    "File",
)


@dataclass(slots=True)
class Integer:
    min_value: int | None = None
    max_value: int | None = None


@dataclass(slots=True)
class Float:
    min_value: float | None = None
    max_value: float | None = None


@dataclass(slots=True)
class String:
    min_length: int | None = None
    max_length: int | None = None


class File:
    __slots__: tuple[str, ...] = (
        "content_type",
        "filename",
        "id",
        "height",
        "width",
        "placeholder",
        "placeholder_version",
        "proxy_url",
        "size",
        "url",
        "_content",
    )

    @classmethod
    def from_option(cls, data: dict[str, Any]) -> File:
        return cls(
            content_type=data["content_type"],
            filename=data["filename"],
            id=int(data["id"]),
            height=data["height"],
            width=data["width"],
            placeholder=data["placeholder"],
            placeholder_version=data["placeholder_version"],
            proxy_url=data["proxy_url"],
            size=data["size"],
            url=data["url"],
        )

    def __init__(
        self,
        content_type: str,
        filename: str,
        id: int,
        height: int,
        width: int,
        placeholder: bool,
        placeholder_version: int,
        proxy_url: str,
        size: int,
        url: str,
    ) -> None:
        self.content_type: str = content_type
        self.filename: str = filename
        self.id: int = id
        self.height: int = height
        self.width: int = width
        self.placeholder: bool = placeholder
        self.placeholder_version: int = placeholder_version
        self.proxy_url: str = proxy_url
        self.size: int = size
        self.url: str = url


TYPE_CONVERSION_TABLE: dict[type, ApplicationCommandOptionType] = {
    bool: ApplicationCommandOptionType.BOOLEAN,
    int: ApplicationCommandOptionType.INTEGER,
    float: ApplicationCommandOptionType.NUMBER,
    str: ApplicationCommandOptionType.STRING,
    User: ApplicationCommandOptionType.USER,
    File: ApplicationCommandOptionType.ATTACHMENT,
    # channel: ApplicationCommandOptionType.CHANNEL,
    # mentionable: ApplicationCommandOptionType.MENTIONABLE,
    # role: ApplicationCommandOptionType.ROLE,
}


class JSONResponseError(TypedDict):
    error: str


class JSONResponseType(TypedDict):
    type: InteractionResponseType
