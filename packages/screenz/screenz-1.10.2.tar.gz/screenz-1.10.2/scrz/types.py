import typing

import PIL.ImageFont

Color: typing.TypeAlias = typing.Union[str, int, tuple[int, int, int], tuple[int, int, int, int]]
Font: typing.TypeAlias = typing.Union[PIL.ImageFont.ImageFont, PIL.ImageFont.FreeTypeFont]
