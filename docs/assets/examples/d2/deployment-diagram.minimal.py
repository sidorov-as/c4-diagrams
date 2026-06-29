from c4 import (
    Container,
    ContainerDb,
    DeploymentDiagram,
    DeploymentNode,
    Person,
    Rel,
)


with DeploymentDiagram(title='Web App Deployment') as diagram:
    user = Person('User', 'Uses the web application.', alias='user')

    with DeploymentNode('Web Server', 'Hosts the frontend application.', alias='web_node'):
        web_app = Container('Web App', 'Customer-facing web application.', technology='Next.js', alias='web_app')

    with DeploymentNode('Database Server', 'Hosts the application database.', alias='db_node'):
        app_db = ContainerDb('App Database', 'Stores application data.', technology='PostgreSQL', alias='app_db')

    user >> Rel('Uses', technology='HTTPS') >> web_app
    web_app >> Rel('Reads and writes', technology='TLS / SQL') >> app_db
