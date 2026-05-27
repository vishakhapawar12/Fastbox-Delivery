# FastBox Delivery Simulator

A Python logistics simulator for a fictional delivery company called FastBox.
Give it a JSON file describing warehouses, delivery agents, and packages — it assigns
packages to agents, simulates their routes, and produces a performance report.

## Quick start

```bash
python main.py                               # runs data.json → report.json
python main.py input.json output.json        # custom paths
python main.py input.json output.json --csv  # also save top performer to CSV

python run_tests.py           # run all test cases
python run_tests.py --verbose  # per-agent breakdown per test
python demo_bonus.py          # show all bonus features
```

No third-party packages needed — Python 3.8+ standard library only.

## Files

```
fastbox-delivery/
├── delivery_system.py   # core engine: parsing, assignment, simulation, report
├── main.py              # CLI wrapper
├── bonus.py             # optional extras (delays, ASCII map, late agent, CSV)
├── demo_bonus.py        # runs through all bonus features
├── run_tests.py         # validates all test cases
├── data.json            # base case input
└── test_cases/          # additional test JSON files
```

## Input format

Two schemas are supported (the base case uses Schema A, the numbered test cases use Schema B):

**Schema A** — warehouses and agents as lists:
```json
{
  "warehouses": [{"id": "W1", "location": [0, 0]}],
  "agents":     [{"id": "A1", "location": [5, 5]}],
  "packages":   [{"id": "P1", "warehouse_id": "W1", "destination": [30, 40]}]
}
```

**Schema B** — warehouses and agents as dicts:
```json
{
  "warehouses": {"W1": [0, 0]},
  "agents":     {"A1": [5, 5]},
  "packages":   [{"id": "P1", "warehouse": "W1", "destination": [30, 40]}]
}
```

The parser detects which one it has and normalizes it automatically.

## Output

```json
{
  "A1": {"packages_delivered": 2, "total_distance": 57.27, "efficiency": 28.64},
  "A2": {"packages_delivered": 2, "total_distance": 60.83, "efficiency": 30.42},
  "A3": {"packages_delivered": 1, "total_distance": 14.14, "efficiency": 14.14},
  "best_agent": "A3"
}
```

`efficiency` is average distance per package (lower = better). `best_agent` is whoever
has the lowest efficiency score among agents who actually delivered something.

## Assumptions

A few decisions I made where the spec was silent:

**Static assignment.** All packages get assigned at the start, using initial agent positions.
Agents don't reposition between assignments — otherwise you'd have a circular dependency
(assigning one package changes distances for the next).

**Tie-breaking by ID.** If two agents are equidistant from a warehouse, the one with the
smaller ID wins (A1 over A2). This keeps output deterministic regardless of dict ordering.

**Greedy routing.** When an agent has packages at multiple warehouses, they visit the nearest
warehouse first, then deliver from there in nearest-destination order. Not a perfect TSP
solution, but reasonable and much simpler. The spec doesn't require optimal routing.

**No return trip.** Agents don't travel back to base after their last delivery. The spec
doesn't mention it, so I left it out.

**Idle agents.** If an agent ends up with no packages their report shows 0/0/0.0 and they're
excluded from best_agent — an idle agent with efficiency 0.0 shouldn't win.

## Bonus features

All live in `bonus.py`, demonstrated in `demo_bonus.py`:

- **Random delays** — each package has a configurable probability of arriving late
- **ASCII map** — terminal grid showing warehouse, agent, and destination positions
- **Late agent** — add a new agent mid-day and reassign nearby packages to them
- **CSV export** — write the best agent's stats to a spreadsheet-friendly CSV

## Test results

```
[PASS]  data.json                5/5 pkgs    best=A3
[PASS]  test_case_1.json        12/12 pkgs   best=A3
[PASS]  test_case_2.json        10/10 pkgs   best=A1
[PASS]  test_case_3.json         6/6 pkgs    best=A3
[PASS]  test_case_4.json        12/12 pkgs   best=A3
[PASS]  test_case_5.json        10/10 pkgs   best=A3
[PASS]  test_case_6.json         9/9 pkgs    best=A3
[PASS]  test_case_7.json        10/10 pkgs   best=A3
[PASS]  test_case_8.json        11/11 pkgs   best=A2
[PASS]  test_case_9.json         8/8 pkgs    best=A3
[PASS]  test_case_10.json       11/11 pkgs   best=A4

Results: 11/11 passed — all clear ✓
```
