import os
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from framework.core.context import TestContext
except ImportError:
    import framework.core.context as context_module

    TestContext = getattr(context_module, "TestContext", None)
    if TestContext is None:
        TestContext = getattr(context_module, "Context", None)
    if TestContext is None:
        TestContext = getattr(context_module, "BDDContext", None)

    if TestContext is None:
        raise ImportError(
            "Не знайдено класу контексту. "
            "Очікується один з класів: TestContext, Context або BDDContext "
            "у модулі framework.core.context"
        )

from framework.core.steps_registry import StepsRegistry

# ANSI-кольори для трохи красивішого логування
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


class StepResult:
    def __init__(self, text: str, passed: bool, error: Optional[str] = None):
        self.text = text
        self.passed = passed
        self.error = error


class ScenarioResult:
    def __init__(self, name: str):
        self.name = name
        self.steps: List[StepResult] = []

    @property
    def passed(self) -> bool:
        # сценарій вважаємо успішним, якщо всі кроки пройшли
        if not self.steps:
            return True
        return all(step.passed for step in self.steps)


def parse_feature_file(path: Path) -> Dict[str, Any]:
    """
    - "Feature: ..."  -> назва фічі
    - "Scenario: ..." -> назва сценарію
    - Given/When/Then/And/But ... -> кроки
    """
    feature_name = None
    scenarios: List[Dict[str, Any]] = []
    current_scenario: Optional[Dict[str, Any]] = None

    with path.open(encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("Feature:"):
                feature_name = line[len("Feature:"):].strip()
            elif line.startswith("Scenario:"):
                # зберігаємо попередній сценарій
                if current_scenario is not None:
                    scenarios.append(current_scenario)
                current_scenario = {
                    "name": line[len("Scenario:"):].strip(),
                    "steps": [],
                }
            elif line.startswith(("Given ", "When ", "Then ", "And ", "But ")):
                if current_scenario is None:
                    # крок без Scenario — ігноруємо
                    continue
                parts = line.split(" ", 1)
                step_text = parts[1].strip() if len(parts) == 2 else ""
                if step_text:
                    current_scenario["steps"].append(step_text)

    if current_scenario is not None:
        scenarios.append(current_scenario)

    return {
        "feature_name": feature_name or path.name,
        "scenarios": scenarios,
    }


def run_feature_file(ctx, steps: StepsRegistry, path: Path) -> Dict[str, Any]:
    parsed = parse_feature_file(path)
    feature_name = parsed["feature_name"]
    scenarios_data = parsed["scenarios"]

    print(f"\n=== Feature file: {path} ===")
    print(f"Feature: {feature_name}")

    scenario_results: List[ScenarioResult] = []

    for scenario_def in scenarios_data:
        scenario = ScenarioResult(scenario_def["name"])
        print(f"  Scenario: {scenario.name}")
        for step_text in scenario_def["steps"]:
            try:
                steps.execute_step(step_text)
                print(f"    {GREEN}[PASS]{RESET} {step_text}")
                scenario.steps.append(StepResult(step_text, True))
            except Exception as e:
                print(f"    {RED}[FAIL]{RESET} {step_text} :: {e}")
                scenario.steps.append(StepResult(step_text, False, str(e)))
        scenario_results.append(scenario)

    # локальна статистика по фічі
    feature_steps_total = sum(len(s.steps) for s in scenario_results)
    feature_steps_passed = sum(
        sum(1 for st in s.steps if st.passed) for s in scenario_results
    )
    feature_steps_failed = feature_steps_total - feature_steps_passed

    feature_scenarios_total = len(scenario_results)
    feature_scenarios_passed = sum(1 for s in scenario_results if s.passed)
    feature_scenarios_failed = feature_scenarios_total - feature_scenarios_passed

    print("\n  --- Feature summary ---")
    print(
        "  Scenarios: {} (passed: {}{}{}," " failed: {}{}{})".format(
            feature_scenarios_total,
            GREEN,
            feature_scenarios_passed,
            RESET,
            RED,
            feature_scenarios_failed,
            RESET,
        )
    )
    print(
        "  Steps:     {} (passed: {}{}{}," " failed: {}{}{})".format(
            feature_steps_total,
            GREEN,
            feature_steps_passed,
            RESET,
            RED,
            feature_steps_failed,
            RESET,
        )
    )

    return {
        "scenario_results": scenario_results,
        "feature_name": feature_name,
    }


def main():
    # корінь проєкту: .../framework/core/runner.py -> два рівні вгору -> корінь
    project_root = Path(__file__).resolve().parents[2]
    features_dir = project_root / "tests" / "features"

    if not features_dir.exists():
        print(f"{RED}Features directory not found:{RESET} {features_dir}")
        return

    ctx = TestContext()
    steps = StepsRegistry(ctx)

    all_feature_results: List[Dict[str, Any]] = []

    MAX_FEATURE_FILES = None  # кількість тестів на виконання

    feature_files = sorted(features_dir.glob("*.kwiga"))

    if MAX_FEATURE_FILES is not None:
        feature_files = feature_files[:MAX_FEATURE_FILES]

    if not feature_files:
        print(f"{YELLOW}No .kwiga feature files found in{RESET} {features_dir}")
        return

    for path in feature_files:
        result = run_feature_file(ctx, steps, path)
        all_feature_results.append(result)

    # глобальна статистика
    total_features = len(all_feature_results)
    all_scenarios: List[ScenarioResult] = []
    for fr in all_feature_results:
        all_scenarios.extend(fr["scenario_results"])

    total_scenarios = len(all_scenarios)
    passed_scenarios = sum(1 for s in all_scenarios if s.passed)
    failed_scenarios = total_scenarios - passed_scenarios

    total_steps = sum(len(s.steps) for s in all_scenarios)
    passed_steps = sum(
        sum(1 for st in s.steps if st.passed) for s in all_scenarios
    )
    failed_steps = total_steps - passed_steps

    print("\n=========== OVERALL SUMMARY ===========")
    print("Features:   {}".format(total_features))
    print(
        "Scenarios:  {} (passed: {}{}{}," " failed: {}{}{})".format(
            total_scenarios,
            GREEN,
            passed_scenarios,
            RESET,
            RED,
            failed_scenarios,
            RESET,
        )
    )
    print(
        "Steps:      {} (passed: {}{}{}," " failed: {}{}{})".format(
            total_steps,
            GREEN,
            passed_steps,
            RESET,
            RED,
            failed_steps,
            RESET,
        )
    )

    if failed_scenarios > 0 or failed_steps > 0:
        print(
            "\n{}Some scenarios/steps failed. "
            "Check the log above for details.{}".format(RED, RESET)
        )


if __name__ == "__main__":
    main()
