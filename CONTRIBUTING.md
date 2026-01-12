# Contributing to `c4-diagrams`

Contributions are very welcome and greatly appreciated.
Every little bit helps — whether it’s code, documentation, bug reports, or ideas.

This guide explains **how you can contribute** and **how to set up the project for local development**.

---

## Ways to Contribute

### Issues: Bugs, Questions, and Feature Requests

The primary way to communicate feedback is via
[GitHub issues](https://github.com/sidorov-as/c4-diagrams/issues).

When opening an issue, please include as much context as possible.

**For bug reports:**

- Operating system and version
- Python version
- Relevant tooling versions (`uv`, `tox`, etc.)
- Clear steps to reproduce
- Expected vs actual behavior

**For feature requests:**

- What problem you are trying to solve
- A short description of the proposed solution
- Keep the scope as small and focused as possible

This is a volunteer-driven project — well-scoped and well-explained issues are much more
likely to be addressed 🙂

---

### Code Contributions

You can contribute by:

- Fixing bugs
- Implementing new features
- Improving performance or internal structure
- Adding or improving tests

Issues labeled **`bug`**, **`enhancement`**, or **`help wanted`** are especially good starting points.

---

### Documentation

Documentation contributions are always welcome:

- Official documentation pages
- Docstrings
- Examples
- Blog posts or articles referencing `c4-diagrams`

---

## Development Setup

This project uses **`uv`** for dependency management.

> This guide assumes you already have **Git** and **uv** installed.

### 1. Fork and clone the repository

```bash
git clone git@github.com:YOUR_NAME/c4-diagrams.git
cd c4-diagrams
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Install pre-commit hooks

Pre-commit runs formatters and linters automatically before each commit.

```bash
uv run pre-commit install
```

---

## Development Workflow

### 1. Create a feature branch

```bash
git checkout -b name-of-your-feature-or-fix
```

### 2. Make your changes

- Follow existing project structure and style
- Add or update tests for any behavioral change
- Keep commits focused and incremental

### 3. Run checks locally

Formatting and static checks:

```bash
make check
```

Unit tests:

```bash
make test
```

### 4. (Optional) Run tox

```bash
tox
```

This runs the test suite across multiple Python versions.

> **Note:**
> Running `tox` locally requires multiple Python versions to be installed.
> This step is mandatory in CI, but optional for local development.

---

## Commit Message Guidelines

This project follows **[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)**.

### Commit Message Format

```
<type>(<scope>): <short summary>
```

- Use **present tense**
- Do **not** capitalize the summary
- Do **not** end with a period

### Commit Types

| type     | description                                       |
|----------|---------------------------------------------------|
| feat     | New features                                      |
| fix      | Bug fixes                                         |
| docs     | Documentation-only changes                        |
| style    | Formatting, whitespace, etc. (no behavior change) |
| refactor | Code changes without bug fixes or features        |
| perf     | Performance improvements                          |
| test     | Adding or fixing tests                            |
| build    | Build system or dependency changes                |
| ci       | CI configuration changes                          |
| chore    | Other non-code changes                            |
| revert   | Revert a previous commit                          |

### Examples

```bash
git commit -m "fix(renderer): handle empty boundary labels"
git commit -m "docs(readme): add minimal usage example"
git commit -m "refactor(core): simplify relationship rendering"
```

---

## Submitting a Pull Request

1. Push your branch to GitHub:

```bash
git push origin name-of-your-feature-or-fix
```

2. Open a Pull Request via the GitHub UI.

---

## Pull Request Checklist

Before submitting, please ensure that:

- [ ] Tests are included or updated
- [ ] Documentation is updated if behavior or APIs changed
- [ ] `make check` passes
- [ ] `make test` passes
- [ ] Commit messages follow Conventional Commits

---

Thank you for contributing to **c4-diagrams** 🚀
