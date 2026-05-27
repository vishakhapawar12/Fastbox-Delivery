# Bonus features for FastBox:
#   1. Random delivery delays
#   2. ASCII map showing the delivery grid
#   3. Late agent joining mid-day
#   4. Export top performer to CSV

import random
import csv
from typing import Dict, List, Tuple, Optional


def simulate_with_delays(packages, delay_chance=0.25, min_delay=5.0, max_delay=30.0, seed=None):
    """
    Randomly apply delivery delays to a set of packages.
    Each package independently has delay_chance probability of being late.
    Returns {package_id: delay_minutes} — 0.0 means on time.
    """
    if seed is not None:
        random.seed(seed)

    delays = {}
    for pkg in packages:
        if random.random() < delay_chance:
            delays[pkg["id"]] = round(random.uniform(min_delay, max_delay), 1)
        else:
            delays[pkg["id"]] = 0.0
    return delays


def print_delay_report(delays):
    delayed = {pid: m for pid, m in delays.items() if m > 0}
    on_time = len(delays) - len(delayed)

    print("\n--- Delay Report ---")
    if not delayed:
        print("  All packages on time.")
    else:
        for pid, mins in sorted(delayed.items()):
            print(f"  {pid}: +{mins} min")
    print(f"  On time: {on_time}/{len(delays)}")


def ascii_map(agents, warehouses, packages, assignment, width=60, height=25):
    """
    Render a rough ASCII grid of the delivery area.
    W = warehouse, first letter of agent ID = agent starting position, * = destination
    """
    all_x = ([v[0] for v in warehouses.values()] +
             [v[0] for v in agents.values()] +
             [p["destination"][0] for p in packages])
    all_y = ([v[1] for v in warehouses.values()] +
             [v[1] for v in agents.values()] +
             [p["destination"][1] for p in packages])

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    span_x = max(max_x - min_x, 1)
    span_y = max(max_y - min_y, 1)

    def to_cell(x, y):
        col = int((x - min_x) / span_x * (width - 1))
        # flip y so higher values appear at the top of the grid
        row = (height - 1) - int((y - min_y) / span_y * (height - 1))
        return row, col

    grid = [["." for _ in range(width)] for _ in range(height)]

    for pkg in packages:
        r, c = to_cell(*pkg["destination"])
        if grid[r][c] == ".":
            grid[r][c] = "*"

    for aid, loc in agents.items():
        r, c = to_cell(*loc)
        grid[r][c] = aid[0]

    # warehouses drawn last so they're never hidden under agents or destinations
    for wid, loc in warehouses.items():
        r, c = to_cell(*loc)
        grid[r][c] = wid[0]

    border = "+" + "-" * width + "+"
    lines = [border]
    for row in grid:
        lines.append("|" + "".join(row) + "|")
    lines.append(border)
    lines.append("  W=warehouse  A=agent  *=destination")
    return "\n".join(lines)


def add_late_agent(new_id, new_loc, assignment, agents, warehouses, reassign_fraction=0.3):
    """
    Simulate a new agent joining partway through the day.

    Grabs the closest reassign_fraction of still-queued packages and hands them
    to the new agent. "Closest" is measured from the new agent's location to each
    package's source warehouse.

    Assumption: all assigned packages are still queued (none are mid-transit).
    This is conservative but unavoidable without tracking delivery progress.
    """
    from delivery_system import euclidean

    all_pkgs = [(pkg, aid) for aid, pkgs in assignment.items() for pkg in pkgs]
    n_take = max(1, int(len(all_pkgs) * reassign_fraction))

    all_pkgs.sort(key=lambda x: euclidean(new_loc, warehouses[x[0]["warehouse"]]))
    to_move = all_pkgs[:n_take]

    new_assignment = {aid: list(pkgs) for aid, pkgs in assignment.items()}
    new_assignment[new_id] = []
    new_agents = dict(agents)
    new_agents[new_id] = list(new_loc)

    for pkg, old_owner in to_move:
        new_assignment[old_owner].remove(pkg)
        new_assignment[new_id].append(pkg)

    print(f"\n{new_id} joined at {new_loc}, picked up: {[p['id'] for p, _ in to_move]}")
    return new_assignment, new_agents


def export_top_performer_csv(report, path="top_performer.csv"):
    best = report.get("best_agent")
    if not best:
        print("No deliveries made — nothing to export.")
        return

    row = {"agent_id": best, **report[best]}
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        w.writeheader()
        w.writerow(row)
    print(f"Top performer ({best}) exported to: {path}")
