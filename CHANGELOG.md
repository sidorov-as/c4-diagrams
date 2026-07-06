## Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.7.1 (2026-07-06)

### Fix

- **core**: fix alias generation for non-ascii labels
- **docs**: Update D2 link to point to official website
- **docs**: fix link to d2

## 0.7.0 (2026-07-06)

### Feat

- add d2 backend

## 0.6.1 (2026-06-22)

### Feat

- **cli**: add --watch option c4 render/export ([#33](https://github.com/sidorov-as/c4-diagrams/issues/33)).

## 0.6.0 (2026-06-21)

### Feat

- **core**: split the portable C4 model from backend-specific extensions.
- **core**: add backend extension data via `extensions=`, `plantuml=`, and `mermaid=` kwargs.
- **plantuml**: move PlantUML-specific relationships, layouts, indexes, and macros to `c4.contrib.plantuml`.
- **mermaid**: add Mermaid contrib helpers and backend-specific extension validation.
- **converters**: add backend-aware JSON schemas, generated specs, and JSON-to-Python conversion.
- **cli**: resolve renderer backend metadata from JSON targets and reject mismatched renderer selections.
- **docs**: add portable core, backend extension, reusable element, renderer, and example documentation.

### Fix

- **cli**: add Mermaid CLI Puppeteer config and headless options for `c4 export` ([#34](https://github.com/sidorov-as/c4-diagrams/issues/34)).

### Breaking changes

1. `c4.diagrams.core` was split into a package. Internal imports from the old monolithic `c4.diagrams.core` module may need to move to `c4.diagrams.core.components`, `c4.diagrams.core.diagram`, `c4.diagrams.core.enums`, `c4.diagrams.core.relationships`, or `c4.diagrams.core.utils`.
2. PlantUML-specific DSL helpers are no longer part of the portable core API. Import directional relationships, bidirectional relationships, layout helpers, and index helpers from `c4.contrib.plantuml`.
3. Mermaid-specific helper exports are available from `c4.contrib.mermaid`.
4. Renderer-specific element and relationship metadata such as `tags`, `sprite`, `link`, `base_shape`, `index`, and stereotypes should now be passed as backend extension data, for example `plantuml={"tags": ["storage"]}` or `mermaid={"type": "boundary"}`.
5. JSON diagrams are now backend-aware and strict. Use the selected core, PlantUML, or Mermaid schema fields; unknown fields are rejected, and the Python DSL `extensions=` envelope is not accepted in JSON input.
6. PlantUML render option APIs were tightened: several style helpers now use `type_` instead of `technology`, and boundary style update helpers no longer accept `element_name` or `technology`.

This release intentionally remains `0.6.0` instead of a major version while the internal and public APIs continue to stabilize.

## 0.5.2 (2026-04-20)

### Fix

- **cli**: fix export cli args parsing

## 0.5.1 (2026-04-20)

### Fix

- **cli**: fix mermaid and plantuml binary checks

## 0.5.0 (2026-04-20)

### Feat

- **renderers**: add mermaid rendering backend
- **cli**: add mermaid options
- **plantuml**: add [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) to `LocalPlantUMLBackend`.

#### Breaking changes

1. Refactor layout options: replace `c4.renderers.plantuml.layout_options.LayoutOptions` with `c4.renderers.plantuml.options.PlantUMLRenderOptionsBuilder`.


## 0.4.5 (2026-04-04)

### Fix

- **core**: add properties to relationships

## 0.4.4 (2026-04-03)

### Fix

- **renderers**: fix empty values rendering

## 0.4.3 (2026-04-03)

### Fix

- **core**: fix empty string labels (#26)

## 0.4.2 (2026-04-03)

### Fix

- **cli**: add the target file’s import root to sys.path ([#23](https://github.com/sidorov-as/c4-diagrams/issues/23))

## 0.4.1 (2026-03-30)

### Fix

- **core**: fix Relationship typing to improve IDEs autocompletion (#21)

## 0.4.0 (2026-03-22)

### Feat

- **cli**: add json-to-python converters CLI
- **converters**: add json-to-python converters
- **renderers**: replace layout options with render options
- **core**: add constraints for diagram types

## 0.3.0 (2026-02-16)

### Feat

- **core**: improve index macros
- **plantuml**: add new c4 style support

## 0.2.0 (2026-02-15)

### Feat

- **core**: refactor init args for diagram components
- **cli**: add c4 cli

## 0.1.2 (2026-02-01)

### Fix

- **plantuml**: minor improvements

## 0.1.1 (2026-01-26)

### Fix

- **core**: minor improvements

## 0.1.0 (2026-01-22)

### Feat

- **core**: add new dsl for relations

## 0.0.4 (2026-01-22)

### Fix

- **core**: remove invalid chars from generated alias

## 0.0.3 (2026-01-12)

### Refactor

- add PlantUML renderer imports (#5)

## 0.0.2 (2026-01-11)

### Feat

- add base diagrams support
- add PlantUML rendering backend

## 0.0.1 (2026-01-11)

### Feat

- init
