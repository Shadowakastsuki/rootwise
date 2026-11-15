
from types import SimpleNamespace

from app.services.environmental_service import (
    point_in_geometry,
    get_environmental_data,
)


def test_point_inside_polygon():
    geometry = {
        "type": "Polygon",
        "coordinates": [[
            [77.0, 12.0],
            [78.0, 12.0],
            [78.0, 13.0],
            [77.0, 13.0],
            [77.0, 12.0],
        ]],
    }

    assert point_in_geometry(77.5, 12.5, geometry)
    assert not point_in_geometry(79.0, 12.5, geometry)


def test_polygon_hole():
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [0, 0], [10, 0], [10, 10],
                [0, 10], [0, 0],
            ],
            [
                [4, 4], [6, 4], [6, 6],
                [4, 6], [4, 4],
            ],
        ],
    }

    assert point_in_geometry(2, 2, geometry)
    assert not point_in_geometry(5, 5, geometry)


def test_multipolygon():
    geometry = {
        "type": "MultiPolygon",
        "coordinates": [
            [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            [[[3, 3], [4, 3], [4, 4], [3, 4], [3, 3]]],
        ],
    }

    assert point_in_geometry(3.5, 3.5, geometry)
    assert not point_in_geometry(2, 2, geometry)


def test_missing_coordinates():
    field = SimpleNamespace(
        centroid_lat=None,
        centroid_lon=None,
        region_id=2,
    )

    result = get_environmental_data(None, field)

    assert result["status"] == "missing_coordinates"
    assert result["map_cell"] is None
    assert result["observations"] == []
