from __future__ import annotations

from pathlib import Path

from generate_examples import (
    BACKEND_EXPORT_ARGS,
    D2,
    DOCS_DIR,
    LIKEC4,
    MERMAID,
    PLANTUML,
    STRUCTURIZR,
    ensure_text_artifact_newline,
    generate_structurizr_view_images,
    run_c4,
)

OVERVIEW_DIR = DOCS_DIR / "assets" / "overview"
PORTABLE_SOURCE = OVERVIEW_DIR / "overview.py"
PLANTUML_LR_SOURCE = OVERVIEW_DIR / "overview.plantuml.py"
WORKSPACE_SOURCE = OVERVIEW_DIR / "overview.workspace.py"
PROJECT_SOURCE = OVERVIEW_DIR / "overview.project.py"

PORTABLE_SOURCE_SUFFIX = {D2: ".d2", PLANTUML: ".puml", MERMAID: ".mmd"}


def render(source: Path, backend: str, output: Path) -> None:
    run_c4(["render", str(source), f"--{backend}", "-o", str(output)])
    ensure_text_artifact_newline(output)


def export_png(source: Path, backend: str, output: Path) -> None:
    run_c4([
        "export",
        str(source),
        f"--{backend}",
        "-f",
        "png",
        "-o",
        str(output),
        *BACKEND_EXPORT_ARGS.get(backend, []),
    ])


def generate_portable() -> None:
    # The PlantUML image is the default (top-down) export used by the README;
    # the home page shows the left-right variant instead.
    for backend, suffix in PORTABLE_SOURCE_SUFFIX.items():
        if backend != PLANTUML:
            render(
                PORTABLE_SOURCE, backend, PORTABLE_SOURCE.with_suffix(suffix)
            )
        export_png(
            PORTABLE_SOURCE,
            backend,
            PORTABLE_SOURCE.with_suffix(f".{backend}.png"),
        )


def generate_plantuml_left_right() -> None:
    # Same model with PlantUML `RelRight` relationships (left-to-right).
    render(PLANTUML_LR_SOURCE, PLANTUML, OVERVIEW_DIR / "overview.puml")
    export_png(
        PLANTUML_LR_SOURCE,
        PLANTUML,
        PLANTUML_LR_SOURCE.with_name("overview.plantuml.lr.png"),
    )


def generate_structurizr() -> None:
    dsl = WORKSPACE_SOURCE.with_suffix(".dsl")
    render(WORKSPACE_SOURCE, STRUCTURIZR, dsl)
    generate_structurizr_view_images(
        source_file=dsl,
        output_file=dsl,
        view_keys=["landscape"],
    )


def generate_likec4() -> None:
    source = PROJECT_SOURCE.with_suffix(".c4")
    render(PROJECT_SOURCE, LIKEC4, source)
    export_png(PROJECT_SOURCE, LIKEC4, PROJECT_SOURCE.with_suffix(".png"))


def main() -> int:
    generate_portable()
    generate_plantuml_left_right()
    generate_structurizr()
    generate_likec4()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
