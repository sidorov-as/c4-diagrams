# LikeC4 Renderers

## LikeC4Renderer

[`LikeC4Renderer`][c4.contrib.likec4.renderer.LikeC4Renderer] converts a [`Project`][c4.contrib.likec4.Project] to LikeC4 source. It validates the project
first and raises [`LikeC4ValidationError`][c4.contrib.likec4.renderer.LikeC4ValidationError] with the element, step or view that
is wrong.

```python
from c4.contrib.likec4 import Project
from c4.contrib.likec4.renderer import LikeC4Renderer

project = Project("Shop")

source = LikeC4Renderer().render(project)   # or project.render()
project.save("architecture.c4")
```

Blocks appear in a fixed order (`specification`, `model`, `deployment`,
`views`) and empty blocks are omitted, so output is stable between runs.

## LocalLikeC4Backend

[`LocalLikeC4Backend`][c4.contrib.likec4.renderer.LocalLikeC4Backend] exports one view as an image through the `likec4` CLI. It
writes the source to a temporary directory, runs
`likec4 export png|jpg --flat -o <out> -f <view-key> <dir>`, returns the bytes
and removes the directory.

```python
from c4.contrib.likec4 import Project
from c4.contrib.likec4.renderer import LikeC4Renderer, LocalLikeC4Backend

project = Project("Shop")

renderer = LikeC4Renderer(
    backend=LocalLikeC4Backend(),
    view_key="index",
)
# Needs the likec4 CLI and a view with the key "index":
# renderer.render_file(project, "index.png", format="png")
```

- `likec4_bin` is a command name, a path, or a command prefix such as
  `["npx", "likec4@1.60.0"]`. The default is `likec4`, or the `LIKEC4_BIN`
  environment variable.
- `timeout_seconds` defaults to `30` (`RENDERING_TIMEOUT_SECONDS`).
- Formats are PNG and JPG; others raise `ValueError`.

### Choosing the view

The view comes from `LikeC4Renderer(view_key=...)`, then `Project(view_key=...)`,
then the project's only view. If there are several views and none is chosen,
`LikeC4BackendConfigurationError` is raised before the CLI runs.

### Errors

| Situation                              | Exception                            |
|----------------------------------------|--------------------------------------|
| `likec4` not found                     | `LikeC4BackendConfigurationError`    |
| Playwright Chromium not installed      | `LikeC4BackendConfigurationError`    |
| No view key, several views             | `LikeC4BackendConfigurationError`    |
| Non-zero exit code, with CLI output    | `LikeC4LocalRenderingError`          |
| Timeout                                | `LikeC4LocalRenderingError`          |
| Unknown view key (no file produced)    | `LikeC4LocalRenderingError`          |
| Unsupported format                     | `ValueError`                         |

## CLI

```bash
# text, no external tools
c4 render project.py --likec4 -o architecture.c4

# image
c4 export project.py --likec4 --likec4-view-key index -f png -o index.png

# a pinned CLI through npx
c4 export project.py --likec4 --likec4-bin "npx likec4@1.60.0" \
  --likec4-view-key index -f jpg -o index.jpg
```

A JSON file with `"backend": "likec4"` selects this renderer automatically; see
the [LikeC4 project spec](../../converters/json/specs/likec4.project.md).
