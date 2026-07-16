import random
import statistics

from .models import ScheduleResult, Shift, Volunteer

Chromosome = list[str | None]

UNFILLED_PENALTY = 50
AVAILABILITY_PENALTY = 40
SKILL_PENALTY = 30
LANGUAGE_PENALTY = 20
LANGUAGE_BONUS = 10
DOUBLE_BOOK_PENALTY = 35
OVER_CAP_PENALTY = 25
FAIRNESS_WEIGHT = 3
BASE_REWARD = 5


class WorkforceGA:
    def __init__(
        self,
        volunteers: list[Volunteer],
        shifts: list[Shift],
        population_size: int = 60,
        generations: int = 150,
        mutation_rate: float = 0.15,
        elite_count: int = 4,
        seed: int | None = None,
        patience: int = 30,
    ) -> None:
        self._volunteers = {v.volunteer_id: v for v in volunteers}
        self._shifts = shifts
        self._population_size = population_size
        self._generations = generations
        self._mutation_rate = mutation_rate
        self._elite_count = elite_count
        self._patience = patience
        self._rng = random.Random(seed)  # noqa: S311
        self._eligible: dict[str, list[str]] = {
            shift.shift_id: [v.volunteer_id for v in volunteers if shift.shift_id in v.available_shift_ids]
            for shift in shifts
        }

    def _random_gene(self, shift_id: str) -> str | None:
        pool = self._eligible[shift_id]
        return self._rng.choice(pool) if pool else None

    def random_chromosome(self) -> Chromosome:
        return [self._random_gene(s.shift_id) for s in self._shifts]

    def fitness(self, chromosome: Chromosome) -> tuple[float, int, int]:
        score, unfilled, violations = 0.0, 0, 0
        counts: dict[str, int] = {}
        blocks_used: dict[str, set[str]] = {}

        for shift, gene in zip(self._shifts, chromosome, strict=True):
            if gene is None:
                unfilled += 1
                score -= UNFILLED_PENALTY
                continue

            volunteer = self._volunteers[gene]
            counts[gene] = counts.get(gene, 0) + 1
            score += BASE_REWARD

            if shift.shift_id not in volunteer.available_shift_ids:
                score -= AVAILABILITY_PENALTY
                violations += 1
            if shift.required_skill not in volunteer.skills:
                score -= SKILL_PENALTY
                violations += 1
            if shift.required_language:
                if shift.required_language in volunteer.languages:
                    score += LANGUAGE_BONUS
                else:
                    score -= LANGUAGE_PENALTY
                    violations += 1

            used = blocks_used.setdefault(gene, set())
            if shift.time_block in used:
                score -= DOUBLE_BOOK_PENALTY
                violations += 1
            else:
                used.add(shift.time_block)

        for volunteer_id, count in counts.items():
            cap = self._volunteers[volunteer_id].max_shifts
            if count > cap:
                excess = count - cap
                score -= OVER_CAP_PENALTY * excess
                violations += excess

        if counts:
            score -= statistics.pvariance(counts.values()) * FAIRNESS_WEIGHT

        return score, unfilled, violations

    def _tournament_select(self, scored: list[tuple[tuple[float, int, int], Chromosome]], k: int = 3) -> Chromosome:
        contenders = [self._rng.choice(scored) for _ in range(k)]
        return max(contenders, key=lambda pair: pair[0][0])[1]

    def _crossover(self, a: Chromosome, b: Chromosome) -> Chromosome:
        return [a[i] if self._rng.random() < 0.5 else b[i] for i in range(len(a))]

    def _mutate(self, chromosome: Chromosome) -> Chromosome:
        mutated = list(chromosome)
        for i, shift in enumerate(self._shifts):
            if self._rng.random() < self._mutation_rate:
                mutated[i] = self._random_gene(shift.shift_id)
        return mutated

    def run(self) -> ScheduleResult:
        population = [self.random_chromosome() for _ in range(self._population_size)]
        best: tuple[tuple[float, int, int], Chromosome] | None = None
        stale_generations = 0
        generations_run = 0

        while generations_run < self._generations:
            generations_run += 1
            scored = sorted(
                ((self.fitness(c), c) for c in population),
                key=lambda pair: pair[0][0],
                reverse=True,
            )
            if best is None or scored[0][0][0] > best[0][0]:
                best = scored[0]
                stale_generations = 0
            else:
                stale_generations += 1
            if stale_generations >= self._patience:
                break

            next_population = [c for _, c in scored[: self._elite_count]]
            while len(next_population) < self._population_size:
                parent_a = self._tournament_select(scored)
                parent_b = self._tournament_select(scored)
                child = self._mutate(self._crossover(parent_a, parent_b))
                next_population.append(child)
            population = next_population

        if best is None:
            raise RuntimeError("GA produced no result — population was empty")
        (fitness_score, unfilled, violations), chromosome = best
        assignment = {shift.shift_id: gene for shift, gene in zip(self._shifts, chromosome, strict=True)}
        return ScheduleResult(
            assignment=assignment,
            fitness=round(fitness_score, 2),
            generations_run=generations_run,
            unfilled_shifts=unfilled,
            constraint_violations=violations,
        )
