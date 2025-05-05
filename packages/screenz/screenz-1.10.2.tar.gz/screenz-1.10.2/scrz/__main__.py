import argparse
import concurrent.futures
import contextlib
import dataclasses
import enum
import importlib.metadata
import os
import pathlib
import random
import sys
import types
import typing

import PIL.Image

from .extractor import (
	VIDEOS,
	Order,
	Scale,
	Verbosity,
	extract_directory_paths,
	extract_directory_videos,
	is_extended_order,
)
from .font import load as load_font
from .generator import (
	Configuration,
	Header,
	compose,
	configure_histogram,
	configure_image_collage,
	configure_video,
	configure_video_collage,
	generate_histogram,
	generate_image_collage,
	generate_video,
	generate_video_collage,
)
from .layout import Layout


class Type(enum.Enum):
	SINGLE = enum.auto()
	RECURSIVE = enum.auto()
	VIDEOS = enum.auto()
	IMAGES = enum.auto()
	HISTOGRAM = enum.auto()


@dataclasses.dataclass(eq=False, kw_only=True)
class Context(contextlib.AbstractContextManager['Context']):
	executor: typing.Optional[concurrent.futures.Executor]
	randomizer: random.Random
	type: Type
	input: pathlib.Path
	output: pathlib.Path
	follow_symlinks: bool
	ignore_patterns: list[str]
	verbosity: typing.Optional[Verbosity]
	order: Order
	window: typing.Optional[slice]
	filename_format: str
	configuration: Configuration
	debug: bool

	def __enter__(self) -> 'Context':
		return self

	def __exit__(
		self,
		exc_type: typing.Optional[typing.Type[BaseException]],
		exc_value: typing.Optional[BaseException],
		traceback: typing.Optional[types.TracebackType],
	) -> typing.Optional[bool]:
		if self.executor is not None:
			self.executor.shutdown()
		return None


def parse_slice(input: str) -> typing.Optional[slice]:
	return slice(*(int(part) if part else None for part in input.split(':')))


def create_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description='Generates screenshots from videos and images')
	parser.add_argument('input')
	parser.add_argument('output')

	parser.add_argument(
		'-V', '--version', action='version', version=importlib.metadata.version('screenz')
	)

	parser.add_argument(
		'-t',
		'--type',
		type=str,
		choices=list(map(str.lower, Type.__members__.keys())),
		help='generation type',
	)
	parser.add_argument(
		'-L',
		'--follow',
		default=False,
		action=argparse.BooleanOptionalAction,
		help='follow symbolic links when recursing',
	)
	parser.add_argument(
		'-i',
		'--ignore',
		type=str,
		nargs='*',
		help='ignore directory or file names matching this pattern when recursing',
	)
	parser.add_argument(
		'-v',
		'--verbosity',
		type=str,
		choices=list(map(str.lower, Verbosity.__members__.keys())),
		help='ffmpeg output verbosity',
	)
	parser.add_argument(
		'-b',
		'--background',
		type=str,
		help='color or image of the background (use image:PATH to specify image)',
	)
	parser.add_argument('-f', '--foreground', type=str, help='color of the foreground and borders')
	parser.add_argument(
		'-a', '--accent', type=str, help='color of the timestamps and histogram bars'
	)
	parser.add_argument('-F', '--font', type=str, help='font name')
	parser.add_argument('-z', '--font-size', type=int, help='font height')
	parser.add_argument(
		'-H',
		'--header',
		type=str,
		choices=list(map(str.lower, Header.__members__.keys())),
		help='level of information in the header',
	)
	parser.add_argument('-s', '--size', type=int, help='size of the cells')
	parser.add_argument(
		'-S',
		'--scale',
		type=str,
		choices=list(map(str.lower, Scale.__members__.keys())),
		help='how to compute the size of the cells',
	)
	parser.add_argument(
		'-l',
		'--layout',
		type=str,
		choices=list(map(str.lower, Layout.__members__.keys())),
		help='cell layout mode',
	)
	parser.add_argument('-C', '--columns', type=int, help='number of columns')
	parser.add_argument('-c', '--count', type=int, help='number of cells')
	parser.add_argument('-p', '--padding', type=int, help='padding between cells')
	parser.add_argument(
		'-o',
		'--order',
		type=str,
		choices=list(map(str.lower, Order.__members__.keys())),
		help='order of files when recursing',
	)
	parser.add_argument('-Z', '--seed', type=int, help='seed for random order')
	parser.add_argument('-w', '--window', type=parse_slice, help='create a window over the results')
	parser.add_argument('-n', '--filename', type=str, help='default image filename format')
	parser.add_argument('-T', '--threads', type=int, help='number of threads')
	parser.add_argument(
		'-d',
		'--debug',
		default=False,
		action=argparse.BooleanOptionalAction,
		help='show layout item bounds',
	)
	return parser


