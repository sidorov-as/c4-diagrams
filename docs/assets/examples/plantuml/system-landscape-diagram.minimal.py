from c4 import (
    Person,
    Rel,
    System,
    SystemLandscapeDiagram,
)


with SystemLandscapeDiagram() as diagram:
    user = Person('User', plantuml={'tags': []}, alias='user')

    app = System('My App', plantuml={'tags': []}, alias='app')

    user >> Rel('Uses', technology='HTTPS', plantuml={'tags': []}) >> app
