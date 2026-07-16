from dataclasses import dataclass

from ..schemas import AmenityType
from ..sensors.simulator import GATES

AMENITIES = tuple(AmenityType)


@dataclass(frozen=True)
class Section:
    section_id: str
    quadrant: str
    level: str
    walk_minutes: int

    @property
    def nearest_gate(self) -> str:
        return self.quadrant

    @property
    def nearest_restroom(self) -> str:
        return f"{self.quadrant} Concourse Restroom"

    @property
    def nearest_concession(self) -> str:
        return f"{self.quadrant} Concourse Concessions"

    @property
    def nearest_accessible_entrance(self) -> str:
        return f"{self.quadrant} Gate Accessible Entrance"

    def destination(self, amenity: AmenityType) -> str:
        destinations: dict[AmenityType, str] = {
            AmenityType.GATE: f"{self.nearest_gate} gate",
            AmenityType.RESTROOM: self.nearest_restroom,
            AmenityType.CONCESSION: self.nearest_concession,
            AmenityType.ACCESSIBLE_ENTRANCE: self.nearest_accessible_entrance,
        }
        return destinations[amenity]


def _build_sections() -> dict[str, Section]:
    sections: dict[str, Section] = {}
    for i, quadrant in enumerate(GATES[:4]):
        lower_id = f"{100 + i * 14 + 1}"
        upper_id = f"{200 + i * 14 + 1}"
        sections[lower_id] = Section(lower_id, quadrant, "Lower", walk_minutes=4)
        sections[upper_id] = Section(upper_id, quadrant, "Upper", walk_minutes=8)
    return sections


SECTIONS: dict[str, Section] = _build_sections()


def find_section(query: str) -> Section:
    text = query.strip().lower()
    for section in SECTIONS.values():
        if section.section_id in text:
            return section
    for section in SECTIONS.values():
        if section.quadrant.lower() in text:
            return section
    return next(iter(SECTIONS.values()))
