from c4 import Rel, System, SystemContextDiagram


def test__render_empty_relationship_labels():
    """
    Regression test for issue: https://github.com/sidorov-as/c4-diagrams/issues/26
    """
    with SystemContextDiagram() as diagram:
        s1 = System(alias="s1", label="System 1")
        s2 = System(alias="s2", label="System 2")
        s3 = System(alias="s3", label="System 3")

        s1 >> Rel("") >> s2
        s2 >> "" >> s3

    result = diagram.as_plantuml()

    assert 'Rel(s1, s2, "")' in result
    assert 'Rel(s2, s3, "")' in result
