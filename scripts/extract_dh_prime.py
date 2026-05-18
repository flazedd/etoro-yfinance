"""Print the DH prime from a PEM dhparam file as a hex string.

IBind's OAuth 1.0a needs IBIND_OAUTH1A_DH_PRIME as hex, not a PEM path.
Run once and copy stdout into .env. Uses the system `openssl` binary so it
doesn't require any extra Python deps.

    uv run python scripts/extract_dh_prime.py ~/ibkr-oauth/dhparam.pem
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: extract_dh_prime.py <path-to-dhparam.pem>", file=sys.stderr)
        sys.exit(2)
    pem_path = Path(sys.argv[1]).expanduser()
    if not pem_path.is_file():
        print(f"no such file: {pem_path}", file=sys.stderr)
        sys.exit(2)

    # `openssl asn1parse` on a dhparam file yields:
    #   SEQUENCE
    #     INTEGER  :<prime hex>
    #     INTEGER  :02         (the generator)
    # We want the first INTEGER's hex value.
    result = subprocess.run(
        ["openssl", "asn1parse", "-in", str(pem_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    integers = [
        line.rpartition(":")[2].strip() for line in result.stdout.splitlines() if "INTEGER" in line
    ]
    if not integers:
        print(f"no INTEGER found in asn1parse output:\n{result.stdout}", file=sys.stderr)
        sys.exit(2)
    print(integers[0])


if __name__ == "__main__":
    main()
