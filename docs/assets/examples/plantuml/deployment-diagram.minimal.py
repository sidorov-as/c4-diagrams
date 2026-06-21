from c4 import (
    Container,
    ContainerDb,
    DeploymentDiagram,
    DeploymentNode,
    Person,
    Rel,
)


with DeploymentDiagram(title='Web App Deployment') as diagram:
    user = Person('User', 'Uses the web application.', plantuml={'tags': []}, alias='user')

    with DeploymentNode('Web Server', 'Hosts the frontend application.', alias='web_node') as web_node:
        web_app = Container('Web App', 'Customer-facing web application.', plantuml={'tags': []}, technology='Next.js', alias='web_app')

    with DeploymentNode('Database Server', 'Hosts the application database.', alias='db_node') as db_node:
        app_db = ContainerDb('App Database', 'Stores application data.', plantuml={'tags': []}, technology='PostgreSQL', alias='app_db')

    user >> Rel('Uses', technology='HTTPS', plantuml={'tags': []}) >> web_node
    web_node >> Rel('Reads and writes', technology='TLS / SQL', plantuml={'tags': []}) >> db_node
