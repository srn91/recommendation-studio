from __future__ import annotations

from app.reporting import build_report, write_outputs


def report() -> None:
    recommendation_report = build_report()
    json_path, markdown_path = write_outputs(recommendation_report)
    print(f"base_precision_at_5={recommendation_report['base_precision_at_5']}")
    print(f"reranked_diversity_at_5={recommendation_report['reranked_diversity_at_5']}")
    print(f"json_path={json_path}")
    print(f"markdown_path={markdown_path}")


def main() -> None:
    import sys

    if len(sys.argv) != 2 or sys.argv[1] != "report":
        raise SystemExit("usage: python3 -m app.cli report")

    report()


if __name__ == "__main__":
    main()
