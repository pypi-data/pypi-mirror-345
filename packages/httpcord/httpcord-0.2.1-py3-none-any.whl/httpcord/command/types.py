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
        "_min_value",
        "_max_value",
        "_min_length",
        "_max_length",
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
            options: dict[str, CommandOption] | None = ...,
            choices: None = ...,
            min_value: None = ...,
            max_value: None = ...,
            min_length: None = ...,
            max_length: None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.SUB_COMMAND_GROUP],
            required: None = ...,
            autocomplete: None = ...,
            options: dict[str, CommandOption] = ...,
            choices: None = ...,
            min_value: None = ...,
            max_value: None = ...,
            min_length: None = ...,
            max_length: None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.STRING],
            required: bool | None = ...,
            autocomplete: Literal[False] | None = ...,
            options: None = ...,
            choices: list[Choice] | None = ...,
            min_value: None = ...,
            max_value: None = ...,
            min_length: int | None = ...,
            max_length: int | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.STRING],
            required: bool | None = ...,
            autocomplete: Literal[True] = ...,
            options: None = ...,
            choices: None = ...,
            min_value: None = ...,
            max_value: None = ...,
            min_length: int | None = ...,
            max_length: int | None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.INTEGER],
            required: bool | None = ...,
            autocomplete: Literal[False] | None = ...,
            options: None = ...,
            choices: list[Choice] | None = ...,
            min_value: int | None = ...,
            max_value: int | None = ...,
            min_length: None = ...,
            max_length: None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.INTEGER],
            required: bool | None = ...,
            autocomplete: Literal[True] = ...,
            options: None = ...,
            choices: None = ...,
            min_value: int | None = ...,
            max_value: int | None = ...,
            min_length: None = ...,
            max_length: None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.NUMBER],
            required: bool | None = ...,
            autocomplete: Literal[False] | None = ...,
            options: None = ...,
            choices: list[Choice] | None = ...,
            min_value: float | None = ...,
            max_value: float | None = ...,
            min_length: None = ...,
            max_length: None = ...,
        ) -> None: ...

        @overload
        def __init__(
            self,
            name: str,
            description: str | None,
            type: Literal[ApplicationCommandOptionType.NUMBER],
            required: bool | None = ...,
            autocomplete: Literal[True] = ...,
            options: None = ...,
            choices: None = ...,
            min_value: float | None = ...,
            max_value: float | None = ...,
            min_length: None = ...,
            max_length: None = ...,
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
            min_value: None = ...,
            max_value: None = ...,
            min_length: None = ...,
            max_length: None = ...,
        ) -> None: ...

    def __init__(
        self,
        name: str,
        description: str | None,
        type: ApplicationCommandOptionType,
        required: bool | None = False,
        autocomplete: bool | None = False,
        options: dict[str, CommandOption] | None = None,
        choices: list[Choice] | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:
        self._name: str = name
        self._description: str | None = description
        self._type: ApplicationCommandOptionType = type
        self._required: bool = required or False
        self._autocomplete: bool | None = autocomplete
        self._options: dict[str, CommandOption] | None = options
        self._choices: list[Choice] | None = choices
        self._min_value: int | float | None = min_value
        self._max_value: int | float | None = max_value
        self._min_length: int | None = min_length
        self._max_length: int | None = max_length

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
            "options": [option.to_dict() for option in self._options.values()] if self._options else None,
            "choices": [choice.to_dict() for choice in self._choices] if self._choices else None,
            "min_value": self._min_value,
            "max_value": self._max_value,
            "min_length": self._min_length,
            "max_length": self._max_length,
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
