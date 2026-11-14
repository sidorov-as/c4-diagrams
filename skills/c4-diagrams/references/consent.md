# Consent and network access

## Tier A: the diagram source leaves the machine

- Kroki: any `--*-backend kroki`, and `--structurizr-backend kroki` (the Structurizr default). URL from `--kroki-url`,
  `KROKI_SERVER_URL`, else `https://kroki.io`.
- PlantUML server: `--plantuml-backend remote`. URL from `--plantuml-server-url`, `PLANTUML_SERVER_URL`, else
  `https://www.plantuml.com/plantuml`.

Before running: name the server, state that the diagram source will be sent there, wait for an explicit yes. Ask again
for every new command.

Exempt: a server the user declared self-hosted and allowed in the `## c4-diagrams` settings
block ([settings.md](settings.md)).

A failing local backend does not trigger a remote one. Report the failure, then offer remote only as a choice that needs
the yes above.

## Tier B: network access without sending the model

Warn before running; the model is not sent but the machine fetches over the network:

- `npx likec4@<version> ...` or any `npx` call: downloads npm packages.
- `pip install`, `npm install`, `brew install`, `apt install`, downloading a PlantUML jar: ask for approval, then run.
- Local PlantUML with `--plantuml-use-bundled-c4-plantuml false`: fetches C4-PlantUML `!include` files from
  `raw.githubusercontent.com`. Rendered `.puml` source also contains remote `!include` URLs by design; mention it when
  the user will run that source.
- Playwright Chromium install (LikeC4, Structurizr local image export).

The default export keeps C4-PlantUML includes bundled (`--plantuml-use-bundled-c4-plantuml` defaults to true), so a
plain local PlantUML export needs no network.
