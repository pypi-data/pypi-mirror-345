import concurrent.futures
import dataclasses
import enum
import fnmatch
import io
import json
import os
import pathlib
import random
import subprocess
import typing

import PIL.Image

IMAGES = frozenset(['.bmp', '.gif', '.jpe', '.jpg', '.jpeg', '.png', '.webp'])
VIDEOS = frozenset(
	[
		'.3gp',
		'.asf',
		'.avi',
		'.f4v',
		'.flv',
		'.m4v',
		'.mkv',
		'.mov',
		'.mpg',
		'.mpeg',
		'.mp4',
		'.mts',
		'.ts',
		'.webm',
		'.wmv',
	]
)
OFFSET = 1.0 / 3.0
PRECISION = 3


@dataclasses.dataclass(eq=False, kw_only=True)
class Information:
	name: str
	size: typing.Optional[int] = None
	duration: typing.Optional[float] = None
	resolution: typing.Optional[tuple[int, int]] = None
	frame_rate: typing.Optional[float] = None
	video_codec: typing.Optional[str] = None
	video_rate: typing.Optional[int] = None
	audio_codec: typing.Optional[str] = None
	audio_rate: typing.Optional[int] = None


class Order(enum.Enum):
	NONE = enum.auto()
	DEFAULT = enum.auto()
	REVERSE = enum.auto()
	SHORTEST = enum.auto()
	LONGEST = enum.auto()
	RANDOM = enum.auto()


class Verbosity(enum.IntEnum):
	QUIET = -8
	PANIC = 0
	FATAL = 8
	ERROR = 16
	WARNING = 24
	INFO = 32
	VERBOSE = 40
	DEBUG = 48
	TRACE = 56


class Scale(enum.Enum):
	BOX = enum.auto()
	WIDTH = enum.auto()
	HEIGHT = enum.auto()
	OVER = enum.auto()
	CROP = enum.auto()


def is_extended_order(order: Order) -> bool:
	return order in (Order.SHORTEST, Order.LONGEST)


def extract_information(
	path: typing.Union[os.PathLike[str], str], *, verbosity: Verbosity = Verbosity.QUIET
) -> Information:
	path = os.fspath(path)
	result = Information(name=os.path.basename(path))

	try:
		result.size = os.path.getsize(path)
	except OSError:
		pass

	args = [
		'ffprobe',
		'-v',
		verbosity.name.lower(),
		'-print_format',
		'json',
		'-show_entries',
		'format=duration:stream=codec_type,codec_name,bit_rate,avg_frame_rate,width,height',
		'-i',
		path,
	]

	process = subprocess.run(
		args=args,
		stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE,
		stderr=subprocess.DEVNULL if verbosity < 0 else None,
		encoding='utf-8',
	)

	if process.returncode:
		return result

	try:
		data: object = json.loads(process.stdout)
	except json.JSONDecodeError:
		return result

	empty_dict: dict[str, object] = {}

	def ensure_dict(input: object) -> dict[str, object]:
		return input if isinstance(input, dict) else empty_dict

	empty_list: list[object] = []

	def ensure_list(input: object) -> list[object]:
		return input if isinstance(input, list) else empty_list

	T = typing.TypeVar('T', str, int, float, bool)

	def ensure_value(type: typing.Type[T], input: object) -> typing.Optional[T]:
		if not isinstance(input, (str, int, float, bool)):
			return None
		try:
			return type(input)
		except ValueError:
			return None

	def ensure_rate(input: object) -> typing.Optional[float]:
		if isinstance(input, (int, float, bool)):
			return float(input)
		elif not isinstance(input, str):
			return None

		split = input.split('/', 1)
		if len(split) == 1:
			split.append('1')
		elif len(split) != 2:
			return None

		try:
			numerator = int(split[0])
			denominator = int(split[1])
		except ValueError:
			return None

		try:
			return numerator / denominator
		except ZeroDivisionError:
			return None

	info = ensure_dict(data)
	format = ensure_dict(info.get('format'))
	streams = ensure_list(info.get('streams'))

	result.duration = ensure_value(float, format.get('duration'))

	video_stream = empty_dict
	audio_stream = empty_dict

	for stream in map(ensure_dict, streams):
		codec_type = stream.get('codec_type')
		if codec_type == 'video' and video_stream is empty_dict:
			video_stream = stream
		elif codec_type == 'audio' and audio_stream is empty_dict:
			audio_stream = stream

	width = ensure_value(int, video_stream.get('width'))
	height = ensure_value(int, video_stream.get('height'))
	if width is not None and height is not None:
		result.resolution = (width, height)

	result.frame_rate = ensure_rate(video_stream.get('avg_frame_rate'))

	result.video_codec = ensure_value(str, video_stream.get('codec_name'))
	result.video_rate = ensure_value(int, video_stream.get('bit_rate'))
	result.audio_codec = ensure_value(str, audio_stream.get('codec_name'))
	result.audio_rate = ensure_value(int, audio_stream.get('bit_rate'))

	return result


