from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

with open(PROJECT_ROOT / "prompts" / "report.yaml") as f:
    report_prompt = yaml.safe_load(f)

with open(PROJECT_ROOT / "prompts" / "orchestrator.yaml") as f:
    sys_prompt = yaml.safe_load(f)


with open(PROJECT_ROOT / "prompts" / "observer.yaml") as f:
    observer_prompt = yaml.safe_load(f)