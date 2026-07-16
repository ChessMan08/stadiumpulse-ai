from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Verbosity(StrEnum):
    RICH = "rich"
    BRIEF = "brief"


class AmenityType(StrEnum):
    GATE = "gate"
    RESTROOM = "restroom"
    CONCESSION = "concession"
    ACCESSIBLE_ENTRANCE = "accessible_entrance"


class OpsQueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    language: str = Field(default="English", max_length=30)


class OpsQueryResponse(BaseModel):
    question: str
    retrieved_sops: list[dict[str, str]]
    active_alerts: list[dict[str, object]]
    narrative: str


class GateReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gate: str
    density: float
    temperature_c: float
    air_quality_index: int
    anomaly: str | None


class SensorSnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: float
    readings: list[GateReadingOut]


class TransitRouteRequest(BaseModel):
    city: str = Field(max_length=30)
    origin: str = Field(min_length=2, max_length=200)
    language: str = Field(default="English", max_length=30)


class TransitRouteResponse(BaseModel):
    city: str
    stadium: str
    zone: str
    modes: list[str]
    estimated_minutes: int
    recommended_gate: str
    congestion_warning: str | None
    narrative: str


class WorkforceOptimizeResponse(BaseModel):
    fitness: float
    generations_run: int
    unfilled_shifts: int
    constraint_violations: int
    total_shifts: int
    filled_percent: float
    assignment: dict[str, str | None]


class BriefingResponse(BaseModel):
    volunteer_id: str
    volunteer_name: str
    message: str


class CommentaryRequest(BaseModel):
    event_id: str = Field(max_length=20)
    language: str = Field(default="English", max_length=30)
    verbosity: Verbosity = Verbosity.RICH


class CommentaryResponse(BaseModel):
    event_id: str
    text: str


class WayfindRequest(BaseModel):
    section: str = Field(min_length=1, max_length=20)
    amenity: AmenityType = AmenityType.GATE
    language: str = Field(default="English", max_length=30)


class WayfindResponse(BaseModel):
    section: str
    quadrant: str
    amenity: AmenityType
    destination: str
    walk_minutes: int
    congestion_warning: str | None
    narrative: str


class ZoneEstimateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gate: str
    estimated_kw: float
    reducible: bool
    potential_savings_kw: float


class SustainabilityReportResponse(BaseModel):
    zones: list[ZoneEstimateOut]
    total_estimated_kw: float
    total_potential_savings_kw: float
    reducible_zones: list[str]
    tip: str


class FaqRequest(BaseModel):
    topic_id: str = Field(max_length=40)
    language: str = Field(default="English", max_length=30)


class FaqResponse(BaseModel):
    topic_id: str
    label: str
    answer: str


class DashboardResponse(BaseModel):
    sensors: SensorSnapshotOut
    peak_gate: str
    active_alert_count: int
    workforce_filled_percent: float
    sustainability_tip: str
    total_estimated_kw: float
