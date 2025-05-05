import collections.abc
import dataclasses
import enum
import math
import sys
import typing

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from .font import load as load_font
from .types import Color, Font
from .vignette import Alignment, Cell, Label, Vignette

T = typing.TypeVar('T')


class Layout(enum.Enum):
	TILED = enum.auto()
	VARIABLE = enum.auto()


@dataclasses.dataclass(eq=False, kw_only=True)
class Item:
	position: tuple[int, int] = (0, 0)
	size: tuple[int, int] = (0, 0)
	spacing: tuple[int, int, int, int] = (0, 0, 0, 0)


@dataclasses.dataclass(eq=False, kw_only=True)
class Text(Item):
	text: str
	font: typing.Optional[Font] = None
	color: Color = 'white'
	border: typing.Optional[Color] = None


@dataclasses.dataclass(eq=False, kw_only=True)
class Image(Item):
	image: typing.Optional[PIL.Image.Image] = None
	background: typing.Optional[Color] = None
	border: typing.Optional[Color] = None


def offset(item: Item, x: int, y: int) -> None:
	xx, yy = item.position
	item.position = (xx + x, yy + y)


def offset_all(items: typing.Iterable[Item], x: int, y: int) -> None:
	for item in items:
		offset(item, x, y)


def measure(items: typing.Iterable[Item], width: int = 0, height: int = 0) -> tuple[int, int]:
	for item in items:
		width = max(width, item.position[0] + item.size[0] + item.spacing[2])
		height = max(height, item.position[1] + item.size[1] + item.spacing[3])

	return width, height


def merge(
	items_first: typing.Sequence[Item],
	items_second: typing.Sequence[Item],
	spacing: typing.Optional[int] = None,
) -> list[Item]:
	result: list[Item] = []

	top_height_raw = 0
	top_height_spacing = 0
	for item in items_first:
		top_height_raw = max(top_height_raw, item.position[1] + item.size[1])
		top_height_spacing = max(
			top_height_spacing, item.position[1] + item.size[1] + item.spacing[3]
		)
		result.append(item)

	count = 0
	bottom_start_raw = sys.maxsize
	bottom_start_spacing = sys.maxsize
	for item in items_second:
		count += 1
		bottom_start_raw = min(bottom_start_raw, item.position[1])
		bottom_start_spacing = min(bottom_start_spacing, item.position[1] - item.spacing[1])
		result.append(item)

	if not count:
		return result

	top_spacing = top_height_spacing - top_height_raw
	bottom_spacing = bottom_start_raw - bottom_start_spacing
	if spacing is None:
		spacing = max(top_spacing, bottom_spacing)

	offset = top_height_raw + spacing - bottom_spacing
	offset_all(items_second, 0, offset)

	return result


def text_from_label(
	label: Label,
	*,
	spacing: tuple[int, int, int, int] = (0, 0, 0, 0),
	width: typing.Optional[int] = None,
) -> typing.Optional[Text]:
	text = label.text
	if text is None:
		return None

	font = label.font
	if font is None:
		font = load_font()

	if not isinstance(font, PIL.ImageFont.FreeTypeFont):
		text = text.encode('iso8859-1', errors='replace').decode('iso8859-1')

	bbox = font.getbbox(text)
	size = (bbox[2] - bbox[0], bbox[3])
	if width is None:
		return Text(
			position=spacing[:2],
			size=size,
			spacing=spacing,
			text=text,
			font=font,
			color=label.color,
			border=label.border,
		)

	cropped_text = text
	iteration = 0
	filler = '...'
	while size[0] > width:
		iteration += 1
		if iteration > len(text):
			return None
		if label.halignment == Alignment.MIDDLE:
			start = (len(text) - iteration) // 2
			cropped_text = text[:start] + filler + text[start + iteration :]
		elif label.halignment == Alignment.FAR:
			cropped_text = filler + text[iteration:]
		else:
			cropped_text = text[:-iteration] + filler
		bbox = font.getbbox(text)
		size = (bbox[2] - bbox[0], bbox[3])

	return Text(
		position=spacing[:2],
		size=size,
		spacing=spacing,
		text=cropped_text,
		font=font,
		color=label.color,
		border=label.border,
	)


def align_text(
	text: Text, x: int, y: int, w: int, h: int, *, halignment: Alignment, valignment: Alignment
) -> None:
	if halignment == Alignment.MIDDLE:
		x += (w - text.size[0]) // 2
	elif halignment == Alignment.FAR:
		x += w - text.size[0]
	if valignment == Alignment.MIDDLE:
		y += (h - text.size[1]) // 2
	elif valignment == Alignment.FAR:
		y += h - text.size[1]
	text.position = (x, y)


