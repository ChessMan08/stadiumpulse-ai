import random
import time
from dataclasses import dataclass

GATES = ("North", "South", "East", "West", "VIP")
DENSITY_ALERT_THRESHOLD = 3.5


@dataclass
class GateReading:
    gate: str
    density: float
    temperature_c: float
    air_quality_index: int
    anomaly: str | None = None


@dataclass
class SensorSnapshot:
    timestamp: float
    readings: list[GateReading]

    @property
    def peak_gate(self) -> GateReading:
        return max(self.readings, key=lambda r: r.density)

    @property
    def alerts(self) -> list[GateReading]:
        return [r for r in self.readings if r.density >= DENSITY_ALERT_THRESHOLD]


class SensorSimulator:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)  # noqa: S311
        self._density: dict[str, float] = {gate: self._rng.uniform(0.8, 2.2) for gate in GATES}
        self._anomaly_gate: str | None = None
        self._anomaly_ttl: int = 0

    def _step(self) -> None:
        if self._anomaly_ttl <= 0 and self._rng.random() < 0.15:
            self._anomaly_gate = self._rng.choice(GATES)
            self._anomaly_ttl = self._rng.randint(3, 6)

        for gate in GATES:
            drift = self._rng.uniform(-0.25, 0.25)
            boost = 2.0 if gate == self._anomaly_gate else 0.0
            self._density[gate] = max(0.2, min(6.0, self._density[gate] + drift + boost))

        if self._anomaly_gate:
            self._anomaly_ttl -= 1
            if self._anomaly_ttl <= 0:
                self._anomaly_gate = None

    def snapshot(self) -> SensorSnapshot:
        self._step()
        readings = [
            GateReading(
                gate=gate,
                density=round(self._density[gate], 2),
                temperature_c=round(self._rng.uniform(19.0, 27.0), 1),
                air_quality_index=self._rng.randint(35, 90),
                anomaly="turnstile_jam" if gate == self._anomaly_gate else None,
            )
            for gate in GATES
        ]
        return SensorSnapshot(timestamp=time.time(), readings=readings)
