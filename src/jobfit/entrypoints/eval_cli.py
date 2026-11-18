import argparse
from pathlib import Path

from jobfit.adapters.taxonomy_file import load_default_taxonomy
from jobfit.eval.dataset import load_cases
from jobfit.eval.runner import render_markdown, run_eval, write_reports


def main() -> int:
    parser = argparse.ArgumentParser(prog="jobfit-eval")
    parser.add_argument("--dataset", type=Path, default=Path("eval/golden.json"))
    parser.add_argument("--out", type=Path, default=Path("reports/eval"))
    args = parser.parse_args()

    if not args.dataset.is_file():
        print(f"Датасет не найден: {args.dataset}")
        return 2

    report = run_eval(load_cases(args.dataset), load_default_taxonomy())
    write_reports(report, args.out)
    print(render_markdown(report))
    return 0 if report.gates_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