def layout_labels(
	labels: typing.Iterable[Label], *, width: int, spacing: tuple[int, int, int, int] = (0, 0, 0, 0)
) -> list[Text]:
	lines: list[list[tuple[Alignment, Alignment, Text]]] = [[]]
	last_alignment: typing.Optional[Alignment] = None
	real_width = width - spacing[0] - spacing[2]
	for label in labels:
		if last_alignment is not None and label.halignment <= last_alignment:
			last_alignment = None
			lines.append([])
		last_alignment = label.halignment
		text = text_from_label(label, spacing=spacing, width=real_width)
		if text is None:
			continue
		lines[-1].append((last_alignment, label.valignment, text))

	result: list[Text] = []
	ytop = spacing[1]
	height = 0
	for line in lines:
		ytop += height
		height = 0
		for _, _, text in line:
			height = max(height, text.size[1])
		for halignment, valignment, text in line:
			align_text(
				text,
				spacing[0],
				ytop,
				real_width,
				height,
				halignment=halignment,
				valignment=valignment,
			)
			result.append(text)

	return result


def image_from_cell(
	cell: Cell,
	*,
	size: typing.Optional[tuple[int, int]] = None,
	background: typing.Optional[Color] = None,
	border: typing.Optional[Color] = None,
	spacing: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> tuple[Image, typing.Optional[Text]]:
	if size is None:
		size = (1, 1) if cell.image is None else cell.image.size

	image = Image(
		position=spacing[:2],
		size=size,
		spacing=spacing,
		image=cell.image,
		background=background,
		border=border,
	)

	if cell.label is None:
		return image, None

	text = text_from_label(cell.label, width=image.size[0] - 2)

	if text is None:
		return image, None

	padding = (1, 1) if isinstance(text.font, PIL.ImageFont.FreeTypeFont) else (1, 0)
	align_text(
		text,
		image.position[0] + padding[0],
		image.position[1] + padding[1],
		image.size[0] - padding[0] * 2,
		image.size[1] - padding[1] * 2,
		halignment=cell.label.halignment,
		valignment=cell.label.valignment,
	)

	return image, text


def split_tiled(
	items: collections.abc.Sequence[T], chunk_size: int
) -> tuple[list[collections.abc.Sequence[T]], None]:
	return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)], None


def split_variable(
	items: typing.Iterable[T],
	measure: typing.Callable[[T], typing.Optional[int]],
	chunk_size: int,
	*,
	columns: typing.Optional[int] = None,
	spacing: tuple[int, int] = (0, 0),
) -> tuple[list[collections.abc.Sequence[T]], int]:
	if columns is None:
		columns = math.floor(math.sqrt(chunk_size))
	rows = math.ceil(chunk_size / columns)

	count = 0
	width_max = 1
	width_sum = 0

	for item in items:
		width = measure(item)
		if width is None:
			continue
		count += 1
		width_max = max(width_max, width)
		width_sum += width

	result: tuple[list[collections.abc.Sequence[T]], int] = (
		[],
		max(width_max, round(columns * width_sum / max(count, 1))),
	)
	threshold = result[1] + spacing[0]

	chunk: list[T] = []
	x = 0
	y = 0
	for item in items:
		width = measure(item)
		if width is None:
			continue
		chunk.append(item)
		x += spacing[min(x, 1)] + width
		if x >= threshold:
			x = 0
			y += 1
			if y >= rows:
				result[0].append(chunk)
				chunk = []
				y = 0

	if chunk:
		result[0].append(chunk)

	return result


def split(
	items: collections.abc.Sequence[T],
	measure: typing.Callable[[T], typing.Optional[int]],
	chunk_size: int,
	mode: Layout = Layout.TILED,
	*,
	columns: typing.Optional[int] = None,
	spacing: tuple[int, int] = (0, 0),
) -> tuple[list[collections.abc.Sequence[T]], typing.Optional[int]]:
	if mode == Layout.TILED:
		return split_tiled(items, chunk_size)
	elif mode == Layout.VARIABLE:
		return split_variable(items, measure, chunk_size, columns=columns, spacing=spacing)
	else:
		return [items], None


