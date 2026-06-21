from __future__ import annotations

import textwrap

import pytest
from pytest_mock import MockerFixture

from c4 import (
    DynamicDiagram,
    Person,
    Rel,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemExt,
)
from c4.contrib.plantuml import (
    LayDown,
    LayUp,
    RelBack,
    RelLeft,
    RelUp,
    increment,
    set_index,
)
from c4.converters.python.converter import PythonCodegen, diagram_to_python_code
from c4.converters.python.renderers.plantuml import PlantUMLRenderOptionsCodegen
from c4.diagrams.core import DiagramElementProperties
from c4.enums import RendererEnum
from c4.renderers import MermaidRenderOptions, RenderOptions
from c4.renderers.base import IndentedStringBuilder
from c4.renderers.plantuml.options import PlantUMLRenderOptions


@pytest.fixture()
def python_codegen():
    return PythonCodegen()


@pytest.fixture()
def builder(python_codegen: PythonCodegen):
    return python_codegen._builder


def test_python_codegen__render_scope_item__relationship(
    python_codegen: PythonCodegen,
    mocker: MockerFixture,
):
    spied__render_relationship = mocker.spy(
        python_codegen,
        "_render_relationship",
    )
    with SystemContextDiagram():
        user = Person("User")
        system = System("System")
        relationship = user >> Rel("Uses") >> system

    python_codegen._render_scope_item(relationship)

    spied__render_relationship.assert_called_once_with(relationship)


