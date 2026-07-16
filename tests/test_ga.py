from app.workforce.demo_data import build_demo_workforce
from app.workforce.genetic_algorithm import WorkforceGA
from app.workforce.models import Shift, Volunteer


def test_ga_is_deterministic_given_seed():
    volunteers, shifts = build_demo_workforce()
    result_a = WorkforceGA(volunteers, shifts, seed=1, generations=40).run()
    result_b = WorkforceGA(volunteers, shifts, seed=1, generations=40).run()
    assert result_a.assignment == result_b.assignment
    assert result_a.fitness == result_b.fitness


def test_ga_improves_on_random_baseline():
    volunteers, shifts = build_demo_workforce()
    ga = WorkforceGA(volunteers, shifts, seed=3, generations=80)
    optimized = ga.run()
    baseline = ga.fitness(ga.random_chromosome())[0]
    assert optimized.fitness >= baseline


def test_ga_respects_availability_when_only_one_choice():
    shifts = [Shift("s1", "North", "Morning", "medical", None)]
    volunteers = [
        Volunteer("v1", "Alice", frozenset({"English"}), frozenset({"medical"}), 2, frozenset({"s1"})),
        Volunteer("v2", "Bob", frozenset({"English"}), frozenset({"medical"}), 2, frozenset()),
    ]
    result = WorkforceGA(volunteers, shifts, seed=5, generations=20).run()
    assert result.assignment["s1"] == "v1"
    assert result.unfilled_shifts == 0
    assert result.constraint_violations == 0


def test_unfillable_shift_reported_as_unfilled():
    shifts = [Shift("s1", "North", "Morning", "medical", None)]
    volunteers = [Volunteer("v1", "Alice", frozenset({"English"}), frozenset({"medical"}), 2, frozenset())]
    result = WorkforceGA(volunteers, shifts, seed=1, generations=10).run()
    assert result.assignment["s1"] is None
    assert result.unfilled_shifts == 1
