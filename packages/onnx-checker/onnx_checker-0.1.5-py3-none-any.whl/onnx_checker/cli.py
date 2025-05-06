"""Command‑line interface for **onnx-checker**.

After installing the package, this module is exposed as the console‑script
`onnxcheck` (configured in pyproject.toml).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .checker import (
    Checker,
    iter_profiles,
    load_profile,
    print_model_summary,
    print_summary,
)

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="onnxcheck",
        description="Inspect an ONNX model and check operator compatibility with hardware profiles.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("model", help="Path to .onnx model file")
    p.add_argument(
        "-p",
        "--hardware",
        nargs="*",
        help="Profile name(s) (e.g. kl720) or JSON file path(s). Omit to scan all built‑in profiles.",
    )
    p.add_argument("--markdown", action="store_true", help="Output report(s) as Markdown")
    return p

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: List[str] | None = None) -> None:  # pragma: no cover
    args = _build_parser().parse_args(argv)
    model_path = Path(args.model)

    # Show model IO + detect dynamic axes
    dynamic = print_model_summary(model_path)

    # Determine which profiles to scan
    profile_keys = args.hardware if args.hardware else iter_profiles()

    for key in profile_keys:
        profile = load_profile(key)

        # Warn if KL* profile & dynamic dims present
        if dynamic and profile.get("name", "").lower().startswith("kl"):
            print(f"[WARNING] Model uses dynamic axes which are NOT supported on {profile['name']}.")

        report = Checker(model_path, profile).run()
        print(report.to_markdown() if args.markdown else report)
        print_summary(report)
        print()


if __name__ == "__main__":  # pragma: no cover
    main()
