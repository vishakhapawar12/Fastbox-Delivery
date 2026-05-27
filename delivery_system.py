# FastBox delivery simulator
# Handles JSON parsing, package assignment, route simulation, and report generation.

import json
import math
import csv
import os


def euclidean(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def parse_input(raw):
    # Two different JSON schemas are floating around in the test files.
    # Schema A: warehouses/agents are lists of {"id": ..., "location": [...]}
    # Schema B: warehouses/agents are plain dicts {"W1": [x, y], ...}
    # Detect and normalize both so the rest of the code doesn't care.

    if isinstance(raw["warehouses"], list):
        warehouses = {w["id"]: list(w["location"]) for w in raw["warehouses"]}
    else:
        warehouses = {k: list(v) for k, v in raw["warehouses"].items()}

    if isinstance(raw["agents"], list):
        agents = {a["id"]: list(a["location"]) for a in raw["agents"]}
    else:
        agents = {k: list(v) for k, v in raw["agents"].items()}

    # Schema A uses "warehouse_id", Schema B uses "warehouse" — handle both
    packages = []
    for p in raw["packages"]:
        packages.append({
            "id": p["id"],
            "warehouse": p.get("warehouse") or p.get("warehouse_id"),
            "destination": list(p["destination"])
        })

    return warehouses, agents, packages


def load_input(filepath):
    with open(filepath) as f:
        raw = json.load(f)
    return parse_input(raw)


def assign_packages(packages, agents, warehouses):
    """
    Assign each package to the agent closest to that package's warehouse.

    Assignment uses initial agent positions only — we compute all assignments
    at once before anyone moves. Sorting agents before the min() call ensures
    ties always resolve to the lexicographically smaller ID (A1 over A2, etc.)
    so output is deterministic.
    """
    assignment = {aid: [] for aid in agents}

    for pkg in packages:
        wloc = warehouses[pkg["warehouse"]]
        nearest = min(sorted(agents), key=lambda a: euclidean(agents[a], wloc))
        assignment[nearest].append(pkg)

    return assignment


def simulate_route(start, packages, warehouses):
    """
    Compute an agent's total travel distance and the order they delivered packages.

    Routing logic: greedy nearest-neighbour.
      1. Group packages by source warehouse.
      2. Always travel to the closest unvisited warehouse next.
      3. At the warehouse, deliver all packages from there in nearest-destination order.
      4. Repeat until done.

    This isn't a perfect TSP solution but it's sensible and fast. The spec doesn't
    require optimal routing, just that agents pick up from a warehouse and deliver.
    Agents don't return to base — no return trip mentioned in the spec.
    """
    if not packages:
        return 0.0, []

    pos = list(start)
    total = 0.0
    delivered = []

    # bucket packages by source warehouse
    by_wh = {}
    for p in packages:
        by_wh.setdefault(p["warehouse"], []).append(p)

    pending = list(by_wh.keys())

    while pending:
        # go to whichever warehouse is closest from current position
        nxt = min(pending, key=lambda w: euclidean(pos, warehouses[w]))
        pending.remove(nxt)

        total += euclidean(pos, warehouses[nxt])
        pos = list(warehouses[nxt])

        # deliver this warehouse's packages, nearest destination first
        q = by_wh[nxt][:]
        while q:
            pkg = min(q, key=lambda p: euclidean(pos, p["destination"]))
            q.remove(pkg)
            total += euclidean(pos, pkg["destination"])
            pos = list(pkg["destination"])
            delivered.append(pkg["id"])

    return round(total, 2), delivered


def build_report(agents, assignment, warehouses):
    report = {}

    for aid in sorted(agents):
        dist, delivered = simulate_route(agents[aid], assignment[aid], warehouses)
        n = len(delivered)
        # efficiency = average distance per package, lower is better
        eff = round(dist / n, 2) if n > 0 else 0.0
        report[aid] = {
            "packages_delivered": n,
            "total_distance": dist,
            "efficiency": eff
        }

    # agents with 0 deliveries get efficiency 0.0, but that shouldn't win best_agent
    active = {a: report[a] for a in report if report[a]["packages_delivered"] > 0}
    report["best_agent"] = min(active, key=lambda a: active[a]["efficiency"]) if active else None

    return report


def save_report(report, path="report.json"):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)


def export_top_performer_csv(report, path="top_performer.csv"):
    best = report.get("best_agent")
    if not best:
        print("No active agents — skipping CSV export.")
        return
    row = {"agent_id": best, **report[best]}
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        w.writeheader()
        w.writerow(row)
    print(f"Top performer exported to: {path}")


def run(input_path, output_path="report.json", verbose=True, export_csv=False):
    warehouses, agents, packages = load_input(input_path)
    assignment = assign_packages(packages, agents, warehouses)
    report = build_report(agents, assignment, warehouses)
    save_report(report, output_path)

    if export_csv:
        export_top_performer_csv(report, output_path.replace(".json", "_top.csv"))

    if verbose:
        _print_summary(report, agents, input_path, output_path)

    return report


def _print_summary(report, agents, input_path, output_path):
    print(f"\n{'='*52}")
    print(f"  FastBox - {os.path.basename(input_path)}")
    print(f"{'='*52}")
    print(f"  {'Agent':<8} {'Pkgs':>6} {'Distance':>10} {'Efficiency':>12}")
    print(f"  {'-'*38}")
    for aid in sorted(agents):
        d = report[aid]
        tag = " *" if aid == report["best_agent"] else ""
        print(f"  {aid:<8} {d['packages_delivered']:>6} {d['total_distance']:>10.2f} {d['efficiency']:>12.2f}{tag}")
    print(f"  {'-'*38}")
    print(f"  Best agent : {report['best_agent']}")
    print(f"  Saved to   : {output_path}")
    print(f"{'='*52}\n")
