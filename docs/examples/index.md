# Examples

## Same portable model, backend defaults

These examples use the same portable C4 core elements for each diagram type and
intentionally avoid backend-specific styling or layout hints. They show how the
same model is rendered by each backend's defaults.

### System context diagram

??? abstract "Python diagram"

    ```python
    --8<-- "assets/examples/python/common/common-system-context-diagram.py"
    ```

=== "PlantUML"

    <figure markdown="span">
      ![PlantUML system context example](../assets/examples/plantuml/common-system-context-diagram.png)
      <figcaption>PlantUML system context diagram</figcaption>
    </figure>

=== "Mermaid"

    <figure markdown="span">
      ![Mermaid system context example](../assets/examples/mermaid/common-system-context-diagram.png)
      <figcaption>Mermaid system context diagram</figcaption>
    </figure>

### System landscape diagram

??? abstract "Python diagram"

    ```python
    --8<-- "assets/examples/python/common/common-system-landscape-diagram.py"
    ```

=== "PlantUML"

    <figure markdown="span">
      ![PlantUML system landscape example](../assets/examples/plantuml/common-system-landscape-diagram.png)
      <figcaption>PlantUML system landscape diagram</figcaption>
    </figure>

=== "Mermaid"

    <figure markdown="span">
      ![Mermaid system landscape example](../assets/examples/mermaid/common-system-landscape-diagram.png)
      <figcaption>Mermaid system landscape diagram</figcaption>
    </figure>

### Container diagram

??? abstract "Python diagram"

    ```python
    --8<-- "assets/examples/python/common/common-container-diagram.py"
    ```

=== "PlantUML"

    <figure markdown="span">
      ![PlantUML container example](../assets/examples/plantuml/common-container-diagram.png)
      <figcaption>PlantUML container diagram</figcaption>
    </figure>

=== "Mermaid"

    <figure markdown="span">
      ![Mermaid container example](../assets/examples/mermaid/common-container-diagram.png)
      <figcaption>Mermaid container diagram</figcaption>
    </figure>

### Component diagram

??? abstract "Python diagram"

    ```python
    --8<-- "assets/examples/python/common/common-component-diagram.py"
    ```

=== "PlantUML"

    <figure markdown="span">
      ![PlantUML component example](../assets/examples/plantuml/common-component-diagram.png)
      <figcaption>PlantUML component diagram</figcaption>
    </figure>

=== "Mermaid"

    <figure markdown="span">
      ![Mermaid component example](../assets/examples/mermaid/common-component-diagram.png)
      <figcaption>Mermaid component diagram</figcaption>
    </figure>

### Dynamic diagram

??? abstract "Python diagram"

    ```python
    --8<-- "assets/examples/python/common/common-dynamic-diagram.py"
    ```

=== "PlantUML"

    <figure markdown="span">
      ![PlantUML dynamic example](../assets/examples/plantuml/common-dynamic-diagram.png)
      <figcaption>PlantUML dynamic diagram</figcaption>
    </figure>

=== "Mermaid"

    <figure markdown="span">
      ![Mermaid dynamic example](../assets/examples/mermaid/common-dynamic-diagram.png)
      <figcaption>Mermaid dynamic diagram</figcaption>
    </figure>

### Deployment diagram

??? abstract "Python diagram"

    ```python
    --8<-- "assets/examples/python/common/common-deployment-diagram.py"
    ```

=== "PlantUML"

    <figure markdown="span">
      ![PlantUML deployment example](../assets/examples/plantuml/common-deployment-diagram.png)
      <figcaption>PlantUML deployment diagram</figcaption>
    </figure>

=== "Mermaid"

    <figure markdown="span">
      ![Mermaid deployment example](../assets/examples/mermaid/common-deployment-diagram.png)
      <figcaption>Mermaid deployment diagram</figcaption>
    </figure>

## Same model, backend-tuned outputs

This example keeps the same C4 elements and relationships, then applies
backend-specific rendering options to make each output easier to read.

### Sysops support system component view

=== "PlantUML"

    <figure markdown="span">
      ![PlantUML tuned Sysops component example](../assets/examples/plantuml/tuned-sysops-component-diagram.png)
      <figcaption>PlantUML tuned component diagram</figcaption>
    </figure>

    ??? abstract "Python diagram"

        ```python
        --8<-- "assets/examples/python/custom/plantuml/tuned-sysops-component-diagram.py"
        ```

    ??? abstract "Rendered PlantUML source"

        ```puml
        --8<-- "assets/examples/plantuml/tuned-sysops-component-diagram.puml"
        ```

=== "Mermaid"

    <figure markdown="span">
      ![Mermaid tuned Sysops component example](../assets/examples/mermaid/tuned-sysops-component-diagram.png)
      <figcaption>Mermaid tuned component diagram</figcaption>
    </figure>

    ??? abstract "Python diagram"

        ```python
        --8<-- "assets/examples/python/custom/mermaid/tuned-sysops-component-diagram.py"
        ```

    ??? abstract "Rendered Mermaid source"

        ```mmd
        --8<-- "assets/examples/mermaid/tuned-sysops-component-diagram.mmd"
        ```

PlantUML is useful when you need rich C4 styling, legends, tags, and stronger
layout nudges. Mermaid is useful when you want simple text output that embeds
well in Markdown-centric tools, but its C4 support has fewer tuning controls.
