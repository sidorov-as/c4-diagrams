## Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