def layout_cells_tiled(
	cells: collections.abc.Sequence[Cell],
	columns: typing.Optional[int] = None,
	*,
	border: typing.Optional[Color] = None,
	spacing: tuple[int, int] = (0, 0),
) -> list[Item]:
	count = len(cells)
	if columns is None:
		columns = math.floor(math.sqrt(count))

	if not all(spacing):
		border = None

	cell_width = 1
	cell_height = 1
	for cell in cells:
		if cell.image is None:
			continue
		cell_width = max(cell_width, cell.image.width)
		cell_height = max(cell_height, cell.image.height)
	cell_size = (cell_width, cell_height)

	result: list[Item] = []
	item_spacing = (spacing[0], spacing[0], spacing[0], spacing[0])
	for i in range(0, count):
		image, text = image_from_cell(
			cells[i], size=cell_size, background='black', border=border, spacing=item_spacing
		)
		row, column = divmod(i, columns)
		x = column * (cell_width + spacing[1])
		y = row * (cell_height + spacing[1])
		offset(image, x, y)
		result.append(image)
		if text is not None:
			offset(text, x, y)
			result.append(text)

	return result


def layout_cells_variable(
	cells: typing.Iterable[Cell],
	width: typing.Optional[int] = None,
	*,
	border: typing.Optional[Color] = None,
	spacing: tuple[int, int] = (0, 0),
) -> list[Item]:
	total_width = 0
	cell_width = 1
	cell_height = 1
	for cell in cells:
		if cell.image is None:
			continue
		total_width += cell.image.width
		cell_width = max(cell_width, cell.image.width)
		cell_height = max(cell_height, cell.image.height)

	if width is None:
		rows = 1
		width = total_width

		while width > (cell_height * (rows + 1)):
			rows += 1
			width = total_width // rows

		width = max(cell_width, width)
		del rows

	width += spacing[0]

	if not all(spacing):
		border = None

	cell_rows: list[list[Cell]] = []
	cell_row: list[Cell] = []
	x = 0
	for cell in cells:
		if cell.image is None:
			continue
		cell_row.append(cell)
		x += spacing[min(x, 1)] + cell.image.width
		if x >= width:
			cell_rows.append(cell_row)
			cell_row = []
			x = 0

	if cell_row:
		cell_rows.append(cell_row)

	cell_width_override: dict[Cell, int] = {}
	for cell_row in cell_rows:
		x = 0
		for i, cell in enumerate(cell_row):
			if typing.TYPE_CHECKING:
				assert cell.image is not None
			x += spacing[min(x, 1)] + cell.image.width

		if x <= width:
			continue

		extra = x - width
		stops: list[float] = [0.0]
		for cell in cell_row:
			if typing.TYPE_CHECKING:
				assert cell.image is not None
			stops.append(stops[-1] + cell.image.width)

		scale = 1.0 - extra / stops[-1]
		for i in range(len(stops)):
			stops[i] *= scale

		for i, cell in enumerate(cell_row):
			cell_width_override[cell] = round(stops[i + 1]) - round(stops[i])

	result: list[Item] = []
	item_spacing = (spacing[0], spacing[0], spacing[0], spacing[0])
	y = 0
	for cell_row in cell_rows:
		x = 0
		for cell in cell_row:
			if typing.TYPE_CHECKING:
				assert cell.image is not None
			image, text = image_from_cell(
				cell,
				size=(cell_width_override.get(cell, cell.image.size[0]), cell.image.size[1]),
				background='black',
				border=border,
				spacing=item_spacing,
			)
			offset(image, x, y)
			result.append(image)
			if text is not None:
				offset(text, x, y)
				result.append(text)
			x += image.size[0] + spacing[1]
		y += cell_height + spacing[1]

	return result


def layout_cells(
	cells: collections.abc.Sequence[Cell],
	mode: Layout = Layout.TILED,
	*,
	columns: typing.Optional[int] = None,
	width: typing.Optional[int] = None,
	border: typing.Optional[Color] = None,
	spacing: tuple[int, int] = (0, 0),
) -> list[Item]:
	if mode == Layout.TILED:
		return layout_cells_tiled(cells, columns=columns, border=border, spacing=spacing)
	elif mode == Layout.VARIABLE:
		return layout_cells_variable(cells, width=width, border=border, spacing=spacing)
	else:
		return []


def layout(
	vignette: Vignette,
	*,
	mode: Layout = Layout.TILED,
	columns: typing.Optional[int] = None,
	width: typing.Optional[int] = None,
	spacing: tuple[int, int] = (0, 0),
) -> list[Item]:
	cells = layout_cells(
		vignette.cells,
		mode=mode,
		columns=columns,
		width=width,
		border=vignette.border,
		spacing=spacing,
	)

	width, _ = measure(cells)
	item_spacing = (spacing[0], spacing[0], spacing[0], spacing[0])

	headers = layout_labels(vignette.headers, width=width, spacing=item_spacing)
	footers = layout_labels(vignette.footers, width=width, spacing=item_spacing)

	part1 = merge(headers, cells, spacing[1] if headers else None)
	part2 = merge(part1, footers, spacing[1] if footers else None)

	return part2
