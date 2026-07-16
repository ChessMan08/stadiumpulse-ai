import random

from ..sensors.simulator import GATES
from .models import Shift, Volunteer

NAMES = [
    "Ananya", "Marco", "Wei", "Fatima", "Diego", "Priya", "Noah", "Yuki",
    "Elena", "Omar", "Grace", "Liam", "Sara", "Chen", "Mateo", "Zoe",
    "Ibrahim", "Nina", "Alex", "Ravi", "Lucia", "Jonas", "Mei", "Tara",
]
LANGUAGES = ("English", "Spanish", "French", "Portuguese", "Mandarin", "Arabic", "Hindi")
SKILLS = ("wayfinding", "hospitality", "medical", "security", "vip", "accessibility")
TIME_BLOCKS = ("Morning", "Midday", "Evening", "Night")


def build_demo_shifts() -> list[Shift]:
    rng = random.Random(11)  # noqa: S311
    shifts: list[Shift] = []
    for gate in GATES:
        for block in TIME_BLOCKS:
            skill = rng.choice(SKILLS)
            language = rng.choice(LANGUAGES) if rng.random() < 0.5 else None
            shifts.append(
                Shift(
                    shift_id=f"{gate}-{block}",
                    gate=gate,
                    time_block=block,
                    required_skill=skill,
                    required_language=language,
                )
            )
    return shifts


def build_demo_volunteers(shifts: list[Shift], seed: int = 7) -> list[Volunteer]:
    rng = random.Random(seed)  # noqa: S311
    shift_ids = [s.shift_id for s in shifts]
    volunteers: list[Volunteer] = []
    for i, name in enumerate(NAMES):
        languages = frozenset(rng.sample(LANGUAGES, k=rng.randint(1, 3)))
        skills = frozenset(rng.sample(SKILLS, k=rng.randint(2, 4)))
        available = frozenset(rng.sample(shift_ids, k=rng.randint(6, len(shift_ids))))
        volunteers.append(
            Volunteer(
                volunteer_id=f"vol-{i:02d}",
                name=name,
                languages=languages,
                skills=skills,
                max_shifts=rng.randint(2, 4),
                available_shift_ids=available,
            )
        )
    return volunteers


def build_demo_workforce(seed: int = 7) -> tuple[list[Volunteer], list[Shift]]:
    shifts = build_demo_shifts()
    volunteers = build_demo_volunteers(shifts, seed=seed)
    return volunteers, shifts