def test_python_codegen__render_ordered_statement__increment(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with DynamicDiagram():
        inc = increment(1)

    python_codegen._render_ordered_statement(inc)

    assert builder.lines == ["increment(1)"]


def test_python_codegen__render_ordered_statement__set_index(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with DynamicDiagram():
        idx = set_index(5)

    python_codegen._render_ordered_statement(idx)

    assert builder.lines == ["set_index(5)"]


def test_python_codegen__render_scope_item__element(
    python_codegen: PythonCodegen,
    mocker: MockerFixture,
):
    spied__render_element = mocker.spy(
        python_codegen,
        "_render_element",
    )
    with SystemContextDiagram():
        user = Person("User")

    python_codegen._render_scope_item(user)

    spied__render_element.assert_called_once_with(user)


def test_python_codegen__render_scope_items(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
    mocker: MockerFixture,
):
    spied_render_scope_item = mocker.spy(
        python_codegen,
        "_render_scope_item",
    )
    with DynamicDiagram() as diagram:
        inc = increment(1)
        idx = set_index(5)

    rendered = python_codegen._render_scope_items(diagram)

    assert rendered is True
    spied_render_scope_item.assert_has_calls([
        mocker.call(inc),
        mocker.call(idx),
    ])


def test_python_codegen__render_scope_items__empty(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    diagram = DynamicDiagram()

    rendered = python_codegen._render_scope_items(diagram)

    assert rendered is False
    assert builder.lines == []


def test_python_codegen__render_boundary_def(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with SystemContextDiagram():
        with SystemBoundary("Boundary", alias="sb") as boundary:
            boundary.set_property_header("A", "B")
            boundary.add_property("k", "v")

    with python_codegen._render_boundary_def(boundary):
        builder.add("must_contain_indent()")

    assert builder.lines == [
        "with SystemBoundary('Boundary', alias='sb') as sb:",
        "    sb.set_property_header('A', 'B')",
        "    sb.add_property('k', 'v')",
        "",
        "    must_contain_indent()",
    ]


def test_python_codegen__render_boundary_def__no_properties(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with SystemContextDiagram():
        boundary = SystemBoundary("Boundary", alias="sb")

    with python_codegen._render_boundary_def(boundary):
        builder.add("must_contain_indent()")

    assert builder.lines == [
        "with SystemBoundary('Boundary', alias='sb'):",
        "    must_contain_indent()",
    ]


def test_python_codegen__render_boundary(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with SystemContextDiagram():
        with SystemBoundary("Boundary", alias="sb") as boundary:
            user = Person("User", alias="user")
            system = System("System", alias="system")
            user >> Rel("Uses") >> system

            with SystemBoundary("Nested", alias="nb") as nb:
                nb.set_property_header("A", "B")
                nb.add_property("k", "v")
                external_system = System("External System", alias="ext_system")
                system >> RelLeft("Interacts with") >> external_system

    python_codegen._render_boundary(boundary)

    assert builder.lines == [
        "with SystemBoundary('Boundary', alias='sb'):",
        "    user = Person('User', alias='user')",
        "",
        "    system = System('System', alias='system')",
        "",
        "    user >> Rel('Uses') >> system",
        "    with SystemBoundary('Nested', alias='nb') as nb:",
        "        nb.set_property_header('A', 'B')",
        "        nb.add_property('k', 'v')",
        "",
        "        ext_system = System('External System', alias='ext_system')",
        "",
        "        system >> RelLeft('Interacts with') >> ext_system",
        "",
    ]


def test_python_codegen__render_empty_boundary(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with SystemContextDiagram():
        with SystemBoundary("Boundary", alias="sb") as boundary:
            pass

    python_codegen._render_boundary(boundary)

    assert builder.lines == [
        "with SystemBoundary('Boundary', alias='sb'):",
        "    pass",
    ]


def test_python_codegen__render_scope_item__boundary(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
    mocker: MockerFixture,
):
    spied_render_boundary = mocker.spy(
        python_codegen,
        "_render_boundary",
    )
    with SystemContextDiagram():
        with SystemBoundary("Boundary 1", alias="b1") as boundary1:
            Person("User", alias="user")

        with SystemBoundary("Boundary 2", alias="b2"):
            System("System", alias="system")

    python_codegen._render_scope_item(boundary1)

    assert builder.lines == [
        "with SystemBoundary('Boundary 1', alias='b1'):",
        "    user = Person('User', alias='user')",
        "",
    ]
    spied_render_boundary.assert_called_once_with(boundary1)


def test_python_codegen__render_scope_items__boundary_children(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
    mocker: MockerFixture,
):
    spied_render_boundary = mocker.spy(
        python_codegen,
        "_render_boundary",
    )
    with SystemContextDiagram():
        with SystemBoundary("Parent", alias="pb") as parent:
            with SystemBoundary("Boundary 1", alias="b1") as boundary1:
                Person("User", alias="user")

            with SystemBoundary("Boundary 2", alias="b2") as boundary2:
                System("System", alias="system")

    rendered = python_codegen._render_scope_items(parent)

    assert rendered is True
    assert builder.lines == [
        "with SystemBoundary('Boundary 1', alias='b1'):",
        "    user = Person('User', alias='user')",
        "",
        "with SystemBoundary('Boundary 2', alias='b2'):",
        "    system = System('System', alias='system')",
        "",
    ]
    spied_render_boundary.assert_has_calls([
        mocker.call(boundary1),
        mocker.call(boundary2),
    ])


def test_python_codegen__render_diagram_def(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with SystemContextDiagram("Title") as diagram:
        ...

    with python_codegen._render_diagram_def(diagram):
        builder.add("must_contain_indent()")

    assert builder.lines == [
        "with SystemContextDiagram(title='Title') as diagram:",
        "    must_contain_indent()",
    ]


def test_python_codegen__render_element(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with SystemContextDiagram():
        user = Person("User", alias="user")

    python_codegen._render_element(user)

    assert builder.lines == [
        "user = Person('User', alias='user')",
    ]


def test_python_codegen__render_element_with_properties(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with SystemContextDiagram():
        user = Person("User", alias="user")
        user.set_property_header("Attribute", "Value")
        user.add_property("first_name", "John")
        user.add_property("last_name", "Doe")

    python_codegen._render_element(user)

    assert builder.lines == [
        "user = Person('User', alias='user')",
        "user.set_property_header('Attribute', 'Value')",
        "user.add_property('first_name', 'John')",
        "user.add_property('last_name', 'Doe')",
        "",
    ]


def test_python_codegen__render_scope_items__diagram_elements(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
    mocker: MockerFixture,
):
    spied_render_element = mocker.spy(
        python_codegen,
        "_render_element",
    )
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")

    rendered = python_codegen._render_scope_items(diagram)

    assert rendered is True
    spied_render_element.assert_has_calls([
        mocker.call(user),
        mocker.call(system),
    ])
    assert builder.lines == [
        "user = Person('User', alias='user')",
        "",
        "system = System('System', alias='system')",
        "",
    ]


def test_python_codegen__render_scope_items__boundary_elements(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
    mocker: MockerFixture,
):
    spied_render_element = mocker.spy(
        python_codegen,
        "_render_element",
    )
    with SystemContextDiagram():
        with SystemBoundary("Boundary") as boundary:
            user = Person("User", alias="user")
            system = System("System", alias="system")

    rendered = python_codegen._render_scope_items(boundary)

    assert rendered is True
    spied_render_element.assert_has_calls([
        mocker.call(user),
        mocker.call(system),
    ])
    assert builder.lines == [
        "user = Person('User', alias='user')",
        "",
        "system = System('System', alias='system')",
        "",
    ]


def test_python_codegen__render_imports(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with DynamicDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")

        with SystemBoundary("Bound", alias="bound"):
            Person("Support", alias="support")

        user >> Rel("Uses") >> system
        LayDown(user, system)
        increment(2)
        set_index(7)

    python_codegen._render_imports(diagram)

    assert builder.lines == [
        "from c4 import (",
        "    DynamicDiagram,",
        "    Person,",
        "    Rel,",
        "    System,",
        "    SystemBoundary,",
        ")",
        "from c4.contrib.plantuml import (",
        "    LayDown,",
        "    increment,",
        "    set_index,",
        ")",
        "",
        "",
    ]


def test_python_codegen__render_imports__c4_macros_use_mermaid_contrib_package():
    python_codegen = PythonCodegen(backend=RendererEnum.MERMAID)
    builder = python_codegen._builder

    with DynamicDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        system >> RelBack("Returns data") >> user

    python_codegen._render_imports(diagram)

    assert builder.lines == [
        "from c4 import (",
        "    DynamicDiagram,",
        "    Person,",
        "    System,",
        ")",
        "from c4.contrib.mermaid import (",
        "    RelBack,",
        ")",
        "",
        "",
    ]


def test_python_codegen__render_imports__c4_macros_use_plantuml_contrib_package():
    python_codegen = PythonCodegen(backend=RendererEnum.PLANTUML)
    builder = python_codegen._builder

    with DynamicDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        system >> RelBack("Returns data") >> user

    python_codegen._render_imports(diagram)

    assert builder.lines == [
        "from c4 import (",
        "    DynamicDiagram,",
        "    Person,",
        "    System,",
        ")",
        "from c4.contrib.plantuml import (",
        "    RelBack,",
        ")",
        "",
        "",
    ]


def test_python_codegen__render_imports__use_c4_macros_contrib_package():
    python_codegen = PythonCodegen(backend=None)
    builder = python_codegen._builder

    with DynamicDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        system >> RelBack("Returns data") >> user

    python_codegen._render_imports(diagram)

    assert builder.lines == [
        "from c4 import (",
        "    DynamicDiagram,",
        "    Person,",
        "    System,",
        ")",
        "from c4.contrib.c4_macros import (",
        "    RelBack,",
        ")",
        "",
        "",
    ]


def test_python_codegen__render_ordered_statement__layout(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with DynamicDiagram():
        user = Person("User", alias="user")
        system = System("System", alias="system")

        with SystemBoundary("Bound", alias="bound"):
            support = Person("Support", alias="support")

        lay_down = LayDown(user, system)
        lay_up = LayUp(support, system)

    python_codegen._render_ordered_statement(lay_down)
    python_codegen._render_ordered_statement(lay_up)

    assert builder.lines == [
        "LayDown(user, system)",
        "LayUp(support, system)",
    ]


def test_python_codegen__render_plantuml_render_options(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
    mocker: MockerFixture,
):
    render_options = PlantUMLRenderOptions()
    spied_render_options_codegen = mocker.spy(
        PlantUMLRenderOptionsCodegen,
        "generate",
    )

    python_codegen._render_plantuml_render_options(render_options)

    assert builder.lines == [
        "plantuml_render_options = PlantUMLRenderOptionsBuilder().build()",
    ]
    spied_render_options_codegen.assert_called_once_with(
        mocker.ANY,  # PlantUMLRenderOptionsCodegen self
        render_options,
    )


def test_python_codegen__render_properties__skips_default_header_without_rows(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    props = DiagramElementProperties()

    python_codegen._render_properties("x", props)

    assert builder.lines == []


@pytest.mark.parametrize(
    ("props", "expected_lines"),
    [
        (
            DiagramElementProperties(show_header=True),
            [],
        ),
        (
            DiagramElementProperties(
                show_header=False, properties=[["k1", "v1"]]
            ),
            [
                "x.without_property_header()",
                "x.add_property('k1', 'v1')",
                "",
            ],
        ),
        (
            DiagramElementProperties(
                header=["A", "B"], properties=[["k1", "v1"]]
            ),
            [
                "x.set_property_header('A', 'B')",
                "x.add_property('k1', 'v1')",
                "",
            ],
        ),
        (
            DiagramElementProperties(properties=[["k1", "v1"], ["k2", "v2"]]),
            [
                "x.add_property('k1', 'v1')",
                "x.add_property('k2', 'v2')",
                "",
            ],
        ),
        (
            DiagramElementProperties(
                show_header=False,
                header=["A", "B"],
                properties=[["k1", "v1"], ["k2", "v2"]],
            ),
            [
                "x.without_property_header()",
                "x.add_property('k1', 'v1')",
                "x.add_property('k2', 'v2')",
                "",
            ],
        ),
        (
            DiagramElementProperties(
                show_header=True,
                header=["A", "B"],
                properties=[["k1", "v1"], ["k2", "v2"]],
            ),
            [
                "x.set_property_header('A', 'B')",
                "x.add_property('k1', 'v1')",
                "x.add_property('k2', 'v2')",
                "",
            ],
        ),
        (
            DiagramElementProperties(
                show_header=True,
                header=["Property", "Value"],
                properties=[["k1", "v1"], ["k2", "v2"]],
            ),
            [
                "x.add_property('k1', 'v1')",
                "x.add_property('k2', 'v2')",
                "",
            ],
        ),
        (
            DiagramElementProperties(
                show_header=True, header=["Property", "Value"], properties=[]
            ),
            [],
        ),
    ],
    ids=[
        "no_rows",
        "without_property_header",
        "set_property_header",
        "add_properties",
        "add_properties__without_property_header",
        "add_properties__set_property_header",
        "add_properties__default_header",
        "show_header__no_properties",
    ],
)
def test_python_codegen__render_properties__emits_expected_statements(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
    props: DiagramElementProperties,
    expected_lines: list[str],
):
    python_codegen._render_properties("x", props)

    assert builder.lines == expected_lines


def test_python_codegen__render_relationship(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    with SystemContextDiagram():
        user = Person("User", alias="user")
        system = System("System", alias="system")
        relationship = user >> Rel("Uses") >> system

    python_codegen._render_relationship(relationship)

    assert builder.lines == ["user >> Rel('Uses') >> system"]


def test_python_codegen__render_relationship_with_attrs(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
):
    rel_attrs = {
        "label": "Uses",
        "description": "Interacts with",
        "technology": "HTTP",
        "plantuml": {
            "sprite": "$sprite",
            "tags": "web,ui",
            "link": "https://example.com",
            "index": "Index(1)",
        },
    }
    expected_rel_attrs = (
        "'Uses', 'Interacts with', technology='HTTP', "
        "plantuml={'sprite': '$sprite', 'tags': 'web,ui', "
        "'link': 'https://example.com', 'index': 'Index(1)'}"
    )
    with SystemContextDiagram():
        user = Person("User", alias="user")
        system = System("System", alias="system")
        relationship = user >> RelUp(**rel_attrs) >> system

    python_codegen._render_relationship(relationship)

    assert builder.lines == [f"user >> RelUp({expected_rel_attrs}) >> system"]


def test_python_codegen__render_relationship_with_properties(
    python_codegen: PythonCodegen,
):
    with SystemContextDiagram() as diagram:
        user = Person("User")
        system = System("System")
        email_provider = SystemExt("Email Provider")

        relationship = user >> Rel("Uses") >> system
        relationship.set_property_header("Key", "Value")
        relationship.add_property("Channel", "Web")
        relationship.add_property("Region", "EU")

        system >> Rel("Uses").add_property("Fallback", "SMTP") >> email_provider
    expected_result = textwrap.dedent(
        """
        from c4 import (
            Person,
            Rel,
            System,
            SystemContextDiagram,
            SystemExt,
        )


        with SystemContextDiagram() as diagram:
            user = Person('User', alias='user')

            system = System('System', alias='system')

            email_provider = SystemExt('Email Provider', alias='email_provider')

            rel_user_system = user >> Rel('Uses') >> system
            rel_user_system.set_property_header('Key', 'Value')
            rel_user_system.add_property('Channel', 'Web')
            rel_user_system.add_property('Region', 'EU')

            rel_system_email_provider = system >> Rel('Uses') >> email_provider
            rel_system_email_provider.add_property('Fallback', 'SMTP')
        """
    ).strip()

    result = python_codegen.generate(diagram)

    assert expected_result == result.strip()


def test_python_codegen__render_scope_items__diagram_relationships(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
    mocker: MockerFixture,
):
    spied_render_relationship = mocker.spy(
        python_codegen,
        "_render_relationship",
    )
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        rel1 = user >> Rel("Send requests") >> system
        rel2 = system >> Rel("Send responses") >> user

    rendered = python_codegen._render_scope_items(diagram)

    assert rendered is True
    spied_render_relationship.assert_has_calls([
        mocker.call(rel1),
        mocker.call(rel2),
    ])
    assert builder.lines == [
        "user = Person('User', alias='user')",
        "",
        "system = System('System', alias='system')",
        "",
        "user >> Rel('Send requests') >> system",
        "system >> Rel('Send responses') >> user",
    ]


def test_python_codegen__render_scope_items__boundary_relationships(
    python_codegen: PythonCodegen,
    builder: IndentedStringBuilder,
    mocker: MockerFixture,
):
    spied_render_relationship = mocker.spy(
        python_codegen,
        "_render_relationship",
    )
    with SystemContextDiagram():
        with SystemBoundary("boundary") as boundary:
            user = Person("User", alias="user")
            system = System("System", alias="system")
            rel1 = user >> Rel("Send requests") >> system
            rel2 = system >> Rel("Send responses") >> user

    rendered = python_codegen._render_scope_items(boundary)

    assert rendered is True
    spied_render_relationship.assert_has_calls([
        mocker.call(rel1),
        mocker.call(rel2),
    ])
    assert builder.lines == [
        "user = Person('User', alias='user')",
        "",
        "system = System('System', alias='system')",
        "",
        "user >> Rel('Send requests') >> system",
        "system >> Rel('Send responses') >> user",
    ]


def test_python_codegen__generate(
    python_codegen: PythonCodegen,
):
    render_options = RenderOptions(plantuml=PlantUMLRenderOptions())
    with DynamicDiagram("D", render_options=render_options) as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system
        increment()
        LayDown(user, system)
    expected_result = textwrap.dedent(
        """
        from c4 import (
            DynamicDiagram,
            Person,
            Rel,
            System,
        )
        from c4.contrib.plantuml import (
            LayDown,
            increment,
        )
        from c4.renderers import (
            PlantUMLRenderOptionsBuilder,
        )


        with DynamicDiagram(title='D') as diagram:
            user = Person('User', alias='user')

            system = System('System', alias='system')

            user >> Rel('Uses') >> system
            increment(1)

            LayDown(user, system)


        plantuml_render_options = PlantUMLRenderOptionsBuilder().build()

        diagram.set_render_options(
            plantuml=plantuml_render_options,
        )
        """
    ).strip()

    result = python_codegen.generate(diagram)

    assert result == expected_result


def test_python_codegen__generate_empty_diagram(
    python_codegen: PythonCodegen,
):
    render_options = RenderOptions(plantuml=PlantUMLRenderOptions())
    diagram = DynamicDiagram("D", render_options=render_options)
    expected_result = textwrap.dedent(
        """
        from c4 import (
            DynamicDiagram,
        )
        from c4.renderers import (
            PlantUMLRenderOptionsBuilder,
        )


        with DynamicDiagram(title='D') as diagram:
            pass


        plantuml_render_options = PlantUMLRenderOptionsBuilder().build()

        diagram.set_render_options(
            plantuml=plantuml_render_options,
        )
        """
    ).strip()

    result = python_codegen.generate(diagram)

    assert result == expected_result


def test_python_codegen__generate__no_render_options(
    python_codegen: PythonCodegen,
):
    with DynamicDiagram("D") as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system
        increment()
        LayDown(user, system)
    expected_result = (
        textwrap.dedent(
            """
        from c4 import (
            DynamicDiagram,
            Person,
            Rel,
            System,
        )
        from c4.contrib.plantuml import (
            LayDown,
            increment,
        )


        with DynamicDiagram(title='D') as diagram:
            user = Person('User', alias='user')

            system = System('System', alias='system')

            user >> Rel('Uses') >> system
            increment(1)

            LayDown(user, system)
        """
        ).strip()
        + "\n"
    )

    result = python_codegen.generate(diagram)

    assert result == expected_result


def test_diagram_to_python_code__render_options_plantuml(
    python_codegen: PythonCodegen,
):
    render_options = RenderOptions(plantuml=PlantUMLRenderOptions())
    with DynamicDiagram("D", render_options=render_options) as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system
        increment()
        LayDown(user, system)
    expected_result = textwrap.dedent(
        """
        from c4 import (
            DynamicDiagram,
            Person,
            Rel,
            System,
        )
        from c4.contrib.plantuml import (
            LayDown,
            increment,
        )
        from c4.renderers import (
            PlantUMLRenderOptionsBuilder,
        )


        with DynamicDiagram(title='D') as diagram:
            user = Person('User', alias='user')

            system = System('System', alias='system')

            user >> Rel('Uses') >> system
            increment(1)

            LayDown(user, system)


        plantuml_render_options = PlantUMLRenderOptionsBuilder().build()

        diagram.set_render_options(
            plantuml=plantuml_render_options,
        )
        """
    ).strip()

    result = diagram_to_python_code(diagram)

    assert result == expected_result


def test_diagram_to_python_code__render_options_mermaid(
    python_codegen: PythonCodegen,
):
    render_options = RenderOptions(mermaid=MermaidRenderOptions())
    with DynamicDiagram("D", render_options=render_options) as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system
        increment()
        LayDown(user, system)
    expected_result = textwrap.dedent(
        """
        from c4 import (
            DynamicDiagram,
            Person,
            Rel,
            System,
        )
        from c4.contrib.plantuml import (
            LayDown,
            increment,
        )
        from c4.renderers import (
            MermaidRenderOptionsBuilder,
        )


        with DynamicDiagram(title='D') as diagram:
            user = Person('User', alias='user')

            system = System('System', alias='system')

            user >> Rel('Uses') >> system
            increment(1)

            LayDown(user, system)


        mermaid_render_options = MermaidRenderOptionsBuilder().build()

        diagram.set_render_options(
            mermaid=mermaid_render_options,
        )
        """
    ).strip()

    result = diagram_to_python_code(diagram)

    assert result == expected_result


def test_diagram_to_python_code__all_render_options(
    python_codegen: PythonCodegen,
):
    render_options = RenderOptions(
        plantuml=PlantUMLRenderOptions(), mermaid=MermaidRenderOptions()
    )
    with DynamicDiagram("D", render_options=render_options) as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system
        increment()
        LayDown(user, system)
    expected_result = textwrap.dedent(
        """
        from c4 import (
            DynamicDiagram,
            Person,
            Rel,
            System,
        )
        from c4.contrib.plantuml import (
            LayDown,
            increment,
        )
        from c4.renderers import (
            MermaidRenderOptionsBuilder,
            PlantUMLRenderOptionsBuilder,
        )


        with DynamicDiagram(title='D') as diagram:
            user = Person('User', alias='user')

            system = System('System', alias='system')

            user >> Rel('Uses') >> system
            increment(1)

            LayDown(user, system)


        plantuml_render_options = PlantUMLRenderOptionsBuilder().build()
        mermaid_render_options = MermaidRenderOptionsBuilder().build()

        diagram.set_render_options(
            plantuml=plantuml_render_options,
            mermaid=mermaid_render_options,
        )
        """
    ).strip()

    result = diagram_to_python_code(diagram)

    assert result == expected_result


def test_diagram_to_python_code__no_render_options(
    python_codegen: PythonCodegen,
):
    with DynamicDiagram("D") as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system
        increment()
        LayDown(user, system)
    expected_result = (
        textwrap.dedent(
            """
        from c4 import (
            DynamicDiagram,
            Person,
            Rel,
            System,
        )
        from c4.contrib.plantuml import (
            LayDown,
            increment,
        )


        with DynamicDiagram(title='D') as diagram:
            user = Person('User', alias='user')

            system = System('System', alias='system')

            user >> Rel('Uses') >> system
            increment(1)

            LayDown(user, system)
        """
        ).strip()
        + "\n"
    )

    result = diagram_to_python_code(diagram)

    assert result == expected_result


def test_diagram_to_python_code__empty_renderer_options(
    python_codegen: PythonCodegen,
):
    render_options = RenderOptions(plantuml=None)
    with DynamicDiagram("D", render_options=render_options) as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system
        increment()
        LayDown(user, system)
    expected_result = (
        textwrap.dedent(
            """
        from c4 import (
            DynamicDiagram,
            Person,
            Rel,
            System,
        )
        from c4.contrib.plantuml import (
            LayDown,
            increment,
        )


        with DynamicDiagram(title='D') as diagram:
            user = Person('User', alias='user')

            system = System('System', alias='system')

            user >> Rel('Uses') >> system
            increment(1)

            LayDown(user, system)
        """
        ).strip()
        + "\n"
    )

    result = diagram_to_python_code(diagram)

    assert result == expected_result
