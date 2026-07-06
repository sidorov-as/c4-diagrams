from c4 import (
    Container,
    ContainerDb,
    ContainerDiagram,
    Person,
    Rel,
    SystemBoundary,
)


with ContainerDiagram(title='Web App') as diagram:
    user = Person('User', alias='user')

    with SystemBoundary('Simple System', alias='system'):
        web = Container('Web App', technology='React', alias='web')

        api = Container('API', technology='Python', alias='api')

        db = ContainerDb('Database', technology='PostgreSQL', alias='db')

    user >> Rel('Uses') >> web
    web >> Rel('Calls') >> api
    api >> Rel('Reads/Writes') >> db
