"""Roidmi map parser."""

import gzip
import json
import logging
import math
from typing import Any, Callable

from vacuum_map_parser_base.config.color import ColorsPalette
from vacuum_map_parser_base.config.drawable import Drawable
from vacuum_map_parser_base.config.image_config import ImageConfig
from vacuum_map_parser_base.config.size import Sizes
from vacuum_map_parser_base.config.text import Text
from vacuum_map_parser_base.map_data import Area, ImageData, MapData, Path, Point, Room, Wall
from vacuum_map_parser_base.map_data_parser import MapDataParser

from .image_parser import RoidmiImageParser

_LOGGER = logging.getLogger(__name__)


class RoidmiMapDataParser(MapDataParser):
    """Roidmi map parser."""

    def __init__( # pylint: disable=R0917
        self,
        palette: ColorsPalette,
        sizes: Sizes,
        drawables: list[Drawable],
        image_config: ImageConfig,
        texts: list[Text],
    ):
        super().__init__(palette, sizes, drawables, image_config, texts)
        self._image_parser = RoidmiImageParser(palette, image_config)

    def unpack_map(self, raw_encoded: bytes, *args: Any, **kwargs: Any) -> bytes:
        return gzip.decompress(raw_encoded)

    def parse(self, raw: bytes, *args: Any, **kwargs: Any) -> MapData:
        map_image_size = raw.find(bytes([127, 123]))
        map_image = raw[16 : map_image_size + 1]
        map_info_raw = raw[map_image_size + 1 :]
        map_info = json.loads(map_info_raw)
        width = map_info["width"]
        height = map_info["height"]
        map_data = MapData(0, 1000)
        image, rooms = self._parse_image(map_image, width, height, map_info)
        map_data.image = image
        map_data.rooms = rooms
        map_data.path = RoidmiMapDataParser._parse_path(map_info)
        map_data.vacuum_position = RoidmiMapDataParser._parse_vacuum_position(map_info)
        map_data.charger = RoidmiMapDataParser._parse_charger_position(map_info)
        map_data.no_go_areas, map_data.no_mopping_areas, map_data.walls = RoidmiMapDataParser._parse_areas(map_info)
        if map_data.image is not None and not map_data.image.is_empty:
            self._image_generator.draw_map(map_data)
            if len(map_data.rooms) > 0 and map_data.vacuum_position is not None:
                map_data.vacuum_room = RoidmiMapDataParser._get_current_vacuum_room(map_image, map_data, width)
                if map_data.vacuum_room is not None:
                    map_data.vacuum_room_name = map_data.rooms[map_data.vacuum_room].name
        return map_data

    @staticmethod
    def _get_current_vacuum_room(map_image: bytes, map_data: MapData, original_width: int) -> int | None:
        if map_data.image is None or map_data.vacuum_position is None or map_data.rooms is None:
            return None
        p = map_data.image.dimensions.img_transformation(map_data.vacuum_position)
        room_number = map_image[int(p.x) + int(p.y) * original_width]
        if room_number in map_data.rooms:
            return room_number
        return None

    @staticmethod
    def _map_to_image(p: Point, resolution: float, min_x: float, min_y: float) -> Point:
        return Point(p.x / 1000 / resolution - min_x, p.y / 1000 / resolution - min_y)

    @staticmethod
    def _image_to_map(p: Point, resolution: float, min_x: float, min_y: float) -> Point:
        return Point((p.x + min_x) * resolution * 1000, (p.y + min_y) * resolution * 1000)

    def _parse_image(
        self, map_image: bytes, width: int, height: int, map_info: dict[str, Any]
    ) -> tuple[ImageData, dict[int, Room]]:
        resolution: float = map_info["resolution"]
        min_x: float = map_info["x_min"] / resolution
        min_y: float = map_info["y_min"] / resolution
        image_top = 0
        image_left = 0
        room_numbers = self._get_room_numbers(map_info)
        image, rooms_raw = self._image_parser.parse(map_image, width, height, room_numbers)
        if image is None:
            image = self._image_generator.create_empty_map_image()

        def points_converter(x: int, y: int) -> Point:
            return self._image_to_map(Point(x + image_left, y + image_top), resolution, min_x, min_y)

        rooms = self._parse_rooms(map_info, rooms_raw, points_converter)
        return (
            ImageData(
                width * height,
                image_top,
                image_left,
                height,
                width,
                self._image_config,
                image,
                lambda p: RoidmiMapDataParser._map_to_image(p, resolution, min_x, min_y),
            ),
            rooms,
        )

    @staticmethod
    def _parse_path(map_info: dict[str, Any]) -> Path:
        path_points = []
        if "posArray" in map_info:
            raw_points = json.loads(map_info["posArray"])
            for raw_point in raw_points:
                point = Point(raw_point[0], raw_point[1])
                path_points.append(point)
        return Path(None, None, None, [path_points])

    @staticmethod
    def _parse_vacuum_position(map_info: dict[str, Any]) -> Point | None:
        vacuum_position = RoidmiMapDataParser._parse_position(map_info, "robotPos", "robotPos", "robotPhi")
        if vacuum_position is None:
            vacuum_position = RoidmiMapDataParser._parse_position(map_info, "posX", "posY", "posPhi")
        return vacuum_position

    @staticmethod
    def _parse_charger_position(map_info: dict[str, Any]) -> Point | None:
        return RoidmiMapDataParser._parse_position(map_info, "chargeHandlePos", "chargeHandlePos", "chargeHandlePhi")

    @staticmethod
    def _parse_position(map_info: dict[str, Any], x_label: str, y_label: str, a_label: str) -> Point | None:
        position = None
        if x_label not in map_info or y_label not in map_info:
            return position
        x = map_info[x_label]
        y = map_info[y_label]
        a = None
        if x_label == y_label:
            x = x[0]
            y = y[1]
        if a_label in map_info:
            a = map_info[a_label] / 1000 * 180 / math.pi
        position = Point(x, y, a)
        return position

    @staticmethod
    def _get_room_numbers(map_info: dict[str, Any]) -> list[int]:
        rooms = []
        areas = []
        if "autoArea" in map_info:
            areas = map_info["autoArea"]
        elif "autoAreaValue" in map_info and map_info["autoAreaValue"] is not None:
            areas = map_info["autoAreaValue"]
        for area in areas:
            rooms.append(area["id"])
        return rooms

    @staticmethod
    def _parse_rooms(
        map_info: dict[str, Any],
        rooms_raw: dict[int, tuple[int, int, int, int]],
        points_converter: Callable[[int, int], Point],
    ) -> dict[int, Room]:
        rooms = {}
        areas = []
        if "autoArea" in map_info:
            areas = map_info["autoArea"]
        elif "autoAreaValue" in map_info and map_info["autoAreaValue"] is not None:
            areas = map_info["autoAreaValue"]
        for area in areas:
            room_id = area["id"]
            name = area["name"]
            pos_x = area["pos"][0] if "pos" in area else None
            pos_y = area["pos"][1] if "pos" in area else None
            p1 = points_converter(rooms_raw[room_id][0], rooms_raw[room_id][1])
            p2 = points_converter(rooms_raw[room_id][2], rooms_raw[room_id][3])
            rooms[room_id] = Room(p1.x, p1.y, p2.x, p2.y, room_id, name, pos_x, pos_y)
        return rooms

    @staticmethod
    def _parse_areas(map_info: dict[str, Any]) -> tuple[list[Area], list[Area], list[Wall]]:
        no_go_areas = []
        no_mopping_areas = []
        walls = []
        if "area" in map_info:
            areas = map_info["area"]
            for area in areas:
                if "active" in area and area["active"] == "forbid" and "vertexs" in area and len(area["vertexs"]) == 4:
                    vertexs = area["vertexs"]
                    x0 = vertexs[0][0]
                    y0 = vertexs[0][1]
                    x1 = vertexs[1][0]
                    y1 = vertexs[1][1]
                    x2 = vertexs[2][0]
                    y2 = vertexs[2][1]
                    x3 = vertexs[3][0]
                    y3 = vertexs[3][1]
                    no_area = Area(x0, y0, x1, y1, x2, y2, x3, y3)
                    if "forbidType" in area and area["forbidType"] == "mop":
                        no_mopping_areas.append(no_area)
                    if "forbidType" in area and area["forbidType"] == "all":
                        no_go_areas.append(no_area)
                if "active" in area and area["active"] == "forbid" and "vertexs" in area and len(area["vertexs"]) == 2:
                    vertexs = area["vertexs"]
                    x0 = vertexs[0][0]
                    y0 = vertexs[0][1]
                    x1 = vertexs[1][0]
                    y1 = vertexs[1][1]
                    wall = Wall(x0, y0, x1, y1)
                    if "forbidType" in area and area["forbidType"] == "all":
                        walls.append(wall)
        return no_go_areas, no_mopping_areas, walls
