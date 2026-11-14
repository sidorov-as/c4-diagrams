# Diagram from a codebase

To keep a diagram up to date from Compose or Kubernetes manifests, use the `c4-pipeline` skill.

Done when every element and relationship is traced to a source or labeled an assumption, and the user has confirmed the
uncertain boundaries.

1. **Choose the level** from the request: system context, container, component, deployment or dynamic. If several views
   of one model are wanted, or the target is Structurizr or LikeC4, plan a `Workspace` or `Project`; otherwise a
   portable diagram per level.
2. **Inspect sources** for that level:
    - Containers: `docker-compose*.yml`, Kubernetes manifests, Helm charts, Dockerfiles, `Procfile`, top-level packages
      or services, `pyproject.toml`/`package.json`/`go.mod` per service.
    - Components: package and import structure inside one container, framework entry points (routers, handlers,
      consumers).
    - External systems and datastores: environment files and config keys, client libraries, connection strings, message
      brokers.
    - Deployment: Terraform, Helm, CI deploy jobs, orchestration files.
    - Dynamic: one user story traced through handlers and outbound calls.
3. **Draft** elements with label, description and technology, then relationships with labels and technology.
4. **Label assumptions.** Mark every inferred fact (an external system seen only in config, a guessed protocol, a
   grouping) as an assumption in a comment and in your reply.
5. **Confirm boundaries.** Ask about anything unclear: where the system boundary runs, whether two services are one
   container, what is external.
6. **Write the Python** following [python-dsl.md](python-dsl.md) or [whole-architecture.md](whole-architecture.md),
   render source with `c4 render`, and show it. Export an image only if asked, under the rules in `SKILL.md`.
