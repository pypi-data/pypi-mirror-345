# generated from codegen/templates/_plane.py

from __future__ import annotations

__all__ = ["DPlane"]

from emath import DVector3


class DPlane:
    __slots__ = ["_distance", "_normal"]

    def __init__(self, distance: float, normal: DVector3):
        self._distance = distance
        self._normal = normal

        magnitude = normal.magnitude
        try:
            self._distance /= magnitude
            self._normal /= magnitude
        except ZeroDivisionError:
            raise ValueError("invalid normal")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DPlane):
            return False
        return self._distance == other._distance and self._normal == other._normal

    def __repr__(self) -> str:
        return f"<Plane distance={self._distance} normal={self._normal}>"

    def get_signed_distance_to_point(self, point: DVector3) -> float:
        return self._normal @ point + self._distance

    @property
    def distance(self) -> float:
        return self._distance

    @property
    def normal(self) -> DVector3:
        return self._normal
