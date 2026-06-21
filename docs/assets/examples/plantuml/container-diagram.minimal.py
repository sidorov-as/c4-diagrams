from c4 import (
    Container,
    ContainerDb,
    ContainerDiagram,
    Person,
    Rel,
    SystemBoundary,
)


with ContainerDiagram(title='Web App') as diagram:
    user = Person('User', plantuml={'tags': []}, alias='user')

    with SystemBoundary('Simple System', alias='system'):
        web = Container('Web App', plantuml={'tags': []}, technology='React', alias='web')

        api = Container('API', plantuml={'tags': []}, technology='Python', alias='api')

        db = ContainerDb('Database', plantuml={'tags': []}, technology='PostgreSQL', alias='db')

    user >> Rel('Uses', plantuml={'tags': []}) >> web
    web >> Rel('Calls', plantuml={'tags': []}) >> api
    api >> Rel('Reads/Writes', plantuml={'tags': []}) >> db
