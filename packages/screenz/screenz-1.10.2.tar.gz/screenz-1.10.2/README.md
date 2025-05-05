# ScreenZ

## Installation

Requires Python 3.13 and [FFmpeg](https://ffmpeg.org/download.html).

Install using `pip install --user screenz`.

Make sure `PATH` is properly set. In particular, `ffmpeg` and `ffprobe` must be in the `PATH` for the tool to function.

## Usage

Generate screens for a single video:

```
screenz video.mp4 output.jpg
```

Generate screens for all videos:

```
screenz --type recursive Videos Screens
```

Generate a collage of all videos:

```
screenz --type videos Videos Collage
```

Generate a collage from all images:

```
screenz --type images Videos Collage
```

Generate an histogram of video length distributions:

```
screenz --type histogram Videos histogram.png
```

## Advanced

Colors can be configured using the `--background`, `--foreground` and `--accent` options. They take colors in the `#rrggbb` format, or any [color name](https://pillow.readthedocs.io/en/stable/reference/ImageColor.html#color-names) supported by Pillow.

The background can also be a tiled image instead of a solid color by by prefixing the image path with `image:` as a value to the `--background` option.

Font can be changed using the `--font` option. It takes the name of a built-in font, or the path to a `.ttf` or `.otf` file. In this case, the `--font-size` is used to specify the pixel size.

The built-in fonts are: `6x12b`, `6x12n`, `8x14b`, `8x14n`, `8x16b`, `8x16n`, `10x18b`, `10x18n`, `10x20b`, `10x20n`, `11x22b`, `11x22n`, `12x24b`, `12x24n`, `14x28b`, `14x28n`, `16x32b` and `16x32n`.

The number of cells is controlled with `--count`, and their size with `--size`. Cells may be bigger or smaller than the requested size to account for aspect ratio, depending on the value of the `--scale` option. The defaults are adjusted to be compliant with the upload rules on a specific site.

## Reference

Use `screenz --help` to see the full documentation on options.
