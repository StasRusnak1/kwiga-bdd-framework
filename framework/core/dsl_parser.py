from dataclasses import dataclass
from typing import List

@dataclass
class Step:
    keyword: str
    text: str
    line_no: int

@dataclass
class Scenario:
    name: str
    steps: List[Step]

@dataclass
class Feature:
    name: str
    scenarios: List[Scenario]

def parse_feature(content: str) -> Feature:
    lines = content.splitlines()
    feature_name = "Unnamed feature"
    scenarios: List[Scenario] = []
    current_scenario = None
    current_steps: List[Step] = []

    for i, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("feature:"):
            feature_name = line.split(":", 1)[1].strip()
        elif line.lower().startswith("scenario:"):
            if current_scenario:
                current_scenario.steps = current_steps
                scenarios.append(current_scenario)
                current_steps = []
            name = line.split(":", 1)[1].strip()
            current_scenario = Scenario(name=name, steps=[])
        elif any(line.startswith(k) for k in ("Given", "When", "Then", "And")):
            parts = line.split(" ", 1)
            keyword = parts[0]
            text = parts[1].strip() if len(parts) > 1 else ""
            current_steps.append(Step(keyword=keyword, text=text, line_no=i))

    if current_scenario:
        current_scenario.steps = current_steps
        scenarios.append(current_scenario)

    return Feature(name=feature_name, scenarios=scenarios)
