"""Console script wrapper for 'osql' — convenience for harlequin with Oracle adapter."""

import subprocess
import sys


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("Usage: osql <tns_alias> [SQL ...]", file=sys.stderr)
        print("Wrapper for 'harlequin --adapter oracle --tns <alias>'", file=sys.stderr)
        sys.exit(1)
    subprocess.run(
        ["harlequin", "--adapter", "oracle", "--tns", sys.argv[1], *sys.argv[2:]],
        check=True,
    )


if __name__ == "__main__":
    main()
