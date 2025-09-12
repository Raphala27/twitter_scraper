import argparse
import json
from app.services.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run mocked Twitter->Ollama pipeline with rules and storage")
    parser.add_argument("user", help="Twitter handle or numeric user_id")
    parser.add_argument("--limit", type=int, default=10, help="Number of posts to process")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    result = run_pipeline(args.user, args.limit)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Processed: {result.get('processed')} posts")
        events = result.get("events", [])
        for i, e in enumerate(events, start=1):
            print(f"\n[{i}] {e.get('created_at')} post_id={e.get('post_id')} rule={e.get('rule')}")
            print(f"Result: {e.get('result')}")


if __name__ == "__main__":
    main()
