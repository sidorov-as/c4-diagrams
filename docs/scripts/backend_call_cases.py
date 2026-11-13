"""Python call -> DSL cases shown in the Structurizr and LikeC4 docs.

This module is the single source for the "Python call -> generated DSL"
tables. ``generate_backend_reference.py`` writes them into the pages, and the
docs tests render every case and check that the fragment shown is really part
of the output, so a table cannot drift from the renderer.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    """One row of a call -> DSL table.

    Attributes:
        call: Python shown in the docs and executed last.
        dsl: DSL fragment shown in the docs; every line must appear, in
            order and consecutive, in the rendered output (indentation is
            ignored).
        setup: Hidden Python executed before ``call``.

    ``call`` may rebind ``workspace`` or define ``renderer``; otherwise a
    default workspace and renderer are used.
    """

    call: str
    dsl: str
    setup: str = ""


STRUCTURIZR_IMPORTS = """
from c4.contrib.structurizr import *
from c4.contrib.structurizr.renderer import (
    LocalStructurizrBackend,
    StructurizrRenderer,
    StructurizrRenderOptions,
)
"""

STRUCTURIZR_ELEMENTS = """
customer = model.Person("Customer", alias="customer")
shop = model.SoftwareSystem("Shop", alias="shop")
api = model.Container("API", alias="api", owner=shop)
"""

STRUCTURIZR_DEPLOYMENT = (
    STRUCTURIZR_ELEMENTS
    + """