def configure() -> Context:
	parser = create_parser()
	options = parser.parse_args()

	type = Type.SINGLE if options.type is None else Type.__members__[options.type.upper()]
	input = os.path.normpath(os.path.abspath(options.input))
	output = os.path.normpath(os.path.abspath(options.output))

	if type == Type.SINGLE or type == Type.RECURSIVE:
		configuration = configure_video()
	elif type == Type.VIDEOS:
		configuration = configure_video_collage()
	elif type == Type.IMAGES:
		configuration = configure_image_collage()
	elif type == Type.HISTOGRAM:
		configuration = configure_histogram()
	else:
		raise ValueError('unknown type')

	follow_symlinks: bool = options.follow
	ignore_patterns: list[str] = [] if options.ignore is None else options.ignore

	verbosity: typing.Optional[Verbosity] = None
	if options.verbosity is not None:
		verbosity = Verbosity.__members__[options.verbosity.upper()]

	if options.background is not None:
		if options.background.startswith('image:'):
			configuration.background = PIL.Image.open(options.background[6:])
			configuration.background.load()
		else:
			configuration.background = options.background

	if options.foreground is not None:
		configuration.foreground = options.foreground

	if options.accent is not None:
		configuration.accent = options.accent

	if options.font is not None:
		configuration.font2 = configuration.font1 = configuration.font0 = (
			load_font(options.font)
			if options.font_size is None
			else load_font(options.font, options.font_size)
		)

	if options.header is not None:
		configuration.header = Header.__members__[options.header.upper()]

	if options.size is not None:
		configuration.size = options.size

	if options.scale is not None:
		configuration.scale = Scale.__members__[options.scale.upper()]

	if options.layout is not None:
		configuration.layout = Layout.__members__[options.layout.upper()]

	if options.columns is not None:
		configuration.columns = options.columns

	if options.count is not None:
		configuration.count = options.count

	if options.padding is not None:
		configuration.padding = (options.padding, options.padding)

	order = Order.DEFAULT
	if options.order is not None:
		order = Order.__members__[options.order.upper()]

	randomizer: random.Random
	if options.seed is not None:
		randomizer = random.Random(options.seed)
	else:
		randomizer = random.SystemRandom()

	window = options.window

	if type == Type.SINGLE:
		filename_format = '{filename}.jpg'
	elif type == Type.RECURSIVE:
		filename_format = os.path.join('{directory}', '{filename}.jpg')
	elif type == Type.VIDEOS:
		filename_format = '{name}_{index:02d}.jpg'
	elif type == Type.IMAGES:
		filename_format = '{name}_{index:02d}.jpg'
	elif type == Type.HISTOGRAM:
		filename_format = '{filename}.jpg'

	if options.filename is not None:
		filename_format = options.filename

	threads: typing.Optional[int] = options.threads
	if threads is None:
		if sys.platform == 'linux':
			threads = len(os.sched_getaffinity(0))
		else:
			threads = os.cpu_count() or 0

		threads = min(32, threads)

	debug: bool = options.debug

	return Context(
		executor=concurrent.futures.ThreadPoolExecutor(threads) if threads > 1 else None,
		randomizer=randomizer,
		type=type,
		input=pathlib.Path(input),
		output=pathlib.Path(output),
		follow_symlinks=follow_symlinks,
		ignore_patterns=ignore_patterns,
		verbosity=verbosity,
		order=order,
		window=window,
		filename_format=filename_format,
		configuration=configuration,
		debug=debug,
	)


def make_output(outputs: set[pathlib.Path], directory: pathlib.Path, filename: str) -> pathlib.Path:
	index = 0
	split: typing.Optional[tuple[str, str]] = None
	output = directory / filename

	while output in outputs:
		index += 1
		if split is None:
			split = os.path.splitext(filename)
		output = directory / '{}[{}]{}'.format(split[0], index, split[1])

	outputs.add(output)
	return output


def execute_video(context: Context) -> None:
	vignette = generate_video(
		context.configuration, context.input, verbosity=context.verbosity, executor=context.executor
	)

	image = compose(context.configuration, vignette, debug=context.debug)
	image.save(context.output)


