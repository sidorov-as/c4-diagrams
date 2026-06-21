import textwrap
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from c4 import (
    ComponentDiagram,
    ContainerDiagram,
    DeploymentDiagram,
    DiagramFormat,
    DynamicDiagram,
    EnterpriseBoundary,
    Person,
    Rel,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemLandscapeDiagram,
)
from c4.contrib.plantuml import LayDown, increment, set_index
from c4.enums import STRICT
from c4.exceptions import MermaidBackendConfigurationError
from c4.renderers import (
    ExtensionValidationMode,
    MermaidRenderOptionsBuilder,
)
from c4.renderers.mermaid.renderer import (
    DIAGRAM_TYPE_TO_MERMAID_DEFINITION_MAP,
    MermaidRenderer,
)


def build_system_context_diagram() -> SystemContextDiagram:
    with SystemContextDiagram(title="Widgets Context") as diagram:
        customer = Person(
            "Customer",
            "A customer of Widgets Limited.",
            alias="customer",
        )

        with EnterpriseBoundary("Widgets Limited", alias="c0"):
            csa = Person(
                "Customer Service Agent",
                "Deals with customer enquiries.",
                alias="csa",
            )

            ecommerce = System(
                "E-commerce System",
                (
                    "Allows customers to buy widgets online via the "
                    "widgets.com website."
                ),
                alias="ecommerce",
            )

            with SystemBoundary("Fulfillment", alias="fulfillment_boundary"):
                fulfillment = System(
                    "Fulfillment System",
                    (
                        "Responsible for processing and shipping of customer "
                        "orders."
                    ),
                    alias="fulfillment",
                )

        customer >> Rel("Asks questions to", technology="Telephone") >> csa
        customer >> Rel("Places orders for widgets using") >> ecommerce
        csa >> Rel("Looks up order information using") >> ecommerce
        ecommerce >> Rel("Sends order information to") >> fulfillment

    return diagram


@pytest.mark.parametrize(
    ("diagram", "expected_definition"),
    [
        (SystemContextDiagram(), "C4Context"),
        (SystemLandscapeDiagram(), "C4Context"),
        (ContainerDiagram(), "C4Container"),
        (ComponentDiagram(), "C4Component"),
        (DynamicDiagram(), "C4Dynamic"),
        (DeploymentDiagram(), "C4Deployment"),
    ],
)
def test_diagram_type_to_mermaid_definition_map(
    diagram,
    expected_definition: str,
) -> None:
    assert (
        DIAGRAM_TYPE_TO_MERMAID_DEFINITION_MAP[type(diagram)]
        == expected_definition
    )


def test_mermaid_renderer__render():
    diagram = build_system_context_diagram()
    renderer = MermaidRenderer()
    expected_result = textwrap.dedent(
        """
        C4Context
        title Widgets Context

        Person(customer, "Customer", "A customer of Widgets Limited.")

        Enterprise_Boundary(c0, "Widgets Limited") {
            Person(csa, "Customer Service Agent", "Deals with customer enquiries.")
            System(ecommerce, "E-commerce System", "Allows customers to buy widgets online via the widgets.com website.")
            System_Boundary(fulfillment_boundary, "Fulfillment") {
                System(fulfillment, "Fulfillment System", "Responsible for processing and shipping of customer orders.")
            }
        }

        Rel(customer, csa, "Asks questions to", "Telephone")

        Rel(customer, ecommerce, "Places orders for widgets using")

        Rel(csa, ecommerce, "Looks up order information using")

        Rel(ecommerce, fulfillment, "Sends order information to")
        """
    )

    result = renderer.render(diagram)

    assert result.strip() == expected_result.strip()


def test_mermaid_renderer__render__without_title() -> None:
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")

        user >> Rel("Uses") >> system

    renderer = MermaidRenderer()
    expected_result = textwrap.dedent(
        """
        C4Context

        Person(user, "User")

        System(system, "System")

        Rel(user, system, "Uses")
        """
    )

    result = renderer.render(diagram)

    assert result.strip() == expected_result.strip()


def test_mermaid_renderer__rejects_relationship_to_boundary() -> None:
    with SystemContextDiagram() as diagram:
        customer = Person("Customer", alias="customer")
        with SystemBoundary("Platform", alias="platform") as platform:
            System("Web App", alias="web_app")

        customer >> Rel("Uses") >> platform

    renderer = MermaidRenderer()
    expected_error = (
        "Mermaid relationships cannot target boundaries: "
        "customer -> platform targets SystemBoundary\\(platform\\). "
        "Use a concrete nested element instead."
    )

    with pytest.raises(ValueError, match=expected_error):
        renderer.render(diagram)


def test_mermaid_renderer__allows_relationship_to_nested_element() -> None:
    with SystemContextDiagram() as diagram:
        customer = Person("Customer", alias="customer")
        with SystemBoundary("Platform", alias="platform"):
            web_app = System("Web App", alias="web_app")

        customer >> Rel("Uses") >> web_app

    result = MermaidRenderer().render(diagram)

    assert 'Rel(customer, web_app, "Uses")' in result


