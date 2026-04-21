from __future__ import annotations

import argparse
import json
from pathlib import Path

from .design_md import generate_design_md
from .extractor import extract_pptx
from .storage import save_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract design guidance from PPTX decks")
    parser.add_argument("pptx_path", type=Path, nargs="?", help="Path to .pptx file")
    parser.add_argument("--output", "-o", type=Path, default=Path("design.md"), help="Output markdown path")
    parser.add_argument("--json", type=Path, default=None, help="Optional analysis JSON output path")
    parser.add_argument("--batch-dir", type=Path, default=None, help="Directory containing .pptx files for batch mode")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Output directory for batch mode artifacts",
    )
    parser.add_argument(
        "--persist-run",
        action="store_true",
        help="Persist run artifacts into backend/runs with generated run_id",
    )
    return parser


def _write_single(pptx_path: Path, output: Path, json_path: Path | None, persist_run: bool) -> None:
    analysis = extract_pptx(pptx_path)
    design_md = generate_design_md(analysis)
    output.write_text(design_md, encoding="utf-8")
    if json_path:
        json_path.write_text(json.dumps(analysis.model_dump(), indent=2), encoding="utf-8")

    print(f"Wrote {output}")
    if json_path:
        print(f"Wrote {json_path}")
    if persist_run:
        run_id = save_run(pptx_path.name, design_md, analysis)
        print(f"Persisted run {run_id}")


def _run_batch(batch_dir: Path, output_dir: Path, persist_run: bool) -> None:
    files = sorted(batch_dir.glob("*.pptx"))
    if not files:
        raise SystemExit(f"No .pptx files found in {batch_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    for pptx_path in files:
        analysis = extract_pptx(pptx_path)
        design_md = generate_design_md(analysis)
        stem = pptx_path.stem
        md_path = output_dir / f"{stem}.design.md"
        json_path = output_dir / f"{stem}.analysis.json"
        md_path.write_text(design_md, encoding="utf-8")
        json_path.write_text(json.dumps(analysis.model_dump(), indent=2), encoding="utf-8")
        print(f"Wrote {md_path}")
        print(f"Wrote {json_path}")
        if persist_run:
            run_id = save_run(pptx_path.name, design_md, analysis)
            print(f"Persisted run {run_id} for {pptx_path.name}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.batch_dir:
        _run_batch(args.batch_dir, args.output_dir, args.persist_run)
        return

    if not args.pptx_path:
        parser.error("Provide a .pptx path or use --batch-dir")
    if args.pptx_path.suffix.lower() != ".pptx":
        parser.error("Input must be a .pptx file")

    _write_single(args.pptx_path, args.output, args.json, args.persist_run)


if __name__ == "__main__":
    main()
