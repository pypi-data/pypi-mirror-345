import dataclasses
import enum
import typing

import PIL.Image

from .types import Color, Font


class Alignment(enum.IntEnum):
	NEAR = -1
	MIDDLE = 0
	FAR = 1


@dataclasses.dataclass(eq=False, kw_only=True)
class Label:
	text: typing.Optional[str] = None
	font: typing.Optional[Font] = None
	halignment: Alignment = Alignment.NEAR
	valignment: Alignment = Alignment.MIDDLE
	color: Color = 'white'
	border: typing.Optional[Color] = None


@dataclasses.dataclass(eq=False, kw_only=True)
class Cell:
	image: typing.Optional[PIL.Image.Image] = None
	label: typing.Optional[Label] = None


@dataclasses.dataclass(eq=False, kw_only=True)
class Vignette:
	background: typing.Union[Color, PIL.Image.Image] = 'black'
	border: typing.Optional[Color] = 'white'
	headers: list[Label] = dataclasses.field(default_factory=list)
	cells: list[Cell] = dataclasses.field(default_factory=list)
	footers: list[Label] = dataclasses.field(default_factory=list)
