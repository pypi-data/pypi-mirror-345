import typing

import PIL.Image
import PIL.ImageDraw

from .layout import Image, Item, Text, measure
from .types import Color


def render(
	*,
	background: typing.Union[Color, PIL.Image.Image],
	items: typing.Iterable[Item],
	debug: bool = False,
) -> PIL.Image.Image:
	width, height = measure(items, 1, 1)

	if isinstance(background, PIL.Image.Image):
		result = PIL.Image.new('RGB', (width, height), typing.cast(str, None))
		for y in range(0, height, background.height):
			for x in range(0, width, background.width):
				result.paste(background, (x, y))
	else:
		result = PIL.Image.new('RGB', (width, height), background)

	draw = PIL.ImageDraw.ImageDraw(result)
	setattr(draw, '_multiline_check', lambda _: False)
	for item in items:
		if isinstance(item, Text):
			render_text(draw, item)
		elif isinstance(item, Image):
			render_image(draw, item)

	if debug:
		for item in items:
			render_bbox_padded(draw, item)
		for item in items:
			render_bbox(draw, item)

	return result


def render_text(draw: PIL.ImageDraw.ImageDraw, text: Text) -> None:
	if text.border is None:
		draw.text(text.position, text.text, text.color, text.font)
	elif isinstance(text.font, PIL.ImageFont.FreeTypeFont):
		draw.text(
			text.position, text.text, text.color, text.font, stroke_width=1, stroke_fill=text.border
		)
	else:
		draw.text((text.position[0] - 1, text.position[1]), text.text, text.border, text.font)
		draw.text((text.position[0], text.position[1] - 1), text.text, text.border, text.font)
		draw.text((text.position[0] + 1, text.position[1]), text.text, text.border, text.font)
		draw.text((text.position[0], text.position[1] + 1), text.text, text.border, text.font)
		draw.text(text.position, text.text, text.color, text.font)


def render_image(draw: PIL.ImageDraw.ImageDraw, image: Image) -> None:
	if image.border is not None:
		draw.rectangle(
			(
				image.position[0] - 1,
				image.position[1] - 1,
				image.position[0] + image.size[0],
				image.position[1] + image.size[1],
			),
			None,
			image.border,
		)
	if image.background is not None:
		draw.rectangle(
			(
				image.position[0],
				image.position[1],
				image.position[0] + image.size[0] - 1,
				image.position[1] + image.size[1] - 1,
			),
			image.background,
		)
	if image.image is None:
		return

	src = image.image
	dst: PIL.Image.Image = getattr(draw, '_image')

	if src.size[0] > image.size[0] or src.size[1] > image.size[1]:
		srcx = (src.size[0] - image.size[0]) // 2
		srcy = (src.size[1] - image.size[1]) // 2
		src = src.crop((srcx, srcy, srcx + image.size[0], srcy + image.size[1]))

	dstx = (image.size[0] - src.size[0]) // 2
	dsty = (image.size[1] - src.size[1]) // 2

	dst.paste(src, (image.position[0] + dstx, image.position[1] + dsty))


def render_bbox_padded(draw: PIL.ImageDraw.ImageDraw, item: Item, color: Color = 'red') -> None:
	if (
		item.size[0] + item.spacing[0] + item.spacing[2] > 0
		and item.size[1] + item.spacing[1] + item.spacing[3] > 0
	):
		draw.rectangle(
			(
				item.position[0] - item.spacing[0],
				item.position[1] - item.spacing[1],
				item.position[0] + item.size[0] + item.spacing[2] - 1,
				item.position[1] + item.size[1] + item.spacing[3] - 1,
			),
			None,
			color,
		)


def render_bbox(draw: PIL.ImageDraw.ImageDraw, item: Item, color: Color = '#00ff00') -> None:
	if item.size[0] > 0 and item.size[1] > 0:
		draw.rectangle(
			(
				item.position[0],
				item.position[1],
				item.position[0] + item.size[0] - 1,
				item.position[1] + item.size[1] - 1,
			),
			None,
			color,
		)