def test_mermaid_renderer__rejects_foreign_extensions() -> None:
    with SystemContextDiagram() as diagram:
        System(
            "System",
            alias="system",
            extensions={"plantuml": {"sprite": "server"}},
        )

    renderer = MermaidRenderer(extension_validation_mode=STRICT)
    expected_error = (
        "System has unsupported backend extensions for "
        "MermaidRenderer: plantuml."
    )

    with pytest.raises(ValueError, match=expected_error):
        renderer.render(diagram)


def test_mermaid_renderer__ignores_foreign_extensions_by_default() -> None:
    with SystemContextDiagram() as diagram:
        System(
            "System",
            alias="system",
            extensions={"plantuml": {"sprite": "server"}},
        )

    renderer = MermaidRenderer()

    renderer.render(diagram)


def test_mermaid_renderer__can_ignore_foreign_extensions() -> None:
    with SystemContextDiagram() as diagram:
        System(
            "System",
            alias="system",
            extensions={"plantuml": {"sprite": "server"}},
        )

    renderer = MermaidRenderer(
        extension_validation_mode=ExtensionValidationMode.IGNORE_FOREIGN,
    )

    result = renderer.render(diagram)

    assert 'System(system, "System")' in result


def test_mermaid_renderer__render_bytes(
    mocker: MockerFixture,
):
    diagram = build_system_context_diagram()
    backend = mocker.Mock()
    backend.to_bytes.return_value = b"diagram-bytes"
    renderer = MermaidRenderer(
        backend=backend,
    )

    result = renderer.render_bytes(diagram, format=DiagramFormat.SVG)

    assert result == b"diagram-bytes"
    backend.to_bytes.assert_called_once()
    assert backend.to_bytes.call_args.kwargs["format"] == DiagramFormat.SVG
    assert "C4Context" in backend.to_bytes.call_args.kwargs["diagram"]


def test_mermaid_renderer__render_bytes__no_backend():
    diagram = build_system_context_diagram()
    renderer = MermaidRenderer()

    with pytest.raises(MermaidBackendConfigurationError):
        renderer.render_bytes(diagram, format=DiagramFormat.SVG)


def test_mermaid_renderer__render_file(
    mocker: MockerFixture,
    tmp_path: Path,
):
    diagram = build_system_context_diagram()
    output_path = tmp_path / "diagram.svg"
    backend = mocker.Mock()
    backend.to_file.return_value = output_path
    renderer = MermaidRenderer(
        backend=backend,
    )

    result = renderer.render_file(
        diagram,
        output_path=output_path,
        format=DiagramFormat.SVG,
        overwrite=False,
    )

    assert result == output_path
    backend.to_file.assert_called_once()
    assert backend.to_file.call_args.kwargs["output_path"] == output_path
    assert backend.to_file.call_args.kwargs["format"] == DiagramFormat.SVG
    assert backend.to_file.call_args.kwargs["overwrite"] is False
    assert "C4Context" in backend.to_file.call_args.kwargs["diagram"]


def test_mermaid_renderer__render_file__no_backend(
    tmp_path: Path,
):
    diagram = build_system_context_diagram()
    renderer = MermaidRenderer()

    with pytest.raises(MermaidBackendConfigurationError):
        renderer.render_file(
            diagram,
            output_path=tmp_path / "diagram.svg",
            format=DiagramFormat.SVG,
        )


def test_mermaid_renderer__rejects_plantuml_index_statements():
    with DynamicDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system
        increment()
        set_index(10)
    renderer = MermaidRenderer()
    expected_error = (
        "increment is not supported by MermaidRenderer "
        "\\(mermaid\\). Allowed renderer types: plantuml."
    )

    with pytest.raises(ValueError, match=expected_error):
        renderer.render(diagram)


def test_mermaid_renderer__rejects_plantuml_layouts():
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        LayDown(user, system)

    renderer = MermaidRenderer()
    expected_error = (
        "LayDown is not supported by MermaidRenderer "
        "\\(mermaid\\). Allowed renderer types: plantuml."
    )

    with pytest.raises(ValueError, match=expected_error):
        renderer.render(diagram)


def test_mermaid_renderer__render__passes_shared_configuration():
    render_options = (
        MermaidRenderOptionsBuilder()
        .update_rel_style("customer", "web_app", offset_x=90, offset_y=60)
        .build()
    )
    renderer = MermaidRenderer(
        render_options=render_options,
    )
    diagram = SystemContextDiagram()
    expected_result = textwrap.dedent(
        """
        C4Context

        UpdateRelStyle(customer, web_app, $offsetX="90", $offsetY="60")
        """
    )

    result = renderer.render(diagram)

    assert result.strip() == expected_result.strip()


def test_mermaid_renderer__render__diagram_render_options():
    render_options = (
        MermaidRenderOptionsBuilder()
        .update_rel_style("customer", "web_app", offset_x=90, offset_y=60)
        .build()
    )
    diagram_render_options = (
        MermaidRenderOptionsBuilder()
        .update_layout_config(c4_shape_in_row=4, c4_boundary_in_row=2)
        .build()
    )
    renderer = MermaidRenderer(
        render_options=render_options,
    )
    diagram = SystemContextDiagram()
    diagram.set_render_options(mermaid=diagram_render_options)
    expected_result = textwrap.dedent(
        """
        C4Context

        UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="2")
        """
    )

    result = renderer.render(diagram)

    assert result.strip() == expected_result.strip()
