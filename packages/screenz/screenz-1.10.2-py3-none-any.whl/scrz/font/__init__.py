import functools
import importlib.resources
import os
import typing

import PIL.Image
import PIL.ImageFont

from ..types import Font

ROOT = importlib.resources.files(__package__)


@functools.cache
def load_builtin(name: str) -> PIL.ImageFont.ImageFont:
	image_resource = ROOT / '{}.png'.format(name)
	with image_resource.open('rb') as fp:
		image = PIL.Image.open(fp)
		image.load()

	font_resource = ROOT / '{}.pil'.format(name)
	with font_resource.open('rb') as fp:
		font = PIL.ImageFont.ImageFont()
		font.file = os.fspath(image_resource) if isinstance(image_resource, os.PathLike) else ''  # type: ignore[attr-defined]
		font._load_pilfont_data(fp, image)  # type: ignore[attr-defined]

	return font


@functools.cache
def has_builtin(name: str) -> bool:
	font_resource = ROOT / '{}.pil'.format(name)
	return font_resource.is_file()


@functools.cache
def load(identifier: typing.Optional[str] = None, size: int = 13) -> Font:
	if identifier is None:
		return PIL.ImageFont.load_default()

	if '/' not in identifier and '\\' not in identifier and has_builtin(identifier):
		return load_builtin(identifier)

	return PIL.ImageFont.truetype(identifier, size)
