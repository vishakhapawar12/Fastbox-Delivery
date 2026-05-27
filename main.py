"""
Usage:
    python main.py                             # data.json -> report.json
    python main.py input.json                  # custom input
    python main.py input.json output.json      # custom input + output
    python main.py input.json output.json --csv  # also export top performer CSV
"""

import sys
import os
from delivery_system import run


def main():
    args = sys.argv[1:]

    export_csv = "--csv" in args
    args = [a for a in args if a != "--csv"]

    input_file  = args[0] if args else "data.json"
    output_file = args[1] if len(args) > 1 else "report.json"

    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' not found.")
        sys.exit(1)

    run(input_file, output_file, verbose=True, export_csv=export_csv)


if __name__ == "__main__":
    main()
