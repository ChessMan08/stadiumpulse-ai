from dataclasses import dataclass


@dataclass(frozen=True)
class Volunteer:
    volunteer_id: str
    name: str
    languages: frozenset[str]
    skills: frozenset[str]
    max_shifts: int
    available_shift_ids: frozenset[str]


@dataclass(frozen=True)
class Shift:
    shift_id: str
    gate: str
    time_block: str
    required_skill: str
    required_language: str | None


@dataclass
class ScheduleResult:
    assignment: dict[str, str | None]
    fitness: float
    generations_run: int
    unfilled_shifts: int
    constraint_violations: int
