from c4 import (
    DynamicDiagram,
    Person,
    Rel,
    System,
    SystemExt,
)


with DynamicDiagram(title='Login Flow') as diagram:
    user = Person('User', 'Signs in to the application.', plantuml={'tags': []}, alias='user')

    web_app = System('Web App', 'Main application used by customers.', plantuml={'tags': []}, alias='web_app')

    idp = SystemExt('Identity Provider', 'External authentication service.', plantuml={'tags': []}, alias='idp')

    user >> Rel('Opens sign-in page', technology='HTTPS', plantuml={'tags': []}) >> web_app
    web_app >> Rel('Authenticates user', technology='OIDC', plantuml={'tags': []}) >> idp
    idp >> Rel('Returns identity token', technology='OIDC', plantuml={'tags': []}) >> web_app
