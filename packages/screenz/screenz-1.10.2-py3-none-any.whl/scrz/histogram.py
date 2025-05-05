import dataclasses
import statistics
import typing

import PIL.Image
import PIL.ImageDraw

from .extractor import Information
from .types import Color


@dataclasses.dataclass(eq=False, kw_only=True)
class Distribution:
	values: list[float] = dataclasses.field(default_factory=list)
	minimum: float = 0.0
	maximum: float = 0.0
	range: float = 0.0
	average: float = 0.0
	median: float = 0.0
	stddev: float = 0.0


def extract_distribution(informations: typing.Iterable[Information]) -> Distribution:
	values = sorted(
		information.duration for information in informations if information.duration is not None
	)
	if not values:
		return Distribution()

	minimum = min(values)
	maximum = max(values)

	return Distribution(
		values=values,
		minimum=minimum,
		maximum=maximum,
		range=maximum - minimum,
		average=statistics.mean(values),
		median=statistics.median(values),
		stddev=statistics.stdev(values) if len(values) > 1 else 0.0,
	)


def trim_distribution(distribution: Distribution, deviation: float = 2.0) -> Distribution:
	deviation *= distribution.stddev
	minimum = max(distribution.average - deviation, distribution.minimum)
	maximum = min(distribution.average + deviation, distribution.maximum)
	values = [value for value in distribution.values if value >= minimum and value <= maximum]

	return Distribution(
		values=values,
		minimum=minimum,
		maximum=maximum,
		range=maximum - minimum,
		average=distribution.average,
		median=distribution.median,
		stddev=distribution.stddev,
	)


def extract_bands(distribution: Distribution, count: int) -> list[int]:
	if distribution.range <= 0:
		return [len(distribution.values)] * count

	width = distribution.range / count
	bands = [0] * count

	for value in distribution.values:
		index = int((value - distribution.minimum) / width)
		if index < 0:
			index = 0
		elif index >= count:
			index = count - 1
		bands[index] += 1

	return bands


def render_histogram(
	bands: list[int],
	*,
	width: int,
	height: int,
	background: Color = 'black',
	axis: Color = 'white',
	bar_color: Color = '#00ff00',
	bar_width: int = 8,
	spacing: int = 2,
) -> PIL.Image.Image:
	image = PIL.Image.new('RGB', (width, height), background)
	draw = PIL.ImageDraw.ImageDraw(image)

	draw.line((0, 0, 0, height - 1), axis)
	draw.line((0, height - 1, width - 1, height - 1), axis)

	bar_height = height - spacing - 2
	if bar_height <= 0:
		return image

	peak = max(bands)
	if peak <= 0:
		return image

	for index, band in enumerate(bands):
		if not band:
			continue

		x1 = bar_width * index + spacing * (index + 1) + 1
		x2 = x1 + bar_width - 1

		h = round(band * bar_height / peak)
		y2 = height - spacing - 2
		y1 = y2 - h

		draw.rectangle((x1, y1, x2, y2), bar_color)

	return image
