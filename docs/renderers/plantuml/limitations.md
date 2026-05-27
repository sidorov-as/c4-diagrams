# PlantUML Limitations

The PlantUML backend targets C4-PlantUML output, but it does not expose every
C4-PlantUML macro as Python DSL.

## Unsupported C4-PlantUML areas

| Area                                      | Status                                                                   |
|-------------------------------------------|--------------------------------------------------------------------------|
| Sequence diagrams                         | Not exposed by the Python DSL                                            |
| Arbitrary raw C4-PlantUML macros          | Not a public DSL surface                                                 |
| Every C4-PlantUML tag/style macro variant | Use supported render options and extension fields                        |
| Mermaid-specific extension data           | Ignored by default; rejected when strict extension validation is enabled |

## Include behavior

Generated PlantUML source includes the C4-PlantUML standard library from the
remote `plantuml-stdlib/C4-PlantUML` repository by default. The generated source
also supports a `RELATIVE_INCLUDE` PlantUML variable so local builds can point to
a local C4-PlantUML checkout:

```shell
plantuml -DRELATIVE_INCLUDE=/path/to/C4-PlantUML diagram.puml
```

Use a local include path when builds must be reproducible without network access.
Remote rendering depends on the PlantUML server and its ability to fetch remote
includes.
