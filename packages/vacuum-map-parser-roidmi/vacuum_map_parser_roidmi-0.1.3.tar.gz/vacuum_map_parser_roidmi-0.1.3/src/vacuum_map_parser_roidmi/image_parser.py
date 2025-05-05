"""Roidmi map image parser."""

import logging

from PIL import Image
from PIL.Image import Image as ImageType
from PIL.Image import Resampling
from vacuum_map_parser_base.config.color import ColorsPalette, SupportedColor
from vacuum_map_parser_base.config.image_config import ImageConfig

_LOGGER = logging.getLogger(__name__)


class RoidmiImageParser:
    """Roidmi map image parser."""

    MAP_WALL = 0
    MAP_OUTSIDE = 127
    MAP_UNKNOWN = 255

    def __init__(self, palette: ColorsPalette, image_config: ImageConfig):
        self._palette = palette
        self._image_config = image_config

    def parse(
        self, raw_data: bytes, width: int, height: int, room_numbers: list[int]
    ) -> tuple[ImageType | None, dict[int, tuple[int, int, int, int]]]:
        rooms: dict[int, tuple[int, int, int, int]] = {}
        scale = self._image_config.scale
        trim_left = int(self._image_config.trim.left * width / 100)
        trim_right = int(self._image_config.trim.right * width / 100)
        trim_top = int(self._image_config.trim.top * height / 100)
        trim_bottom = int(self._image_config.trim.bottom * height / 100)
        trimmed_height = height - trim_top - trim_bottom
        trimmed_width = width - trim_left - trim_right
        if trimmed_width == 0 or trimmed_height == 0:
            return None, rooms
        image = Image.new("RGBA", (trimmed_width, trimmed_height))
        pixels = image.load()
        unknown_pixels = set()
        for img_y in range(trimmed_height):
            for img_x in range(trimmed_width):
                pixel_type = raw_data[img_x + trim_left + width * (img_y + trim_bottom)]
                x = img_x
                y = trimmed_height - 1 - img_y
                if pixel_type == RoidmiImageParser.MAP_OUTSIDE:
                    pixels[x, y] = self._palette.get_color(SupportedColor.MAP_OUTSIDE)
                elif pixel_type == RoidmiImageParser.MAP_WALL:
                    pixels[x, y] = self._palette.get_color(SupportedColor.MAP_WALL_V2)
                elif pixel_type == RoidmiImageParser.MAP_UNKNOWN:
                    pixels[x, y] = self._palette.get_color(SupportedColor.UNKNOWN)
                elif pixel_type in room_numbers:
                    room_x = img_x + trim_left
                    room_y = img_y + trim_bottom
                    room_number = pixel_type
                    if room_number not in rooms:
                        rooms[room_number] = (room_x, room_y, room_x, room_y)
                    else:
                        rooms[room_number] = (
                            min(rooms[room_number][0], room_x),
                            min(rooms[room_number][1], room_y),
                            max(rooms[room_number][2], room_x),
                            max(rooms[room_number][3], room_y),
                        )
                    pixels[x, y] = self._palette.get_room_color(room_number)
                else:
                    pixels[x, y] = self._palette.get_color(SupportedColor.UNKNOWN)
                    unknown_pixels.add(pixel_type)
        if self._image_config.trim != 1 and trimmed_width != 0 and trimmed_height != 0:
            image = image.resize((int(trimmed_width * scale), int(trimmed_height * scale)), resample=Resampling.NEAREST)
        if len(unknown_pixels) > 0:
            _LOGGER.warning("unknown pixel_types: %s", unknown_pixels)
        return image, rooms
