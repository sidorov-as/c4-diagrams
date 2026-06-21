from c4 import (
    Person,
    Rel,
    System,
    SystemContextDiagram,
)


with SystemContextDiagram() as diagram:
    user = Person('User', alias='user')

    app = System('My App', alias='app')

    user >> Rel('Uses', technology='HTTPS') >> app
