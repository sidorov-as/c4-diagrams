# Sources

What Compose and Kubernetes manifests give a generator. Facts marked *stated* are fields; facts marked *inferred* are
guesses and follow Rule 4 of `SKILL.md`.

## Docker Compose

Files: `docker-compose.yml`, `compose.yaml`, `compose.*.yaml`, overrides.

| Need              | Source                                                          | Kind     |
|-------------------|-----------------------------------------------------------------|----------|
| Element           | Each key under `services`                                       | stated   |
| Name, alias       | The service key                                                 | stated   |
| Technology        | `image` (name and tag), or `build` context                      | stated   |
| Database or queue | Image name (`postgres`, `redis`, `rabbitmq`) → `ContainerDb` or `ContainerQueue` | inferred |
| Port              | `ports`, `expose`                                               | stated   |
| Relationship      | `depends_on`                                                    | stated that startup depends, inferred that the system calls |
| Relationship      | Environment variables naming another service or holding a URL (`DB_HOST=db`, `http://api:8000`) | inferred |
| Relationship      | `c4.*` labels (`c4.rel.<dep>.label`)                            | stated   |
| Boundary          | `networks`, `profiles`                                          | inferred |

`depends_on` records start order, not who calls whom: label such a relationship "Depends on" and keep it an assumption
unless a `c4.*` label says otherwise. Merge override files in Compose order before reading.

## Kubernetes

Files: YAML with `kind:`; one file may hold several documents (`---`).

| Need              | Source                                                          | Kind     |
|-------------------|-----------------------------------------------------------------|----------|
| Element           | `Deployment`, `StatefulSet`, `DaemonSet`, `CronJob` (one per workload) | stated |
| Technology        | `spec.template.spec.containers[].image`                         | stated   |
| Database          | `StatefulSet` with a known database image                       | inferred |
| Port              | `containers[].ports`, `Service.spec.ports`                      | stated   |
| Boundary          | `metadata.namespace`                                            | stated   |
| Relationship      | `Service.spec.selector` matched to workload `template.metadata.labels`: links a Service to its workload | stated   |
| Relationship      | `Ingress` rule `backend.service.name`: external entry to a Service | stated   |
| Relationship      | Environment variables, `ConfigMap` values with a Service name or URL (`api.default.svc`) | inferred |

A Service is not an element: it names how a workload is reached. Resolve a Service name to its workload through the
selector, then draw the relationship to the workload.

## Helm and kustomize

Read only rendered output, never templates: a template is not valid YAML.

```shell
helm template <release> <chart> -f values.yaml > rendered.yaml
kubectl kustomize <dir> > rendered.yaml
```

Both run locally, but `helm template` may download a chart or dependencies, and `helm dependency update` always does.
Warn the user before running a command that may fetch, and ask first (`c4-diagrams` Rule 4). A chart already in the
repository with vendored dependencies needs no network.

A generator reads the rendered file the same way as plain manifests. For CI, render in the same job, then generate.
