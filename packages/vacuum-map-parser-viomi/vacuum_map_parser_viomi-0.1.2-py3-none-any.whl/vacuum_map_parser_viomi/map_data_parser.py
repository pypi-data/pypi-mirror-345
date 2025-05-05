"""Viomi map parser."""

import logging
import math
import zlib
from typing import Any

from vacuum_map_parser_base.config.color import ColorsPalette
from vacuum_map_parser_base.config.drawable import Drawable
from vacuum_map_parser_base.config.image_config import ImageConfig
from vacuum_map_parser_base.config.size import Sizes
from vacuum_map_parser_base.config.text import Text
from vacuum_map_parser_base.map_data import Area, ImageData, MapData, Path, Point, Room, Wall, Zone
from vacuum_map_parser_base.map_data_parser import MapDataParser

from .image_parser import ViomiImageParser
from .parsing_buffer import ParsingBuffer

_LOGGER = logging.getLogger(__name__)


class ViomiMapDataParser(MapDataParser):
    """Viomi map parser."""

    FEATURE_ROBOT_STATUS = 0x00000001
    FEATURE_IMAGE = 0x00000002
    FEATURE_HISTORY = 0x00000004
    FEATURE_CHARGE_STATION = 0x00000008
    FEATURE_RESTRICTED_AREAS = 0x00000010
    FEATURE_CLEANING_AREAS = 0x00000020
    FEATURE_NAVIGATE = 0x00000040
    FEATURE_REALTIME = 0x00000080
    FEATURE_ROOMS = 0x00001000

    POSITION_UNKNOWN = 1100

    def __init__( # pylint: disable=R0917
        self,
        palette: ColorsPalette,
        sizes: Sizes,
        drawables: list[Drawable],
        image_config: ImageConfig,
        texts: list[Text],
    ):
        super().__init__(palette, sizes, drawables, image_config, texts)
        self._image_parser = ViomiImageParser(palette, image_config, drawables)

    def unpack_map(self, raw_encoded: bytes, *args: Any, **kwargs: Any) -> bytes:
        return zlib.decompress(raw_encoded)

    def parse(self, raw: bytes, *args: Any, **kwargs: Any) -> MapData:
        map_data = MapData(0, 1)
        buf = ParsingBuffer("header", raw, 0, len(raw))
        feature_flags = buf.get_uint32("feature_flags")
        map_id = buf.peek_uint32("map_id")
        _LOGGER.debug("feature_flags: 0x%x, map_id: %d", feature_flags, map_id)

        if feature_flags & ViomiMapDataParser.FEATURE_ROBOT_STATUS != 0:
            ViomiMapDataParser._parse_section(buf, "robot_status", map_id)
            buf.skip("unknown1", 0x28)

        if feature_flags & ViomiMapDataParser.FEATURE_IMAGE != 0:
            ViomiMapDataParser._parse_section(buf, "image", map_id)
            map_data.image, map_data.rooms, map_data.cleaned_rooms = self._parse_image(buf)

        if feature_flags & ViomiMapDataParser.FEATURE_HISTORY != 0:
            ViomiMapDataParser._parse_section(buf, "history", map_id)
            map_data.path = ViomiMapDataParser._parse_history(buf)

        if feature_flags & ViomiMapDataParser.FEATURE_CHARGE_STATION != 0:
            ViomiMapDataParser._parse_section(buf, "charge_station", map_id)
            map_data.charger = ViomiMapDataParser._parse_position(buf, "pos", with_angle=True)
            _LOGGER.debug("pos: %s", map_data.charger)

        if feature_flags & ViomiMapDataParser.FEATURE_RESTRICTED_AREAS != 0:
            ViomiMapDataParser._parse_section(buf, "restricted_areas", map_id)
            map_data.walls, map_data.no_go_areas = ViomiMapDataParser._parse_restricted_areas(buf)

        if feature_flags & ViomiMapDataParser.FEATURE_CLEANING_AREAS != 0:
            ViomiMapDataParser._parse_section(buf, "cleaning_areas", map_id)
            map_data.zones = ViomiMapDataParser._parse_cleaning_areas(buf)

        if feature_flags & ViomiMapDataParser.FEATURE_NAVIGATE != 0:
            ViomiMapDataParser._parse_section(buf, "navigate", map_id)
            buf.skip("unknown1", 4)
            map_data.goto = ViomiMapDataParser._parse_position(buf, "pos")
            value = buf.get_float32("value")
            _LOGGER.debug("pos: %s, value: %f", map_data.goto, value)

        if feature_flags & ViomiMapDataParser.FEATURE_REALTIME != 0:
            ViomiMapDataParser._parse_section(buf, "realtime", map_id)
            buf.skip("unknown1", 5)
            map_data.vacuum_position = ViomiMapDataParser._parse_position(buf, "pos", with_angle=True)
            _LOGGER.debug("pos: %s", map_data.vacuum_position)

        if feature_flags & 0x00000800 != 0:
            ViomiMapDataParser._parse_section(buf, "unknown1", map_id)
            ViomiMapDataParser._parse_unknown_section(buf)

        if feature_flags & ViomiMapDataParser.FEATURE_ROOMS != 0 and map_data.rooms is not None:
            ViomiMapDataParser._parse_section(buf, "rooms", map_id)
            ViomiMapDataParser._parse_rooms(buf, map_data.rooms)

        if feature_flags & 0x00002000 != 0:
            ViomiMapDataParser._parse_section(buf, "unknown2", map_id)
            ViomiMapDataParser._parse_unknown_section(buf)

        if feature_flags & 0x00004000 != 0:
            ViomiMapDataParser._parse_section(buf, "room_outlines", map_id)
            ViomiMapDataParser._parse_room_outlines(buf)

        buf.check_empty()

        if map_data.rooms is not None:
            _LOGGER.debug("rooms: %s", [str(room) for number, room in map_data.rooms.items()])
        if map_data.image is not None and not map_data.image.is_empty:
            self._image_generator.draw_map(map_data)
            if map_data.rooms is not None and len(map_data.rooms) > 0 and map_data.vacuum_position is not None:
                vacuum_position_on_image = ViomiMapDataParser._map_to_image(map_data.vacuum_position)
                map_data.vacuum_room = ViomiImageParser.get_current_vacuum_room(buf, vacuum_position_on_image)
                if map_data.vacuum_room is not None:
                    map_data.vacuum_room_name = map_data.rooms[map_data.vacuum_room].name
                _LOGGER.debug("current vacuum room: %s", map_data.vacuum_room)
        return map_data

    @staticmethod
    def _map_to_image(p: Point) -> Point:
        return Point(p.x * 20 + 400, p.y * 20 + 400)

    @staticmethod
    def _image_to_map(x: float) -> float:
        return (x - 400) / 20

    def _parse_image(self, buf: ParsingBuffer) -> tuple[ImageData, dict[int, Room], set[int]]:
        buf.skip("unknown1", 0x08)
        image_top = 0
        image_left = 0
        image_height = buf.get_uint32("image_height")
        image_width = buf.get_uint32("image_width")
        buf.skip("unknown2", 20)
        image_size = image_height * image_width
        _LOGGER.debug("width: %d, height: %d", image_width, image_height)
        buf.mark_as_image_beginning()
        image, rooms_raw, cleaned_areas, cleaned_areas_layer = self._image_parser.parse(buf, image_width, image_height)
        if image is None:
            image = self._image_generator.create_empty_map_image()
        _LOGGER.debug("img: number of rooms: %d, numbers: %s", len(rooms_raw), rooms_raw.keys())
        rooms = {}
        for number, room in rooms_raw.items():
            rooms[number] = Room(
                ViomiMapDataParser._image_to_map(room[0] + image_left),
                ViomiMapDataParser._image_to_map(room[1] + image_top),
                ViomiMapDataParser._image_to_map(room[2] + image_left),
                ViomiMapDataParser._image_to_map(room[3] + image_top),
                number,
            )
        return (
            ImageData(
                image_size,
                image_top,
                image_left,
                image_height,
                image_width,
                self._image_config,
                image,
                ViomiMapDataParser._map_to_image,
                additional_layers={Drawable.CLEANED_AREA: cleaned_areas_layer},
            ),
            rooms,
            cleaned_areas,
        )

    @staticmethod
    def _parse_history(buf: ParsingBuffer) -> Path:
        path_points = []
        buf.skip("unknown1", 4)
        history_count = buf.get_uint32("history_count")
        for _ in range(history_count):
            buf.get_uint8("mode")  # 0: taxi, 1: working
            position = ViomiMapDataParser._parse_position(buf, "path")
            if position is not None:
                path_points.append(position)
        return Path(len(path_points), 1, 0, [path_points])

    @staticmethod
    def _parse_restricted_areas(buf: ParsingBuffer) -> tuple[list[Wall], list[Area]]:
        walls = []
        areas = []
        buf.skip("unknown1", 4)
        area_count = buf.get_uint32("area_count")
        for _ in range(area_count):
            buf.skip("restricted.unknown1", 12)
            p1 = ViomiMapDataParser._parse_position(buf, "p1")
            p2 = ViomiMapDataParser._parse_position(buf, "p2")
            p3 = ViomiMapDataParser._parse_position(buf, "p3")
            p4 = ViomiMapDataParser._parse_position(buf, "p4")
            buf.skip("restricted.unknown2", 48)
            _LOGGER.debug("restricted: %s %s %s %s", p1, p2, p3, p4)
            if p1 is not None and p2 is not None and p3 is not None and p4 is not None:
                if p1 == p2 and p3 == p4:
                    walls.append(Wall(p1.x, p1.y, p3.x, p3.y))
                else:
                    areas.append(Area(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y))
        return walls, areas

    @staticmethod
    def _parse_cleaning_areas(buf: ParsingBuffer) -> list[Zone]:
        buf.skip("unknown1", 4)
        area_count = buf.get_uint32("area_count")
        zones = []
        for _ in range(area_count):
            buf.skip("area.unknown1", 12)
            p1 = ViomiMapDataParser._parse_position(buf, "p1")
            ViomiMapDataParser._parse_position(buf, "p2")
            p3 = ViomiMapDataParser._parse_position(buf, "p3")
            ViomiMapDataParser._parse_position(buf, "p4")
            buf.skip("area.unknown2", 48)
            if p1 is not None and p3 is not None:
                zones.append(Zone(p1.x, p1.y, p3.x, p3.y))
        return zones

    @staticmethod
    def _parse_rooms(buf: ParsingBuffer, map_data_rooms: dict[int, Room]) -> None:
        map_name = buf.get_string_len8("map_name")
        map_arg = buf.get_uint32("map_arg")
        _LOGGER.debug("map#%d: %s", map_arg, map_name)
        while map_arg > 1:
            map_name = buf.get_string_len8("map_name")
            map_arg = buf.get_uint32("map_arg")
            _LOGGER.debug("map#%d: %s", map_arg, map_name)
        room_count = buf.get_uint32("room_count")
        for _ in range(room_count):
            room_id = buf.get_uint8("room.id")
            room_name = buf.get_string_len8("room.name")
            if map_data_rooms is not None and room_id in map_data_rooms:
                map_data_rooms[room_id].name = room_name
            buf.skip("room.unknown1", 1)
            room_text_pos = ViomiMapDataParser._parse_position(buf, "room.text_pos")
            _LOGGER.debug("room#%d: %s %s", room_id, room_name, room_text_pos)
        buf.skip("unknown1", 6)

    @staticmethod
    def _parse_room_outlines(buf: ParsingBuffer) -> None:
        buf.skip("unknown1", 51)
        room_count = buf.get_uint32("room_count")
        for _ in range(room_count):
            room_id = buf.get_uint32("room.id")
            segment_count = buf.get_uint32("room.segment_count")
            for _ in range(segment_count):
                buf.skip("unknown2", 5)
            _LOGGER.debug("room#%d: segment_count: %d", room_id, segment_count)

    @staticmethod
    def _parse_section(buf: ParsingBuffer, name: str, map_id: int) -> None:
        buf.set_name(name)
        magic = buf.get_uint32("magic")
        if magic != map_id:
            raise ValueError(
                f"error parsing section {name} at offset {buf.offs - 4:#x}: magic check failed. "
                + f"Magic: {magic:#x}, Map ID: {map_id:#x}"
            )

    @staticmethod
    def _parse_position(buf: ParsingBuffer, name: str, with_angle: bool = False) -> Point | None:
        x = buf.get_float32(name + ".x")
        y = buf.get_float32(name + ".y")
        if ViomiMapDataParser.POSITION_UNKNOWN in (x, y):
            return None
        a = None
        if with_angle:
            a = buf.get_float32(name + ".a") * 180 / math.pi
        return Point(x, y, a)

    @staticmethod
    def _parse_unknown_section(buf: ParsingBuffer) -> bool:
        n = buf.data[buf.offs :].find(buf.data[4:8])
        if n >= 0:
            buf.offs += n
            buf.length -= n
            return True
        buf.offs += buf.length
        buf.length = 0
        return False
