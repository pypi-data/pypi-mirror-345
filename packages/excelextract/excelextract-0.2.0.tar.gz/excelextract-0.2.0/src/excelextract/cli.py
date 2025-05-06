#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

from .io import loopFiles

def main():
    try:
        parser = argparse.ArgumentParser(
            prog="excelextract",
            description=(
                "Extract structured CSV data from Excel (.xlsx) files using a declarative JSON configuration.\n\n"
                "This tool is designed for researchers and survey teams working with standardized Excel forms. "
                "You define what to extract via a JSON file — no programming required."
            ),
            epilog=(
                "Example usage:\n"
                "  excelextract config.json\n\n"
                "For documentation and examples, see: https://github.com/philippe554/excelextract"
            ),
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument("config", type=Path, help="Path to the JSON configuration file.")
        parser.add_argument("-i", "--input", type=Path, help="Input glob, overrides config.")
        parser.add_argument("-o", "--output", type=Path, help="Output folder, prefix for output files in the config.")

        args = parser.parse_args()

        if not args.config.exists():
            raise FileNotFoundError(f"Config file {args.config} does not exist.")

        try:
            with args.config.open("r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Config file {args.config} is not a valid JSON file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error reading config file {args.config}: {e}")

        if "exports" not in config:
            raise ValueError("Config file does not contain 'exports' key.")
        exports = config["exports"]

        for exportConfig in exports:
            if args.input:
                exportConfig["input"] = str(args.input)
            
            if "output" not in exportConfig:
                exportConfig["output"] = "output.csv"
            if args.output:
                exportConfig["output"] = args.output / exportConfig["output"]

            loopFiles(exportConfig)

        print("Processing completed.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
