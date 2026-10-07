import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.demo_data import build_demo_context


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a demo observability context for the SRE agent")
    parser.add_argument("--service", default="checkout", help="Service name to simulate")
    parser.add_argument("--write-json", action="store_true", help="Write the demo context to a JSON file")
    args = parser.parse_args()

    context = build_demo_context(args.service)

    print("Demo observability context generated for:", args.service)
    print(json.dumps(context, indent=2))

    if args.write_json:
        output_path = Path("examples/demo_observability_output.json")
        output_path.write_text(json.dumps(context, indent=2), encoding="utf-8")
        print("\nWrote demo data to:", output_path)


if __name__ == "__main__":
    main()