live = model.DeploymentEnvironment("Live")
server = live.DeploymentNode("Server", alias="server")
"""
)

STRUCTURIZR_CASES: dict[str, tuple[Case, ...]] = {
    "structurizr-calls-elements": (
        Case(
            call=(
                'customer = model.Person("Customer", '
                'description="Buys goods", tags=["External"])'
            ),
            dsl="""
                customer = person "Customer" "Buys goods" {
                  tags "Person,External"
                }
            """,
        ),
        Case(
            call=(
                'shop = model.SoftwareSystem("Shop", description="Online shop")'
            ),
            dsl="""
                shop = softwareSystem "Shop" "Online shop" {
                  tags "Software System"
                }
            """,
        ),
        Case(
            setup='shop = model.SoftwareSystem("Shop", alias="shop")',
            call=(
                'api = model.Container("API", description="HTTP API", '
                'technology="FastAPI", owner=shop)'
            ),
            dsl="""
                api = container "API" "HTTP API" "FastAPI" {
                  tags "Container"
                }
            """,
        ),
        Case(
            setup=(
                'shop = model.SoftwareSystem("Shop", alias="shop")\n'
                'api = model.Container("API", alias="api", owner=shop)'
            ),
            call=(
                'model.Component("Login", description="Checks passwords", '
                'technology="Python", owner=api)'
            ),
            dsl="""
                login = component "Login" "Checks passwords" "Python" {
                  tags "Component"
                }
            """,
        ),
        Case(
            call=(
                'live = model.DeploymentEnvironment("Live")\n'
                'server = live.DeploymentNode("Server", '
                'technology="Ubuntu 24.04")'
            ),
            dsl="""
                deploymentEnvironment "Live" {
                  server = deploymentNode "Server" "" "Ubuntu 24.04" {
            """,
        ),
        Case(
            setup=STRUCTURIZR_DEPLOYMENT,
            call='docker = server.DeploymentNode("Docker")',
            dsl="""
                docker = deploymentNode "Docker" {
                  tags "Boundary"
            """,
        ),
        Case(
            setup=STRUCTURIZR_DEPLOYMENT,
            call=(
                'lb = server.InfrastructureNode("Load balancer", '
                'technology="nginx")'
            ),
            dsl="""
                load_balancer = infrastructureNode "Load balancer" "" "nginx" {
            """,
        ),
        Case(
            setup=STRUCTURIZR_DEPLOYMENT,
            call="server.SoftwareSystemInstance(shop)",
            dsl="""
                shop_instance = softwareSystemInstance shop {
                  tags "Software System"
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_DEPLOYMENT,
            call="server.ContainerInstance(api)",
            dsl="""
                api_instance = containerInstance api {
                  tags "Container"
                }
            """,
        ),
    ),
    "structurizr-calls-metadata": (
        Case(
            call='model.SoftwareSystem("Shop", alias="web_shop")',
            dsl='web_shop = softwareSystem "Shop" {',
        ),
        Case(
            call=(
                'model.SoftwareSystem("Shop", tags=["Critical"]).tag("Legacy")'
            ),
            dsl='tags "Software System,Critical,Legacy"',
        ),
        Case(
            call=(
                'model.SoftwareSystem("Shop", properties={"owner": "team-a"})'
            ),
            dsl="""
                properties {
                  "owner" "team-a"
                }
            """,
        ),
        Case(
            call=(
                'model.SoftwareSystem("Shop", url="https://example.com/shop")'
            ),
            dsl='url "https://example.com/shop"',
        ),
        Case(
            call='model.Person("Customer", style={"shape": "Person"})',
            dsl="""
                element "c4diagrams_style_customer" {
                  shape Person
                }
            """,
        ),
    ),
    "structurizr-calls-relationships": (
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='customer.uses(api, "Calls", technology="HTTPS")',
            dsl="""
                customer -> api "Calls" "HTTPS" {
                  tags "Relationship"
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='api.used_by(customer, "Calls", technology="HTTPS")',
            dsl='customer -> api "Calls" "HTTPS" {',
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='customer >> Rel("Calls", technology="HTTPS") >> api',
            dsl='customer -> api "Calls" "HTTPS" {',
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='customer >> "Uses" >> shop',
            dsl='customer -> shop "Uses" {',
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='customer >> Rel("Calls") >> [api, shop]',
            dsl="""
                customer -> api "Calls" {
                  tags "Relationship"
                }
                customer -> shop "Calls" {
                  tags "Relationship"
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='api << Rel("Calls") << customer',
            dsl='customer -> api "Calls" {',
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS
            + 'other = model.Person("Other", alias="other")\n',
            call='[customer, other] >> Rel("Calls") >> api',
            dsl="""
                customer -> api "Calls" {
                  tags "Relationship"
                }
                other -> api "Calls" {
                  tags "Relationship"
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call="customer >> shop",
            dsl="""
                customer -> shop {
                  tags "Relationship"
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='customer >> shop | "Uses"',
            dsl='customer -> shop "Uses" {',
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call=(
                'customer.uses(api, "Calls", tags=["Async"], '
                'properties={"sla": "99.9"})'
            ),
            dsl="""
                customer -> api "Calls" {
                  tags "Relationship,Async"
                  properties {
                    "sla" "99.9"
                  }
                }
            """,
        ),
    ),
    "structurizr-calls-views": (
        Case(
            call='workspace.views.SystemLandscapeView(key="landscape")',
            dsl="""
                systemLandscape "landscape" {
                  include *
                  autoLayout lr
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='workspace.views.SystemContextView(shop, key="context")',
            dsl="""
                systemContext shop "context" {
                  include *
                  autoLayout lr
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='workspace.views.ContainerView(shop, key="containers")',
            dsl='container shop "containers" {',
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call='workspace.views.ComponentView(api, key="components")',
            dsl='component api "components" {',
        ),
        Case(
            setup=STRUCTURIZR_DEPLOYMENT,
            call=(
                'workspace.views.DeploymentView(shop, environment="Live", '
                'key="live")'
            ),
            dsl='deployment shop "Live" "live" {',
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call=(
                'flow = workspace.views.DynamicView(shop, key="checkout")\n'
                'flow.step(customer, api, "Pays", technology="HTTPS")'
            ),
            dsl="""
                dynamic shop "checkout" {
                  customer -> api "Pays" "HTTPS"
                  autoLayout lr
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call=(
                'workspace.views.SystemContextView(shop, key="context",\n'
                '    include=["*", ViewTag("Critical")],\n'
                "    exclude=[customer])"
            ),
            dsl="""
                include *
                include element.tag==Critical
                exclude customer
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call=(
                'workspace.views.ContainerView(shop, key="containers",\n'
                '    exclude=RawSelector("relationship.tag==Async"))'
            ),
            dsl="exclude relationship.tag==Async",
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call=(
                'workspace.views.ContainerView(shop, key="containers",\n'
                "    animation=[[customer], [api]])"
            ),
            dsl="""
                animation {
                  customer
                  api
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call=(
                'workspace.views.SystemLandscapeView(key="landscape",\n'
                '    auto_layout=AutoLayout("TopBottom", '
                "rank_separation=100))"
            ),
            dsl="autoLayout tb 100",
        ),
        Case(
            call=(
                'workspace.views.SystemLandscapeView(key="landscape",\n'
                '    tags=["Overview"], properties={"audience": "all"})'
            ),
            dsl="""
                tags "Overview"
                properties {
                  "audience" "all"
                }
            """,
        ),
        Case(
            setup=STRUCTURIZR_ELEMENTS,
            call=(
                'flow = workspace.views.DynamicView(shop, key="checkout")\n'
                'flow.step(customer, api, "Pays", create_relationship=True)'
            ),
            dsl='customer -> api "Pays" {',
        ),
    ),
    "structurizr-calls-styles": (
        Case(
            call=(
                'workspace.styles.element("Staff", background="#455a64", '
                'color="#ffffff")'
            ),
            dsl="""
                element "Staff" {
                  background #455a64
                  color #ffffff
                }
            """,
        ),
        Case(
            call='workspace.styles.tag("Storage", shape="Cylinder")',
            dsl="""
                element "Storage" {
                  shape Cylinder
                }
            """,
        ),
        Case(
            call=(
                'workspace.styles.relationship("Async", border="Dashed", '
                "thickness=2)"
            ),
            dsl="""
                relationship "Async" {
                  thickness 2
                  style dashed
                }
            """,
        ),
    ),
    "structurizr-calls-options": (
        Case(
            setup='workspace.styles.element("Staff", border="Dotted")',
            call=(
                "renderer = StructurizrRenderer(\n"
                "    StructurizrRenderOptions(style_preset=None))"
            ),
            dsl="""
                element "Staff" {
                  border Dotted
                }
            """,
        ),
        Case(
            call=(
                "renderer = StructurizrRenderer(\n"
                '    StructurizrRenderOptions(style_preset="new-c4-style"))'
            ),
            dsl="""
                element "Element" {
                  shape RoundedBox
                  color #0773af
            """,
        ),
        Case(
            setup='workspace.views.SystemLandscapeView(key="landscape")',
            call=(
                "renderer = StructurizrRenderer(\n"
                "    StructurizrRenderOptions(\n"
                '        auto_layout=AutoLayout("TopBottom")))'
            ),
            dsl="autoLayout tb",
        ),
        Case(
            call=(
                'workspace = Workspace("Demo", '
                'theme="https://example.com/theme.json")'
            ),
            dsl='theme "https://example.com/theme.json"',
        ),
    ),
}

LIKEC4_IMPORTS = """
from c4.contrib.likec4 import *
from c4.contrib.likec4.renderer import LikeC4Renderer
"""

LIKEC4_SPEC = """
spec = project.specification
spec.element("actor", shape="person").element("system").element("container")
spec.relationship("async")
spec.tag("internal").tag("legacy")
spec.color("brand", "#ff6600")
spec.deployment_node("server")
"""

LIKEC4_MODEL = (
    LIKEC4_SPEC
    + """
model = project.model
customer = model.element("actor", "Customer", alias="customer")
shop = model.element("system", "Shop", alias="shop")
api = shop.element("container", "API", alias="api")
"""
)

LIKEC4_RELATED = (
    LIKEC4_MODEL
    + """
other = model.element("system", "Other", alias="other")
"""
)

LIKEC4_DEPLOYMENT = (
    LIKEC4_MODEL
    + """
prod = project.deployment.node("server", "Production", alias="prod")
"""
)

LIKEC4_CASES: dict[str, tuple[Case, ...]] = {
    "likec4-calls-specification": (
        Case(
            call=(
                "project.specification.element(\n"
                '    "actor", title="Actor", shape="person", color="blue")'
            ),
            dsl="""
                element actor {
                  title "Actor"
                  style {
                    color blue
                    shape person
                  }
                }
            """,
        ),
        Case(
            call=(
                "project.specification.relationship(\n"
                '    "async", technology="AMQP", line="dotted", head="open")'
            ),
            dsl="""
                relationship async {
                  technology "AMQP"
                  line dotted
                  head open
                }
            """,
        ),
        Case(
            call='project.specification.tag("internal", color="green")',
            dsl="tag internal { color green }",
        ),
        Case(
            call='project.specification.color("brand", "#ff6600")',
            dsl="color brand #ff6600",
        ),
        Case(
            call=(
                'project.specification.deployment_node("server", '
                'title="Server")'
            ),
            dsl='deploymentNode server { title "Server" }',
        ),
    ),
    "likec4-calls-elements": (
        Case(
            setup=LIKEC4_SPEC,
            call=(
                "customer = project.model.element(\n"
                '    "actor", "Customer", alias="customer")'
            ),
            dsl='customer = actor "Customer"',
        ),
        Case(
            setup=LIKEC4_SPEC,
            call=(
                'shop = project.model.element("system", "Shop", '
                'alias="shop")\n'
                'api = shop.element("container", "API", alias="api")'
            ),
            dsl="""
                shop = system "Shop" {
                  api = container "API"
                }
            """,
        ),
        Case(
            setup=LIKEC4_SPEC,
            call=(
                'with project.model.element("system", "Shop", '
                'alias="shop"):\n'
                '    project.model.element("container", "API", alias="api")'
            ),
            dsl="""
                shop = system "Shop" {
                  api = container "API"
                }
            """,
        ),
        Case(
            setup=LIKEC4_SPEC,
            call=(
                'project.model.element("system", "Shop",\n'
                '    summary="Online shop", technology="Django",\n'
                '    description="Takes **orders**.")'
            ),
            dsl="""
                summary "Online shop"
                description \'\'\'Takes **orders**.\'\'\'
                technology "Django"
            """,
        ),
        Case(
            setup=LIKEC4_SPEC,
            call=(
                'project.model.element("system", "Shop",\n'
                '    tags=["internal"], icon="tech:python")'
            ),
            dsl="""
                #internal
                icon tech:python
            """,
        ),
        Case(
            setup=LIKEC4_SPEC,
            call=(
                'project.model.element("system", "Shop",\n'
                '    metadata={"owner": "team-a", "env": ["dev", "prod"]},\n'
                '    links=["https://example.com", '
                '("https://example.com/docs", "Docs")])'
            ),
            dsl="""
                metadata {
                  owner "team-a"
                  env ["dev", "prod"]
                }
                link https://example.com
                link https://example.com/docs "Docs"
            """,
        ),
        Case(
            setup=LIKEC4_SPEC,
            call=(
                'project.model.element("actor", "Customer",\n'
                '    color="brand", shape="person", opacity=50)'
            ),
            dsl="""
                style {
                  color brand
                  shape person
                  opacity 50%
                }
            """,
        ),
    ),
    "likec4-calls-relationships": (
        Case(
            setup=LIKEC4_MODEL,
            call='customer.uses(shop, "buys")',
            dsl='customer -> shop "buys"',
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'customer.uses(shop, "buys", kind="async", technology="HTTPS")'
            ),
            dsl="""
                customer -[async]-> shop "buys" { technology "HTTPS" }
            """,
        ),
        Case(
            setup=LIKEC4_MODEL,
            call='customer.uses(shop, "talks", bidirectional=True)',
            dsl='customer <-> shop "talks"',
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'customer.uses(shop, "buys", tags=["legacy"], line="dashed")'
            ),
            dsl="""
                customer -> shop "buys" {
                  #legacy
                  style { line dashed }
                }
            """,
        ),
    ),
    "likec4-calls-relationship-forms": (
        Case(
            setup=LIKEC4_RELATED,
            call='customer >> Rel("buys") >> shop',
            dsl='customer -> shop "buys"',
        ),
        Case(
            setup=LIKEC4_RELATED,
            call='customer >> "buys" >> shop',
            dsl='customer -> shop "buys"',
        ),
        Case(
            setup=LIKEC4_RELATED,
            call='shop << Rel("buys") << customer',
            dsl='customer -> shop "buys"',
        ),
        Case(
            setup=LIKEC4_RELATED,
            call='shop.used_by(customer, "buys")',
            dsl='customer -> shop "buys"',
        ),
        Case(
            setup=LIKEC4_RELATED,
            call=(
                'customer >> Rel("buys", kind="async", '
                'technology="HTTPS") >> shop'
            ),
            dsl="""
                customer -[async]-> shop "buys" { technology "HTTPS" }
            """,
        ),
        Case(
            setup=LIKEC4_RELATED,
            call='customer >> Rel("buys") >> [shop, other]',
            dsl="""
                customer -> shop "buys"
                customer -> other "buys"
            """,
        ),
        Case(
            setup=LIKEC4_RELATED,
            call='[customer, other] >> Rel("buys") >> shop',
            dsl="""
                customer -> shop "buys"
                other -> shop "buys"
            """,
        ),
        Case(
            setup=LIKEC4_RELATED,
            call="customer >> shop",
            dsl="customer -> shop",
        ),
        Case(
            setup=LIKEC4_RELATED,
            call='customer >> shop | "buys"',
            dsl='customer -> shop "buys"',
        ),
    ),
    "likec4-calls-deployment": (
        Case(
            setup=LIKEC4_MODEL,
            call=(
                "prod = project.deployment.node(\n"
                '    "server", "Production", alias="prod")'
            ),
            dsl='prod = server "Production"',
        ),
        Case(
            setup=LIKEC4_DEPLOYMENT,
            call=('prod.instance(api, "api_1")\nprod.instance(api)'),
            dsl="""
                api_1 = instanceOf shop.api
                instanceOf shop.api
            """,
        ),
        Case(
            setup=LIKEC4_DEPLOYMENT,
            call='replica = prod.node("server", "Replica")',
            dsl="""
                prod = server "Production" {
                  Replica = server "Replica"
                }
            """,
        ),
        Case(
            setup=LIKEC4_DEPLOYMENT
            + 'replica = prod.node("server", "Replica", alias="replica")\n'
            + 'primary = prod.instance(api, "primary")\n',
            call='primary.uses(replica, "replicates to")',
            dsl='prod.primary -> prod.replica "replicates to"',
        ),
        Case(
            setup=LIKEC4_DEPLOYMENT
            + 'replica = prod.node("server", "Replica", alias="replica")\n'
            + 'primary = prod.instance(api, "primary")\n',
            call='primary >> Rel("replicates to") >> replica',
            dsl='prod.primary -> prod.replica "replicates to"',
        ),
    ),
    "likec4-calls-views": (
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'project.views.element_view("index", "Landscape", of=shop)'
                ".include(Wildcard())"
            ),
            dsl="""
                view index of shop {
                  title "Landscape"
                  include *
                }
            """,
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'view = project.views.element_view("index")\n'
                "view.include(Children(shop), Descendants(shop))"
            ),
            dsl="include shop.*, shop.**",
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'view = project.views.element_view("index")\n'
                "view.include(Between(customer, shop))\n"
                "view.include(Between(customer, shop, both=True))\n"
                "view.include(Incoming(shop), Outgoing(shop), InOut(shop))"
            ),
            dsl="""
                include customer -> shop
                include customer <-> shop
                include -> shop
                include shop ->
                include -> shop ->
            """,
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'view = project.views.element_view("index")\n'
                'view.include(Where(shop, tag="legacy"))\n'
                'view.include(RawPredicate("shop.api"))'
            ),
            dsl="""
                include shop where tag is #legacy
                include shop.api
            """,
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'view = project.views.element_view("index")\n'
                "view.include(Wildcard()).exclude(customer)"
            ),
            dsl="exclude customer",
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'view = project.views.element_view("index")\n'
                'view.style(shop, color="brand", opacity=40)'
            ),
            dsl="""
                style shop {
                  color brand
                  opacity 40%
                }
            """,
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'view = project.views.element_view("index")\n'
                'view.auto_layout("LeftRight", rank_sep=80, node_sep=60)'
            ),
            dsl="autoLayout LeftRight 80 60",
        ),
        Case(
            setup=LIKEC4_MODEL + 'project.views.dynamic_view("flow", "Flow")\n',
            call=(
                'view = project.views.element_view("index")\n'
                'view.include(shop, navigate_to="flow")'
            ),
            dsl="include shop with { navigateTo flow }",
        ),
        Case(
            setup=LIKEC4_DEPLOYMENT,
            call=(
                'view = project.views.deployment_view("live", "Live")\n'
                "view.include(Wildcard())"
            ),
            dsl="""
                deployment view live {
                  title "Live"
                  include *
                }
            """,
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                "flow = project.views.dynamic_view(\n"
                '    "flow", "Checkout", variant="sequence")\n'
                'flow.step(customer, shop, "pays", technology="HTTPS")\n'
                'flow.back(customer, shop, "confirms")'
            ),
            dsl="""
                dynamic view flow {
                  title "Checkout"
                  variant sequence
                  customer -> shop "pays" { technology "HTTPS" }
                  customer <- shop "confirms"
                }
            """,
        ),
    ),
    "likec4-calls-styles": (
        Case(
            call=(
                'project.specification.color("brand", "#ff6600")\n'
                'project.specification.tag("promo", color="brand")'
            ),
            dsl="tag promo { color brand }",
        ),
        Case(
            call=(
                'project.specification.element("service", '
                'shape="component", color="indigo", border="dashed")'
            ),
            dsl="""
                element service {
                  style {
                    color indigo
                    shape component
                    border dashed
                  }
                }
            """,
        ),
        Case(
            call=(
                'project.specification.element("service", size="lg", '
                'padding="sm", text_size="xs")'
            ),
            dsl="""
                style {
                  size lg
                  textSize xs
                  padding sm
                }
            """,
        ),
        Case(
            setup=LIKEC4_SPEC,
            call=(
                'project.model.element("system", "Shop", '
                'iconPosition="bottom", icon_size="lg")'
            ),
            dsl="""
                style {
                  iconSize lg
                  iconPosition bottom
                }
            """,
        ),
        Case(
            setup=LIKEC4_SPEC,
            call=(
                'project.specification.relationship("sync", '
                'line="solid", head="vee", tail="none")'
            ),
            dsl="""
                relationship sync {
                  line solid
                  head vee
                  tail none
                }
            """,
        ),
        Case(
            setup=LIKEC4_MODEL,
            call=(
                'view = project.views.element_view("index")\n'
                'view.style(shop, shape="queue", size="lg", multiple=True)'
            ),
            dsl="""
                style shop {
                  shape queue
                  size lg
                  multiple true
                }
            """,
        ),
    ),
}


def clean(text: str) -> str:
    """Dedent a case block and strip surrounding blank lines."""
    return textwrap.dedent(text).strip("\n")


def structurizr_render(case: Case) -> str:
    """Run a Structurizr case and return the rendered DSL."""
    namespace: dict[str, object] = {}
    exec(clean(STRUCTURIZR_IMPORTS), namespace)  # noqa: S102
    exec(  # noqa: S102
        'workspace = Workspace("Demo")\n'
        "model = workspace.model\n"
        + clean(case.setup)
        + "\n"
        + clean(case.call)
        + "\n",
        namespace,
    )
    renderer = namespace.get("renderer") or namespace["StructurizrRenderer"]()  # type: ignore[operator]
    return renderer.render(namespace["workspace"])  # type: ignore[attr-defined,no-any-return]


def contains_fragment(output: str, fragment: str) -> bool:
    """Whether the fragment appears in the output.

    A one-line fragment may appear anywhere inside a line. A longer fragment
    must match consecutive lines. Indentation is ignored, so fragments can be
    shown without the leading whitespace of their nesting level.
    """
    wanted = [line.strip() for line in clean(fragment).splitlines()]
    if len(wanted) == 1:
        return wanted[0] in output
    lines = [line.strip() for line in output.splitlines()]
    return any(
        lines[start : start + len(wanted)] == wanted
        for start in range(len(lines) - len(wanted) + 1)
    )


def likec4_render(case: Case) -> str:
    """Run a LikeC4 case and return the rendered ``.c4`` text."""
    namespace: dict[str, object] = {}
    exec(clean(LIKEC4_IMPORTS), namespace)  # noqa: S102
    exec(  # noqa: S102
        'project = Project("Demo")\n'
        + clean(case.setup)
        + "\n"
        + clean(case.call)
        + "\n",
        namespace,
    )
    renderer = namespace.get("renderer") or namespace["LikeC4Renderer"]()  # type: ignore[operator]
    return renderer.render(namespace["project"])  # type: ignore[attr-defined,no-any-return]
