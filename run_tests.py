"""
Run all test cases and validate the reports.

Checks:
  - every package in the input ends up delivered exactly once
  - efficiency values are consistent with distance/packages
  - report has the correct structure

Usage:
    python run_tests.py
    python run_tests.py --verbose
"""

import json
import os
import sys
from delivery_system import load_input, assign_packages, build_report, save_report

VERBOSE = "--verbose" in sys.argv
TEST_DIR = os.path.join(os.path.dirname(__file__), "test_cases")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")
BASE_CASE = os.path.join(os.path.dirname(__file__), "data.json")


def validate_report(report, total_packages):
    issues = []

    if "best_agent" not in report:
        issues.append("Missing 'best_agent' key")

    delivered_sum = sum(v["packages_delivered"] for k, v in report.items() if k != "best_agent")
    if delivered_sum != total_packages:
        issues.append(f"Package count mismatch: report says {delivered_sum}, input has {total_packages}")

    for aid, stats in report.items():
        if aid == "best_agent":
            continue
        if stats["total_distance"] < 0:
            issues.append(f"{aid}: negative distance")
        if stats["efficiency"] < 0:
            issues.append(f"{aid}: negative efficiency")
        n = stats["packages_delivered"]
        if n > 0:
            expected = round(stats["total_distance"] / n, 2)
            if abs(expected - stats["efficiency"]) > 0.01:
                issues.append(f"{aid}: efficiency mismatch (got {stats['efficiency']}, expected {expected})")

    return len(issues) == 0, issues


def run_single(filepath, out_dir):
    fname = os.path.basename(filepath)
    out_path = os.path.join(out_dir, fname.replace(".json", "_report.json"))

    try:
        warehouses, agents, packages = load_input(filepath)
        assignment = assign_packages(packages, agents, warehouses)
        report = build_report(agents, assignment, warehouses)
        save_report(report, out_path)

        passed, issues = validate_report(report, len(packages))
        status = "PASS" if passed else "FAIL"
        best = report.get("best_agent", "?")
        total_del = sum(v["packages_delivered"] for k, v in report.items() if k != "best_agent")

        print(f"  [{status}]  {fname:<25}  {total_del}/{len(packages)} pkgs  best={best}")

        if not passed:
            for issue in issues:
                print(f"          ✗ {issue}")

        if VERBOSE:
            for aid in sorted(agents):
                d = report[aid]
                marker = " *" if aid == best else ""
                print(f"          {aid}: {d['packages_delivered']} pkgs, "
                      f"dist={d['total_distance']:.2f}, eff={d['efficiency']:.2f}{marker}")

        return passed

    except Exception as exc:
        print(f"  [ERROR] {fname:<25}  {exc}")
        return False


def main():
    os.makedirs(REPORT_DIR, exist_ok=True)

    test_files = []
    if os.path.isfile(BASE_CASE):
        test_files.append(BASE_CASE)

    for i in range(1, 100):
        p = os.path.join(TEST_DIR, f"test_case_{i}.json")
        if os.path.isfile(p):
            test_files.append(p)

    if not test_files:
        print("No test files found. Expected data.json and/or test_cases/test_case_*.json")
        sys.exit(1)

    print(f"\nRunning {len(test_files)} test(s)...\n")
    results = [run_single(fp, REPORT_DIR) for fp in test_files]

    passed = sum(results)
    failed = len(results) - passed
    print(f"\n{'-'*52}")
    print(f"  Results: {passed}/{len(results)} passed", end="")
    print(f"  ({failed} failed)" if failed else "  -- all clear!")
    print(f"  Reports saved to: {REPORT_DIR}/")
    print(f"{'-'*52}\n")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