def seek_indexed(
	duration: typing.Optional[float], index: int, count: int
) -> typing.Optional[float]:
	return None if duration is None else round((index + 0.5) * (duration / count), PRECISION)


def seek_offset(duration: typing.Optional[float], offset: float = OFFSET) -> typing.Optional[float]:
	return None if duration is None else round(duration * offset, PRECISION)


def extract_frame(
	path: typing.Union[os.PathLike[str], str],
	*,
	seek: typing.Optional[float] = None,
	size: typing.Optional[int] = None,
	scale: Scale = Scale.BOX,
	verbosity: Verbosity = Verbosity.ERROR,
) -> typing.Optional[PIL.Image.Image]:
	path = os.fspath(path)

	filters: list[str] = []
	if size is not None:
		if scale == Scale.BOX:
			filters.append('scale={0}:{0}:force_original_aspect_ratio=decrease'.format(size))
		elif scale == Scale.WIDTH:
			filters.append('scale={}:-1'.format(size))
		elif scale == Scale.HEIGHT:
			filters.append('scale=-1:{}'.format(size))
		elif scale == Scale.OVER:
			filters.append('scale={0}:{0}:force_original_aspect_ratio=increase'.format(size))
		elif scale == Scale.CROP:
			filters.extend(['crop=min(iw\\,ih):min(iw\\,ih)', 'scale={}:-1'.format(size)])

	filters.extend(['format=rgb24', 'setsar=1', 'setdar=a'])

	args = [
		'ffmpeg',
		'-hide_banner',
		'-nostats',
		'-loglevel',
		verbosity.name.lower(),
		'-threads',
		'1',
		'-filter_threads',
		'1',
	]

	if seek is not None:
		args.extend(['-ss', str(seek)])

	args.extend(
		[
			'-an',
			'-sn',
			'-dn',
			'-i',
			path,
			'-map_metadata',
			'-1',
			'-filter:v',
			','.join(filters),
			'-frames:v',
			'1',
			'-codec:v',
			'ppm',
			'-f',
			'image2pipe',
			'-',
		]
	)

	process = subprocess.run(
		args,
		stdin=subprocess.DEVNULL,
		stdout=subprocess.PIPE,
		stderr=subprocess.DEVNULL if verbosity < 0 else None,
	)

	if process.returncode or not process.stdout:
		return None

	with io.BytesIO(process.stdout) as fp:
		image = PIL.Image.open(fp)
		image.load()

	return image


def extract_frames(
	path: typing.Union[os.PathLike[str], str],
	*,
	count: int,
	duration: typing.Optional[float] = None,
	size: typing.Optional[int] = None,
	scale: Scale = Scale.BOX,
	verbosity: typing.Optional[Verbosity] = None,
	executor: typing.Optional[concurrent.futures.Executor] = None,
) -> list[tuple[float, typing.Optional[PIL.Image.Image]]]:
	def callback(index: int) -> tuple[float, typing.Optional[PIL.Image.Image]]:
		seek = seek_indexed(duration, index, count)
		image = extract_frame(
			path,
			seek=seek,
			size=size,
			scale=scale,
			verbosity=Verbosity.ERROR if verbosity is None else verbosity,
		)
		return seek or 0.0, image

	if executor is None:
		return list(map(callback, range(count)))

	return list(executor.map(callback, range(count), chunksize=1))


