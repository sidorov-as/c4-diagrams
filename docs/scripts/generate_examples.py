from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent
EXAMPLES_DIR = DOCS_DIR / "assets" / "examples"
JSON_EXAMPLES_DIR = EXAMPLES_DIR / "json"
PYTHON_EXAMPLES_DIR = EXAMPLES_DIR / "python"
COMMON_PYTHON_EXAMPLES_DIR = PYTHON_EXAMPLES_DIR / "common"
CUSTOM_PYTHON_EXAMPLES_DIR = PYTHON_EXAMPLES_DIR / "custom"
REPO_ROOT = DOCS_DIR.parent
NO_BYTECODE_ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
TEXT_ARTIFACT_SUFFIXES = {".mmd", ".puml", ".py"}

PLANTUML = "plantuml"
MERMAID = "mermaid"

# Core examples are JSON-only; only these backends have rendered source/images.
RENDERABLE_BACKEND_SOURCE_SUFFIX = {
    PLANTUML: ".puml",
    MERMAID: ".mmd",
}

BACKEND_EXPORT_ARGS = {
    PLANTUML: ["--plantuml-skinparam-dpi=200"],
    MERMAID: ["--mermaid-puppeteer-headless=false", "--mermaid-scale-factor=5"],
}


def run_c4(args: Iterable[str]) -> None:
    subprocess.run(  # noqa: S603
        [sys.executable, "-m", "c4", *args],
        cwd=REPO_ROOT,
        env=NO_BYTECODE_ENV,
        check=True,
    )


def ensure_text_artifact_newline(path: Path) -> None:
    if path.suffix not in TEXT_ARTIFACT_SUFFIXES or not path.exists():
        return

    content = path.read_text(encoding="utf-8")
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def iter_json_examples() -> Iterable[tuple[str, Path]]:
    for backend in RENDERABLE_BACKEND_SOURCE_SUFFIX:
        backend_dir = JSON_EXAMPLES_DIR / backend
        for json_file in sorted(backend_dir.glob("*.json")):
            yield backend, json_file


def iter_common_python_examples() -> Iterable[Path]:
    yield from sorted(COMMON_PYTHON_EXAMPLES_DIR.glob("*.py"))


def iter_custom_python_examples() -> Iterable[tuple[str, Path]]:
    for backend in RENDERABLE_BACKEND_SOURCE_SUFFIX:
        backend_dir = CUSTOM_PYTHON_EXAMPLES_DIR / backend
        for python_file in sorted(backend_dir.glob("*.py")):
            yield backend, python_file


def generate_json_example_sources(*, include_images: bool) -> None:
    for backend, json_file in iter_json_examples():
        backend_flag = f"--{backend}"
        source_suffix = RENDERABLE_BACKEND_SOURCE_SUFFIX[backend]
        backend_export_args = BACKEND_EXPORT_ARGS.get(backend, [])
        output_file = EXAMPLES_DIR / backend / json_file.name

        run_c4([
            "convert",
            str(json_file),
            "--json-to-py",
            "-o",
            str(output_file.with_suffix(".py")),
        ])
        ensure_text_artifact_newline(output_file.with_suffix(".py"))

        run_c4([
            "render",
            str(json_file),
            backend_flag,
            "-o",
            str(output_file.with_suffix(source_suffix)),
        ])
        ensure_text_artifact_newline(output_file.with_suffix(source_suffix))

        if include_images:
            run_c4([
                "export",
                str(json_file),
                backend_flag,
                "-f",
                "png",
                "-o",
                str(output_file.with_suffix(".png")),
                *backend_export_args,
            ])


def generate_common_example_sources(*, include_images: bool) -> None:
    for python_file in iter_common_python_examples():
        for backend, source_suffix in RENDERABLE_BACKEND_SOURCE_SUFFIX.items():
            backend_flag = f"--{backend}"
            backend_export_args = BACKEND_EXPORT_ARGS.get(backend, [])
            output_file = EXAMPLES_DIR / backend / python_file.name

            run_c4([
                "render",
                str(python_file),
                backend_flag,
                "-o",
                str(output_file.with_suffix(source_suffix)),
            ])
            ensure_text_artifact_newline(output_file.with_suffix(source_suffix))

            if include_images:
                run_c4([
                    "export",
                    str(python_file),
                    backend_flag,
                    "-f",
                    "png",
                    "-o",
                    str(output_file.with_suffix(".png")),
                    *backend_export_args,
                ])


def generate_custom_example_sources(*, include_images: bool) -> None:
    for backend, python_file in iter_custom_python_examples():
        backend_flag = f"--{backend}"
        source_suffix = RENDERABLE_BACKEND_SOURCE_SUFFIX[backend]
        backend_export_args = BACKEND_EXPORT_ARGS.get(backend, [])
        output_file = EXAMPLES_DIR / backend / python_file.name

        run_c4([
            "render",
            str(python_file),
            backend_flag,
            "-o",
            str(output_file.with_suffix(source_suffix)),
        ])
        ensure_text_artifact_newline(output_file.with_suffix(source_suffix))

        if include_images:
            run_c4([
                "export",
                str(python_file),
                backend_flag,
                "-f",
                "png",
                "-o",
                str(output_file.with_suffix(".png")),
                *backend_export_args,
            ])


def generate_diagram_specs() -> None:
    subprocess.run(  # noqa: S603
        [sys.executable, "-m", "docs.scripts.generate_diagram_spec_docs"],
        cwd=REPO_ROOT,
        env=NO_BYTECODE_ENV,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate docs example artifacts and JSON schema docs.",
    )
    parser.add_argument(
        "--skip-images",
        action="store_true",
        help=(
            "Regenerate Python, JSON-derived text sources, and schema docs "
            "without exporting PNG images."
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Regenerate all docs example artifacts and JSON schema docs.",
    )
    parser.add_argument(
        "--generate-json-example-sources",
        "--json-example-sources",
        dest="json_example_sources",
        action="store_true",
        help="Regenerate artifacts derived from JSON examples.",
    )
    parser.add_argument(
        "--generate-common-example-sources",
        "--common-example-sources",
        dest="common_example_sources",
        action="store_true",
        help="Regenerate artifacts derived from common Python examples.",
    )
    parser.add_argument(
        "--generate-custom-example-sources",
        "--custom-example-sources",
        dest="custom_example_sources",
        action="store_true",
        help="Regenerate artifacts derived from custom Python examples.",
    )
    parser.add_argument(
        "--generate-diagram-specs",
        "--diagram-specs",
        dest="diagram_specs",
        action="store_true",
        help="Regenerate JSON diagram schema docs.",
    )
    args = parser.parse_args()

    generator_selected = (
        args.all
        or args.json_example_sources
        or args.common_example_sources
        or args.custom_example_sources
        or args.diagram_specs
    )
    if not generator_selected:
        parser.error("select at least one generator flag or use --all")

    if args.all or args.json_example_sources:
        generate_json_example_sources(include_images=not args.skip_images)

    if args.all or args.common_example_sources:
        generate_common_example_sources(include_images=not args.skip_images)

    if args.all or args.custom_example_sources:
        generate_custom_example_sources(include_images=not args.skip_images)

    if args.all or args.diagram_specs:
        generate_diagram_specs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
