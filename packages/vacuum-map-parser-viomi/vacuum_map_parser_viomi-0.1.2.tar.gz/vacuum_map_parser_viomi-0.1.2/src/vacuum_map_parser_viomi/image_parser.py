"""Viomi map image parser."""

import logging

from PIL import Image
from PIL.Image import Image as ImageType
from PIL.Image import Resampling
from vacuum_map_parser_base.config.color import ColorsPalette, SupportedColor
from vacuum_map_parser_base.config.drawable import Drawable
from vacuum_map_parser_base.config.image_config import ImageConfig
from vacuum_map_parser_base.map_data import Point

from .parsing_buffer import ParsingBuffer

_LOGGER = logging.getLogger(__name__)


class ViomiImageParser:
    """Viomi map image parser."""

    MAP_OUTSIDE = 0x00
    MAP_WALL = 0xFF
    MAP_SCAN = 0x01
    MAP_NEW_DISCOVERED_AREA = 0x02
    MAP_ROOM_MIN = 10
    MAP_ROOM_MAX = 59
    MAP_SELECTED_ROOM_MIN = 60
    MAP_SELECTED_ROOM_MAX = 109

    def __init__(self, palette: ColorsPalette, image_config: ImageConfig, drawables: list[Drawable]):
        self._palette = palette
        self._image_config = image_config
        self._drawables = drawables

    def parse(
        self, buf: ParsingBuffer, width: int, height: int
    ) -> tuple[ImageType | None, dict[int, tuple[int, int, int, int]], set[int], ImageType | None]:
        rooms = {}
        cleaned_areas = set()
        scale = self._image_config.scale
        trim_left = int(self._image_config.trim.left * width / 100)
        trim_right = int(self._image_config.trim.right * width / 100)
        trim_top = int(self._image_config.trim.top * height / 100)
        trim_bottom = int(self._image_config.trim.bottom * height / 100)
        trimmed_height = height - trim_top - trim_bottom
        trimmed_width = width - trim_left - trim_right
        if trimmed_width == 0 or trimmed_height == 0:
            return None, {}, set(), None
        image = Image.new("RGBA", (trimmed_width, trimmed_height))
        pixels = image.load()
        cleaned_areas_layer = None
        cleaned_areas_pixels = None
        draw_cleaned_area = Drawable.CLEANED_AREA in self._drawables
        if draw_cleaned_area:
            cleaned_areas_layer = Image.new("RGBA", (trimmed_width, trimmed_height))
            cleaned_areas_pixels = cleaned_areas_layer.load()
        buf.skip("trim_bottom", trim_bottom * width)
        unknown_pixels = set()
        for img_y in range(trimmed_height):
            buf.skip("trim_left", trim_left)
            for img_x in range(trimmed_width):
                pixel_type = buf.get_uint8("pixel")
                x = img_x
                y = trimmed_height - 1 - img_y
                if pixel_type == ViomiImageParser.MAP_OUTSIDE:
                    pixels[x, y] = self._palette.get_color(SupportedColor.MAP_OUTSIDE)
                elif pixel_type == ViomiImageParser.MAP_WALL:
                    pixels[x, y] = self._palette.get_color(SupportedColor.MAP_WALL_V2)
                elif pixel_type == ViomiImageParser.MAP_SCAN:
                    pixels[x, y] = self._palette.get_color(SupportedColor.SCAN)
                elif pixel_type == ViomiImageParser.MAP_NEW_DISCOVERED_AREA:
                    pixels[x, y] = self._palette.get_color(SupportedColor.NEW_DISCOVERED_AREA)
                elif ViomiImageParser.MAP_ROOM_MIN <= pixel_type <= ViomiImageParser.MAP_SELECTED_ROOM_MAX:
                    room_x = img_x + trim_left
                    room_y = img_y + trim_bottom
                    if pixel_type < self.MAP_SELECTED_ROOM_MIN:
                        room_number = pixel_type
                    else:
                        room_number = pixel_type - self.MAP_SELECTED_ROOM_MIN + self.MAP_ROOM_MIN
                        cleaned_areas.add(room_number)
                        if draw_cleaned_area and cleaned_areas_pixels is not None:
                            cleaned_areas_pixels[x, y] = self._palette.get_color(SupportedColor.CLEANED_AREA)
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
            buf.skip("trim_right", trim_right)
        buf.skip("trim_top", trim_top * width)
        if self._image_config.scale != 1 and trimmed_width != 0 and trimmed_height != 0:
            image = image.resize((int(trimmed_width * scale), int(trimmed_height * scale)), resample=Resampling.NEAREST)
            if draw_cleaned_area and cleaned_areas_layer is not None:
                cleaned_areas_layer = cleaned_areas_layer.resize(
                    (int(trimmed_width * scale), int(trimmed_height * scale)), resample=Resampling.NEAREST
                )
        if len(unknown_pixels) > 0:
            _LOGGER.warning("unknown pixel_types: %s", unknown_pixels)
        return image, rooms, cleaned_areas, cleaned_areas_layer

    @staticmethod
    def get_current_vacuum_room(buf: ParsingBuffer, vacuum_position_on_image: Point) -> int | None:
        pixel_type = buf.get_at_image(int(vacuum_position_on_image.y) * 800 + int(vacuum_position_on_image.x))
        if ViomiImageParser.MAP_ROOM_MIN <= pixel_type <= ViomiImageParser.MAP_ROOM_MAX:
            return pixel_type
        if ViomiImageParser.MAP_SELECTED_ROOM_MIN <= pixel_type <= ViomiImageParser.MAP_SELECTED_ROOM_MAX:
            return pixel_type - ViomiImageParser.MAP_SELECTED_ROOM_MIN + ViomiImageParser.MAP_ROOM_MIN
        return None
