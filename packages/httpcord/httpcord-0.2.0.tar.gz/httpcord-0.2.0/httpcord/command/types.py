from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Literal,
    overload,
)

from httpcord.enums import ApplicationCommandOptionType


__all__: tuple[str, ...] = (
    "CommandOption",
    "Choice",
)


class CommandOption:
    __slots__ = (
        "_name",
        "_description",
        "_type",
        "_required",
        "_autocomplete",
        "_options",
        "_choices",
    )

    if TYPE_CHECKING:
        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.SUB_COMMAND],
            required: None = ...,
            autocomplete: Literal[False] | None = ...,
            options: list[CommandOption] | None = ...,
            choices: None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.SUB_COMMAND_GROUP],
            required: None = ...,
            autocomplete: None = ...,
            options: list[CommandOption] = ...,
            choices: None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[
                ApplicationCommandOptionType.STRING,
                ApplicationCommandOptionType.INTEGER,
                ApplicationCommandOptionType.NUMBER,
            ],
            required: bool | None = ...,
            autocomplete: Literal[False] | None = ...,
            options: None = ...,
            choices: list[Choice] | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[
                ApplicationCommandOptionType.STRING,
                ApplicationCommandOptionType.INTEGER,
                ApplicationCommandOptionType.NUMBER,
            ],
            required: bool | None = ...,
            autocomplete: Literal[True] = ...,
            options: None = ...,
            choices: None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[
                ApplicationCommandOptionType.BOOLEAN,
                ApplicationCommandOptionType.USER,
                ApplicationCommandOptionType.CHANNEL,
                ApplicationCommandOptionType.ROLE,
                ApplicationCommandOptionType.MENTIONABLE,
                ApplicationCommandOptionType.ATTACHMENT,
            ],
            required: bool | None = ...,
            autocomplete: None = ...,
            options: None = ...,
            choices: None = ...,
        ) -> None: ...


    def __init__(
        self,
        name: str,
        description: str | None,
        type: ApplicationCommandOptionType,
        required: bool | None = False,
        autocomplete: bool | None = False,
        options: list[CommandOption] | None = None,
        choices: list[Choice] | None = None,
    ) -> None:
        self._name: str = name
        self._description: str | None = description
        self._type: ApplicationCommandOptionType = type
        self._required: bool = required or False
        self._autocomplete: bool | None = autocomplete
        self._options: list[CommandOption] | None = options
        self._choices: list[Choice] | None = choices

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "description": self._description,
            "type": self._type.value,
            "required": self._required if self._type not in [
                ApplicationCommandOptionType.SUB_COMMAND,
                ApplicationCommandOptionType.SUB_COMMAND_GROUP,
            ] else None,
            "autocomplete": self._autocomplete,
            "options": [option.to_dict() for option in self._options] if self._options else None,
            "choices": [choice.to_dict() for choice in self._choices] if self._choices else None,
        }

    def __iter__(self):
        yield from self.to_dict().items()


class Choice:
    __slots__ = (
        "_name",
        "_value",
    )

    def __init__(self, name: str, value: str) -> None:
        self._name: str = name
        self._value: str = value

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "value": self._value,
        }

    def __iter__(self):
        yield from self.to_dict().items()
