"""
Demo of all bonus features using the base case (data.json).
Run with: python demo_bonus.py
"""

import os
from delivery_system import load_input, assign_packages, build_report
from bonus import simulate_with_delays, print_delay_report, ascii_map, add_late_agent, export_top_performer_csv

INPUT_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def main():
    print("\n" + "=" * 55)
    print("  FastBox Bonus Feature Demo")
    print("=" * 55)

    warehouses, agents, packages = load_input(INPUT_FILE)
    assignment = assign_packages(packages, agents, warehouses)
    report = build_report(agents, assignment, warehouses)

    # --- 1. Random delivery delays ---
    print("\n[1] Random Delivery Delays")
    delays = simulate_with_delays(packages, delay_chance=0.4, seed=42)
    print_delay_report(delays)

    # --- 2. ASCII map ---
    print("\n[2] ASCII Map")
    print(ascii_map(agents, warehouses, packages, assignment, width=55, height=18))

    # --- 3. Late agent joining mid-day ---
    print("\n[3] Late Agent Joining Mid-Day")
    new_assignment, new_agents = add_late_agent(
        new_id="A4",
        new_loc=[25, 35],
        assignment=assignment,
        agents=agents,
        warehouses=warehouses,
        reassign_fraction=0.4
    )
    new_report = build_report(new_agents, new_assignment, warehouses)
    print("\nUpdated report after A4 joins:")
    for aid in sorted(new_agents):
        d = new_report[aid]
        marker = " *" if aid == new_report["best_agent"] else ""
        print(f"  {aid}: {d['packages_delivered']} pkgs, dist={d['total_distance']:.2f}, eff={d['efficiency']:.2f}{marker}")

    # --- 4. Export top performer to CSV ---
    print("\n[4] Export Top Performer to CSV")
    csv_path = os.path.join(os.path.dirname(__file__), "top_performer.csv")
    export_top_performer_csv(report, csv_path)
    with open(csv_path) as f:
        for line in f:
            print("  " + line.strip())

    print("\n" + "=" * 55 + "\n")


if __name__ == "__main__":
    main()
