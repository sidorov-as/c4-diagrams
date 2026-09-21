from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
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
TEXT_ARTIFACT_SUFFIXES = {".c4", ".d2", ".dsl", ".mmd", ".puml", ".py"}

D2 = "d2"
PLANTUML = "plantuml"
MERMAID = "mermaid"
STRUCTURIZR = "structurizr"
LIKEC4 = "likec4"

# Core examples are JSON-only; only these backends have rendered source/images.
RENDERABLE_BACKEND_SOURCE_SUFFIX = {
    D2: ".d2",
    PLANTUML: ".puml",
    MERMAID: ".mmd",
    STRUCTURIZR: ".dsl",
    LIKEC4: ".c4",
}

# Structurizr and LikeC4 render whole workspaces, not the portable diagrams
# used by the common examples.
PORTABLE_BACKENDS = (D2, PLANTUML, MERMAID)

BACKEND_EXPORT_ARGS = {
    PLANTUML: ["--plantuml-skinparam-dpi=200"],
    MERMAID: ["--mermaid-puppeteer-headless=false", "--mermaid-scale-factor=5"],
    D2: ["--d2-layout=elk"],
}

# Structurizr and LikeC4 custom examples define a single view with this key.
CUSTOM_EXAMPLE_VIEW_KEY = "components"

D2_LAYOUT_VARIANTS = ("dagre", "elk")
D2_LAYOUT_VARIANT_EXAMPLE_NAMES = {
    "component-diagram",
    "container-diagram",
    "deployment-diagram",
    "dynamic-diagram",
    "dynamic-diagram.sequence",
    "system-context-diagram",
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
    lines = [line.rstrip() for line in content.rstrip().splitlines()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
        output_file.parent.mkdir(parents=True, exist_ok=True)

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
            if backend == STRUCTURIZR:
                # No whole-workspace image: every view gets its own PNG.
                generate_structurizr_view_images(
                    source_file=output_file.with_suffix(source_suffix),
                    output_file=output_file,
                    view_keys=[
                        view["key"]
                        for view in json.loads(
                            json_file.read_text(encoding="utf-8")
                        )["views"]["items"]
                    ],
                )
            else:
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

            if backend == LIKEC4:
                generate_likec4_view_images(
                    json_file=json_file,
                    output_file=output_file,
                )
                generate_likec4_viewer_bundle(
                    source_file=output_file.with_suffix(source_suffix),
                    output_file=output_file.with_suffix(".viewer.js"),
                    prefix=f"likec4-{json_file.stem.removeprefix('project.')}",
                )

            if (
                backend == D2
                and json_file.stem in D2_LAYOUT_VARIANT_EXAMPLE_NAMES
            ):
                generate_d2_layout_variant_images(
                    json_file=json_file,
                    output_file=output_file,
                )


def generate_structurizr_view_images(
    *,
    source_file: Path,
    output_file: Path,
    view_keys: Iterable[str],
) -> None:
    """
    Generate one PNG per view of a Structurizr workspace example.

    ``structurizr export -f png`` renders every view of a DSL workspace in one
    run (``<view-key>.png`` plus a ``<view-key>-key.png`` legend, which is
    dropped). Images are written as ``<example>.<view-key>.png`` for
    docs/examples/structurizr/structurizr.md.
    """
    with tempfile.TemporaryDirectory() as export_dir:
        subprocess.run(  # noqa: S603
            [  # noqa: S607
                "structurizr",
                "export",
                "-w",
                str(source_file),
                "-f",
                "png",
                "-o",
                export_dir,
            ],
            cwd=REPO_ROOT,
            check=True,
        )
        for view_key in view_keys:
            shutil.copy(
                Path(export_dir) / f"{view_key}.png",
                output_file.with_suffix(f".{view_key}.png"),
            )


def generate_likec4_view_images(*, json_file: Path, output_file: Path) -> None:
    """
    Generate one PNG per view of a LikeC4 project example.

    The default view keeps the plain example name; the others are written as
    ``<example>.<view-key>.png`` for docs/examples/likec4/likec4.md.
    """
    views = json.loads(json_file.read_text(encoding="utf-8"))["views"]["items"]
    for view in views:
        run_c4([
            "export",
            str(json_file),
            f"--{LIKEC4}",
            "--likec4-view-key",
            view["key"],
            "-f",
            "png",
            "-o",
            str(output_file.with_suffix(f".{view['key']}.png")),
        ])


def generate_likec4_viewer_bundle(
    *,
    source_file: Path,
    output_file: Path,
    prefix: str,
) -> None:
    """
    Generate the LikeC4 web component bundle for the interactive docs viewer.

    The bundle registers ``<{prefix}-view>``; it is loaded lazily by
    docs/assets/javascripts/likec4-viewer.js.
    """
    with tempfile.TemporaryDirectory() as workspace:
        shutil.copy(source_file, workspace)
        subprocess.run(  # noqa: S603
            [  # noqa: S607
                "likec4",
                "codegen",
                "webcomponent",
                workspace,
                "-o",
                str(output_file),
                "-w",
                prefix,
            ],
            cwd=REPO_ROOT,
            check=True,
        )


def generate_d2_layout_variant_images(
    *,
    json_file: Path,
    output_file: Path,
) -> None:
    """
    Generate D2 PNG variants for the layout tabs in docs/examples/d2/d2.md.
    """
    for layout in D2_LAYOUT_VARIANTS:
        run_c4([
            "export",
            str(json_file),
            "--d2",
            "-f",
            "png",
            "-o",
            str(output_file.with_suffix(f".{layout}.png")),
            f"--d2-layout={layout}",
        ])


def generate_common_example_sources(*, include_images: bool) -> None:
    for python_file in iter_common_python_examples():
        for backend in PORTABLE_BACKENDS:
            source_suffix = RENDERABLE_BACKEND_SOURCE_SUFFIX[backend]
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
    backend_export_args = {
        PLANTUML: ["--plantuml-skinparam-dpi=100"],
        MERMAID: [
            "--mermaid-puppeteer-headless=false",
            "--mermaid-scale-factor=5",
        ],
        D2: ["--d2-layout=elk"],
    }

    for backend, python_file in iter_custom_python_examples():
        backend_flag = f"--{backend}"
        source_suffix = RENDERABLE_BACKEND_SOURCE_SUFFIX[backend]
        export_args = backend_export_args.get(backend, [])
        output_file = EXAMPLES_DIR / backend / python_file.name

        run_c4([
            "render",
            str(python_file),
            backend_flag,
            "-o",
            str(output_file.with_suffix(source_suffix)),
        ])
        ensure_text_artifact_newline(output_file.with_suffix(source_suffix))

        if not include_images:
            continue

        if backend == STRUCTURIZR:
            generate_structurizr_view_images(
                source_file=output_file.with_suffix(source_suffix),
                output_file=output_file,
                view_keys=[CUSTOM_EXAMPLE_VIEW_KEY],
            )
            continue

        run_c4([
            "export",
            str(python_file),
            backend_flag,
            *(
                ["--likec4-view-key", CUSTOM_EXAMPLE_VIEW_KEY]
                if backend == LIKEC4
                else []
            ),
            "-f",
            "png",
            "-o",
            str(output_file.with_suffix(".png")),
            *export_args,
        ])
        if backend == LIKEC4:
            generate_likec4_viewer_bundle(
                source_file=output_file.with_suffix(source_suffix),
                output_file=output_file.with_suffix(".viewer.js"),
                prefix=f"likec4-{python_file.stem}",
            )


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
