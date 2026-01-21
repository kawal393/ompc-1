import json
import sys
from typing import Any, Dict

REQUIRED_FIELDS = [
    "model_name",
    "version",
    "training_compute_flops",
    "license_type",
    "intended_use"
]

SYSTEMIC_THRESHOLD = 1e25  # Heuristic threshold aligned with EU AI Act guidance

def validate(data: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED_FIELDS if k not in data or not data[k]]
    if missing:
        return {
            "status": "FAIL",
            "errors": f"Missing required fields: {missing}"
        }

    try:
        flops = float(data["training_compute_flops"])
    except (ValueError, TypeError):
        return {
            "status": "FAIL",
            "errors": "training_compute_flops must be numeric"
        }

    risk_level = "Systemic (Heuristic)" if flops >= SYSTEMIC_THRESHOLD else "Standard"

    certificate_id = f"OMPC1-2026-{abs(hash(data['model_name'] + data['version'])) % 10000000:07d}"

    return {
        "status": "PASS",
        "model": data["model_name"],
        "standard": "OMPC-1",
        "risk_level": risk_level,
        "certificate_id": certificate_id
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python engine.py <model.json>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        data = json.load(f)

    result = validate(data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
