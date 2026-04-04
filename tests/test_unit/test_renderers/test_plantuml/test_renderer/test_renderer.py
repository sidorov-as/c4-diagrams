import textwrap
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from c4 import (
    ComponentDiagram,
    Container,
    ContainerDb,
    ContainerDiagram,
    DeploymentDiagram,
    DynamicDiagram,
    EnterpriseBoundary,
    LayDown,
    Person,
    Rel,
    RelDown,
    RelLeft,
    RelRight,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemExt,
    SystemLandscapeDiagram,
    increment,
    set_index,
)
from c4.diagrams.core import Diagram, RelUp
from c4.exceptions import PlantUMLBackendConfigurationError
from c4.renderers import RenderOptions
from c4.renderers.plantuml import LayoutOptions
from c4.renderers.plantuml.backends import DiagramFormat
from c4.renderers.plantuml.constants import (
    C4_COMPONENT_INCLUDE,
    C4_CONTAINER_INCLUDE,
    C4_CONTEXT_INCLUDE,
    C4_DEPLOYMENT_INCLUDE,
    C4_DYNAMIC_INCLUDE,
    RELATIVE_INCLUDE_COMMENT,
)
from c4.renderers.plantuml.renderer import (
    PlantUMLComponentDiagramRenderer,
    PlantUMLContainerDiagramRenderer,
    PlantUMLDeploymentDiagramRenderer,
    PlantUMLDynamicDiagramRenderer,
    PlantUMLRenderer,
    PlantUMLSystemContextDiagramRenderer,
    PlantUMLSystemLandscapeDiagramRenderer,
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

        taxamo = System(
            "Taxamo",
            (
                "Calculates local tax and acts as a front-end for "
                "Braintree Payments."
            ),
            alias="taxamo",
        )

        braintree = System(
            "Braintree Payments",
            "Processes credit card payments on behalf of Widgets Limited.",
            alias="braintree",
        )

        post = System(
            "Jersey Post",
            "Calculates worldwide shipping costs for packages.",
            alias="post",
        )

        customer >> RelRight("Asks questions to", technology="Telephone") >> csa
        (
            customer
            >> RelRight(
                "Places orders for widgets using",
            )
            >> ecommerce
        )
        csa >> Rel("Looks up order information using") >> ecommerce
        ecommerce >> RelRight("Sends order information to") >> fulfillment
        fulfillment >> RelDown("Gets shipping charges from") >> post
        ecommerce >> RelDown("Delegates credit card processing to") >> taxamo
        taxamo >> RelLeft("Uses for credit card processing") >> braintree

        LayDown(customer, braintree)

    return diagram


@pytest.mark.parametrize(
    ("diagram", "renderer_class"),
    [
        (
            SystemContextDiagram(),
            PlantUMLSystemContextDiagramRenderer,
        ),
        (
            SystemLandscapeDiagram(),
            PlantUMLSystemLandscapeDiagramRenderer,
        ),
        (
            ContainerDiagram(),
            PlantUMLContainerDiagramRenderer,
        ),
        (
            ComponentDiagram(),
            PlantUMLComponentDiagramRenderer,
        ),
        (
            DynamicDiagram(),
            PlantUMLDynamicDiagramRenderer,
        ),
        (
            DeploymentDiagram(),
            PlantUMLDeploymentDiagramRenderer,
        ),
    ],
)
def test_plant_uml_renderer__get_renderer(
    diagram: Diagram,
    renderer_class: type,
):
    renderer = PlantUMLRenderer()

    result = renderer.get_renderer(diagram)

    assert isinstance(result, renderer_class)


def test_plant_uml_renderer__get_renderer__passes_shared_configuration():
    includes = ["!include custom.puml"]
    layout_config = LayoutOptions().layout_top_down(with_legend=True).build()
    backend = object()
    renderer = PlantUMLRenderer(
        includes=includes,
        layout_config=layout_config,
        backend=backend,
        use_new_c4_style=True,
    )
    diagram = SystemContextDiagram()

    result = renderer.get_renderer(diagram)

    assert result._includes == includes
    assert result._config is layout_config
    assert result._plantuml_backend is backend
    assert result._use_new_c4_style is True


def test_plant_uml_renderer__get_renderer__diagram_render_options():
    includes = ["!include custom.puml"]
    layout_config = LayoutOptions().layout_top_down(with_legend=True).build()
    diagram_layout_config = LayoutOptions().layout_landscape().build()
    backend = object()
    renderer = PlantUMLRenderer(
        includes=includes,
        layout_config=layout_config,
        backend=backend,
        use_new_c4_style=True,
    )
    diagram = SystemContextDiagram(
        render_options=RenderOptions(plantuml=diagram_layout_config)
    )

    result = renderer.get_renderer(diagram)

    assert result._includes == includes
    assert result._config is diagram_layout_config
    assert result._plantuml_backend is backend
    assert result._use_new_c4_style is True


def test_plant_uml_renderer__get_renderer__unsupported_diagram_type():
    class UnsupportedDiagram:
        pass

    renderer = PlantUMLRenderer()
    diagram = UnsupportedDiagram()
    expected_error = f"Unsupported PlantUML diagram type: {type(diagram)}"

    with pytest.raises(NotImplementedError, match=expected_error):
        renderer.get_renderer(diagram)  # type: ignore[arg-type]


def test_plant_uml__system_context_diagram__render():
    diagram = build_system_context_diagram()
    layout_config = LayoutOptions().layout_top_down(with_legend=True).build()
    renderer = PlantUMLSystemContextDiagramRenderer(
        layout_config=layout_config,
    )

    result = renderer.render(diagram)

    assert "@startuml" in result
    assert "@enduml" in result
    assert RELATIVE_INCLUDE_COMMENT in result
    assert C4_CONTEXT_INCLUDE in result
    assert "title Widgets Context" in result
    assert "Customer" in result
    assert "E-commerce System" in result
    assert "Braintree Payments" in result
    assert "Places orders for widgets using" in result
    assert "LAYOUT_TOP_DOWN" in result
    assert "LAYOUT_WITH_LEGEND" in result


def test_plant_uml__system_context_diagram__render__new_c4_style():
    diagram = build_system_context_diagram()
    renderer = PlantUMLSystemContextDiagramRenderer(
        use_new_c4_style=True,
    )

    result = renderer.render(diagram)

    assert "!NEW_C4_STYLE=1" in result


def test_plant_uml__system_context_diagram__render__include():
    diagram = build_system_context_diagram()
    renderer = PlantUMLSystemContextDiagramRenderer(
        includes=["!include custom-theme.puml"],
    )

    result = renderer.render(diagram)

    assert RELATIVE_INCLUDE_COMMENT in result
    assert C4_CONTEXT_INCLUDE in result
    assert "!include custom-theme.puml" in result


def test_plant_uml__system_context_diagram__render_bytes(
    mocker: MockerFixture,
):
    diagram = build_system_context_diagram()
    backend = mocker.Mock()
    backend.to_bytes.return_value = b"diagram-bytes"
    renderer = PlantUMLSystemContextDiagramRenderer(
        backend=backend,
    )

    result = renderer.render_bytes(diagram, format=DiagramFormat.SVG)

    assert result == b"diagram-bytes"
    backend.to_bytes.assert_called_once()
    assert backend.to_bytes.call_args.kwargs["format"] == DiagramFormat.SVG
    assert "@startuml" in backend.to_bytes.call_args.kwargs["diagram"]
    assert "@enduml" in backend.to_bytes.call_args.kwargs["diagram"]


def test_plant_uml__system_context_diagram__render_bytes__no_backend():
    diagram = build_system_context_diagram()
    renderer = PlantUMLSystemContextDiagramRenderer()

    with pytest.raises(PlantUMLBackendConfigurationError):
        renderer.render_bytes(diagram, format=DiagramFormat.SVG)


def test_plant_uml__system_context_diagram__render_file(
    mocker: MockerFixture,
    tmp_path: Path,
):
    diagram = build_system_context_diagram()
    output_path = tmp_path / "diagram.svg"
    backend = mocker.Mock()
    backend.to_file.return_value = output_path
    renderer = PlantUMLSystemContextDiagramRenderer(
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
    assert "@startuml" in backend.to_file.call_args.kwargs["diagram"]
    assert "@enduml" in backend.to_file.call_args.kwargs["diagram"]


def test_plant_uml__system_context_diagram__render_file__no_backend(
    tmp_path: Path,
):
    diagram = build_system_context_diagram()
    renderer = PlantUMLSystemContextDiagramRenderer()

    with pytest.raises(PlantUMLBackendConfigurationError):
        renderer.render_file(
            diagram,
            output_path=tmp_path / "diagram.svg",
            format=DiagramFormat.SVG,
        )


@pytest.mark.parametrize(
    ("renderer_class", "expected_include"),
    [
        (
            PlantUMLSystemContextDiagramRenderer,
            C4_CONTEXT_INCLUDE,
        ),
        (
            PlantUMLSystemLandscapeDiagramRenderer,
            C4_CONTEXT_INCLUDE,
        ),
        (
            PlantUMLContainerDiagramRenderer,
            C4_CONTAINER_INCLUDE,
        ),
        (
            PlantUMLComponentDiagramRenderer,
            C4_COMPONENT_INCLUDE,
        ),
        (
            PlantUMLDynamicDiagramRenderer,
            C4_DYNAMIC_INCLUDE,
        ),
        (
            PlantUMLDeploymentDiagramRenderer,
            C4_DEPLOYMENT_INCLUDE,
        ),
    ],
)
def test_base_plant_uml_renderer__init__uses_default_includes(
    renderer_class: type,
    expected_include: str,
):
    renderer = renderer_class()

    assert (
        RELATIVE_INCLUDE_COMMENT in renderer._layout_options_renderer._includes
    )
    assert expected_include in renderer._layout_options_renderer._includes


def test_plant_uml_renderer__render__delegates_to_specific_renderer(
    mocker: MockerFixture,
):
    diagram = SystemContextDiagram()
    renderer = PlantUMLRenderer()
    concrete_renderer = mocker.Mock()
    concrete_renderer.render.return_value = "rendered-diagram"
    get_renderer = mocker.patch.object(
        renderer,
        "get_renderer",
        return_value=concrete_renderer,
    )

    result = renderer.render(diagram)

    assert result == "rendered-diagram"
    get_renderer.assert_called_once_with(diagram)
    concrete_renderer.render.assert_called_once_with(diagram)


def test_plant_uml_renderer__render_bytes__delegates_to_specific_renderer(
    mocker: MockerFixture,
):
    diagram = SystemContextDiagram()
    renderer = PlantUMLRenderer()
    concrete_renderer = mocker.Mock()
    concrete_renderer.render_bytes.return_value = b"rendered-bytes"
    get_renderer = mocker.patch.object(
        renderer,
        "get_renderer",
        return_value=concrete_renderer,
    )

    result = renderer.render_bytes(diagram, format=DiagramFormat.PNG)

    assert result == b"rendered-bytes"
    get_renderer.assert_called_once_with(diagram)
    concrete_renderer.render_bytes.assert_called_once_with(
        diagram,
        format=DiagramFormat.PNG,
    )


def test_plant_uml_renderer__render_file__delegates_to_specific_renderer(
    mocker: MockerFixture,
    tmp_path: Path,
):
    diagram = SystemContextDiagram()
    output_path = tmp_path / "diagram.png"
    renderer = PlantUMLRenderer()
    concrete_renderer = mocker.Mock()
    concrete_renderer.render_file.return_value = output_path
    get_renderer = mocker.patch.object(
        renderer,
        "get_renderer",
        return_value=concrete_renderer,
    )

    result = renderer.render_file(
        diagram,
        output_path=output_path,
        format=DiagramFormat.PNG,
        overwrite=False,
    )

    assert result == output_path
    get_renderer.assert_called_once_with(diagram)
    concrete_renderer.render_file.assert_called_once_with(
        diagram,
        output_path=output_path,
        format=DiagramFormat.PNG,
        overwrite=False,
    )


def test_plantuml_dynamic_diagram_renderer__base_elements():
    renderer = PlantUMLDynamicDiagramRenderer()
    with DynamicDiagram() as diagram:
        customer = Person("Customer", "A customer", alias="customer")
        app = Container(
            "Customer Application",
            "Allows customers to manage their profile",
            "Javascript, Angular",
            alias="app",
        )
        customer_service = Container(
            "Customer Service",
            "The point of access for customer information",
            "Java, Spring Boot",
            alias="customer_service",
        )
        customer_db = ContainerDb(
            "Customer Database",
            "Stores customer information",
            "Oracle 12c",
            alias="customer_db",
        )

        customer >> "Updates his profile using" >> app
        increment(1)
        app >> "Updates customer information using" >> customer_service
        set_index(2)
        customer_service >> "Stores data in" >> customer_db
    expected_diagram = textwrap.dedent(
        """
        @startuml
        ' convert it with additional command line argument -DRELATIVE_INCLUDE="relative/absolute" to use locally
        !if %variable_exists("RELATIVE_INCLUDE")
            !include %get_variable_value("RELATIVE_INCLUDE")/C4_Dynamic.puml
        !else
            !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Dynamic.puml
        !endif

        Person(customer, "Customer", "A customer")

        Container(app, "Customer Application", "Javascript, Angular", "Allows customers to manage their profile")

        Container(customer_service, "Customer Service", "Java, Spring Boot", "The point of access for customer information")

        ContainerDb(customer_db, "Customer Database", "Oracle 12c", "Stores customer information")

        Rel(customer, app, "Updates his profile using")
        increment()
        Rel(app, customer_service, "Updates customer information using")
        setIndex(2)
        Rel(customer_service, customer_db, "Stores data in")

        @enduml
        """
    ).strip()

    result = renderer.render(diagram)

    assert result == expected_diagram


def test_plantuml_dynamic_diagram_renderer__base_elements__unknown_type():
    renderer = PlantUMLDynamicDiagramRenderer()
    element = object()
    expected_error = f"Unsupported element {element!r} for DynamicDiagram."

    with pytest.raises(TypeError, match=expected_error):
        renderer.render_base_element(element)


def test_plantuml_renderer__relationships_with_properties():
    renderer = PlantUMLDynamicDiagramRenderer()
    with SystemContextDiagram() as diagram:
        user = Person("User")
        system = System("System")
        email_provider = SystemExt("Email Provider")

        relationship = user >> RelUp("Uses") >> system
        relationship.set_property_header("Key", "Value")
        relationship.add_property("Channel", "Web")
        relationship.add_property("Region", "EU")

        system >> Rel("Uses").add_property("Fallback", "SMTP") >> email_provider
    expected_diagram = textwrap.dedent(
        """
        @startuml
        ' convert it with additional command line argument -DRELATIVE_INCLUDE="relative/absolute" to use locally
        !if %variable_exists("RELATIVE_INCLUDE")
            !include %get_variable_value("RELATIVE_INCLUDE")/C4_Dynamic.puml
        !else
            !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Dynamic.puml
        !endif

        Person(user, "User")

        System(system, "System")

        System_Ext(email_provider, "Email Provider")

        SetPropertyHeader("Key", "Value")
        AddProperty("Channel", "Web")
        AddProperty("Region", "EU")
        Rel_Up(user, system, "Uses")

        SetPropertyHeader("Property", "Value")
        AddProperty("Fallback", "SMTP")
        Rel(system, email_provider, "Uses")

        @enduml
        """
    ).strip()

    result = renderer.render(diagram)

    assert result == expected_diagram