def extract_directory_paths(
	path: typing.Union[os.PathLike[str], str],
	extensions: typing.Container[str],
	*,
	follow_symlinks: bool = False,
	ignore_patterns: typing.Optional[typing.Iterable[str]] = None,
	recurse: bool = False,
	order: Order = Order.DEFAULT,
	window: typing.Optional[slice] = None,
	randomizer: typing.Optional[random.Random] = None,
) -> list[pathlib.Path]:
	path_object = pathlib.Path(path)

	if ignore_patterns is None:
		ignore_patterns = []

	directories: list[pathlib.Path] = []
	files: list[pathlib.Path] = []

	for entry in os.scandir(path_object):
		if any(fnmatch.fnmatchcase(entry.name, pattern) for pattern in ignore_patterns):
			continue
		if recurse and entry.is_dir(follow_symlinks=follow_symlinks):
			directories.append(path_object / entry.name)
		elif (
			entry.is_file(follow_symlinks=follow_symlinks)
			and os.path.splitext(entry.name)[1].lower() in extensions
		):
			files.append(path_object / entry.name)

	for directory in directories:
		files.extend(
			extract_directory_paths(
				directory,
				extensions,
				follow_symlinks=follow_symlinks,
				ignore_patterns=ignore_patterns,
				recurse=recurse,
				order=Order.NONE,
			)
		)

	if order == Order.DEFAULT:
		files.sort(key=lambda x: (x.name.lower(), x.name))
	elif order == Order.REVERSE:
		files.sort(key=lambda x: (x.name.lower(), x.name), reverse=True)
	elif order == Order.RANDOM:
		if randomizer is None:
			random.shuffle(files)
		else:
			randomizer.shuffle(files)

	if window is not None:
		files = files[window]

	return files


def extract_directory_videos(
	path: typing.Union[os.PathLike[str], str],
	*,
	follow_symlinks: bool = False,
	ignore_patterns: typing.Optional[typing.Iterable[str]] = None,
	recurse: bool = True,
	order: Order = Order.DEFAULT,
	window: typing.Optional[slice] = None,
	offset: typing.Optional[float] = OFFSET,
	size: typing.Optional[int] = None,
	scale: Scale = Scale.BOX,
	verbosity: typing.Optional[Verbosity] = None,
	executor: typing.Optional[concurrent.futures.Executor] = None,
	randomizer: typing.Optional[random.Random] = None,
) -> list[tuple[pathlib.Path, Information, typing.Optional[PIL.Image.Image]]]:
	def callback(
		path: pathlib.Path,
	) -> tuple[pathlib.Path, Information, typing.Optional[PIL.Image.Image]]:
		info = extract_information(
			path, verbosity=Verbosity.QUIET if verbosity is None else verbosity
		)
		if offset is None:
			return path, info, None
		seek = seek_offset(info.duration, offset)
		image = extract_frame(
			path,
			seek=seek,
			size=size,
			scale=scale,
			verbosity=Verbosity.ERROR if verbosity is None else verbosity,
		)
		return path, info, image

	extended = is_extended_order(order)
	videos = extract_directory_paths(
		path,
		VIDEOS,
		follow_symlinks=follow_symlinks,
		ignore_patterns=ignore_patterns,
		recurse=recurse,
		order=Order.NONE if extended else order,
		window=None if extended else window,
		randomizer=randomizer,
	)

	if executor is None:
		result = list(map(callback, videos))
	else:
		result = list(executor.map(callback, videos, chunksize=1))

	if not extended:
		return result

	if order == Order.SHORTEST:
		result.sort(key=lambda t: (t[1].duration or 0.0, t[0].name.lower(), t[0].name))
	elif order == Order.LONGEST:
		result.sort(key=lambda t: (-(t[1].duration or 0.0), t[0].name.lower(), t[0].name))

	if window is not None:
		result = result[window]

	return result


def extract_directory_images(
	path: typing.Union[os.PathLike[str], str],
	*,
	follow_symlinks: bool = False,
	ignore_patterns: typing.Optional[typing.Iterable[str]] = None,
	recurse: bool = True,
	order: Order = Order.DEFAULT,
	window: typing.Optional[slice] = None,
	size: typing.Optional[int] = None,
	scale: Scale = Scale.BOX,
	verbosity: typing.Optional[Verbosity] = None,
	executor: typing.Optional[concurrent.futures.Executor] = None,
	randomizer: typing.Optional[random.Random] = None,
) -> list[tuple[pathlib.Path, typing.Optional[PIL.Image.Image]]]:
	def callback(path: pathlib.Path) -> tuple[pathlib.Path, typing.Optional[PIL.Image.Image]]:
		image = extract_frame(
			path,
			size=size,
			scale=scale,
			verbosity=Verbosity.ERROR if verbosity is None else verbosity,
		)
		return path, image

	images = extract_directory_paths(
		path,
		IMAGES,
		follow_symlinks=follow_symlinks,
		ignore_patterns=ignore_patterns,
		recurse=recurse,
		order=order,
		window=window,
		randomizer=randomizer,
	)

	if executor is None:
		return list(map(callback, images))

	return list(executor.map(callback, images, chunksize=1))