def execute_recursive(context: Context) -> None:
	if is_extended_order(context.order):
		paths = [
			path
			for path, _, _ in extract_directory_videos(
				context.input,
				follow_symlinks=context.follow_symlinks,
				ignore_patterns=context.ignore_patterns,
				recurse=True,
				order=context.order,
				window=context.window,
				offset=None,
				verbosity=context.verbosity,
				executor=context.executor,
				randomizer=context.randomizer,
			)
		]

	else:
		paths = extract_directory_paths(
			context.input,
			VIDEOS,
			follow_symlinks=context.follow_symlinks,
			ignore_patterns=context.ignore_patterns,
			recurse=True,
			order=context.order,
			window=context.window,
			randomizer=context.randomizer,
		)

	outputs: set[pathlib.Path] = set()
	for index, input in enumerate(paths):
		relative_input = input.relative_to(context.input)
		print(os.fspath(relative_input))

		values: dict[str, object] = {
			'directory': os.fspath(relative_input.parent),
			'filename': input.stem,
			'name': input.name,
			'index': index,
			'ordinal': index + 1,
			'count': len(paths),
		}

		output = make_output(outputs, context.output, context.filename_format.format(**values))
		os.makedirs(output.parent, exist_ok=True)

		sub_context = Context(
			executor=context.executor,
			randomizer=context.randomizer,
			type=Type.SINGLE,
			input=input,
			output=output,
			follow_symlinks=context.follow_symlinks,
			ignore_patterns=context.ignore_patterns,
			verbosity=context.verbosity,
			order=context.order,
			window=None,
			filename_format=os.path.basename(context.filename_format),
			configuration=context.configuration,
			debug=context.debug,
		)

		execute_video(sub_context)


def execute_video_collage(context: Context) -> None:
	width: typing.Optional[int] = None

	def receiver(value: typing.Optional[int]) -> None:
		nonlocal width
		width = value

	vignettes = list(
		generate_video_collage(
			context.configuration,
			context.input,
			follow_symlinks=context.follow_symlinks,
			ignore_patterns=context.ignore_patterns,
			order=context.order,
			window=context.window,
			receiver=receiver,
			verbosity=context.verbosity,
			executor=context.executor,
			randomizer=context.randomizer,
		)
	)

	outputs: set[pathlib.Path] = set()
	for index, vignette in enumerate(vignettes):
		values: dict[str, object] = {
			'directory': '',
			'filename': '',
			'name': context.input.name,
			'index': index,
			'ordinal': index + 1,
			'count': len(vignettes),
		}

		output = make_output(outputs, context.output, context.filename_format.format(**values))
		os.makedirs(output.parent, exist_ok=True)

		image = compose(context.configuration, vignette, width=width, debug=context.debug)
		image.save(output)

		del image


def execute_image_collage(context: Context) -> None:
	width: typing.Optional[int] = None

	def receiver(value: typing.Optional[int]) -> None:
		nonlocal width
		width = value

	vignettes = list(
		generate_image_collage(
			context.configuration,
			context.input,
			follow_symlinks=context.follow_symlinks,
			ignore_patterns=context.ignore_patterns,
			order=context.order,
			window=context.window,
			receiver=receiver,
			verbosity=context.verbosity,
			executor=context.executor,
			randomizer=context.randomizer,
		)
	)

	outputs: set[pathlib.Path] = set()
	for index, vignette in enumerate(vignettes):
		values: dict[str, object] = {
			'directory': '',
			'filename': '',
			'name': context.input.name,
			'index': index,
			'ordinal': index + 1,
			'count': len(vignettes),
		}

		output = make_output(outputs, context.output, context.filename_format.format(**values))
		os.makedirs(output.parent, exist_ok=True)

		image = compose(context.configuration, vignette, width=width, debug=context.debug)
		image.save(output)

		del image


def execute_histogram(context: Context) -> None:
	vignette = generate_histogram(
		context.configuration,
		context.input,
		follow_symlinks=context.follow_symlinks,
		ignore_patterns=context.ignore_patterns,
		order=context.order,
		window=context.window,
		verbosity=context.verbosity,
		executor=context.executor,
		randomizer=context.randomizer,
	)

	image = compose(context.configuration, vignette, debug=context.debug)
	image.save(context.output)


def main() -> None:
	with configure() as context:
		if context.type == Type.SINGLE:
			execute_video(context)
		elif context.type == Type.RECURSIVE:
			execute_recursive(context)
		elif context.type == Type.VIDEOS:
			execute_video_collage(context)
		elif context.type == Type.IMAGES:
			execute_image_collage(context)
		elif context.type == Type.HISTOGRAM:
			execute_histogram(context)


if __name__ == '__main__':
	main()
