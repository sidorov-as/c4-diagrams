from c4 import (
    DynamicDiagram,
    Person,
    Rel,
    System,
    SystemExt,
)


with DynamicDiagram(title='Login Flow') as diagram:
    user = Person('User', 'Signs in to the application.', alias='user')

    web_app = System('Web App', 'Main application used by customers.', alias='web_app')

    idp = SystemExt('Identity Provider', 'External authentication service.', alias='idp')

    user >> Rel('Opens sign-in page', technology='HTTPS') >> web_app
    web_app >> Rel('Authenticates user', technology='OIDC') >> idp
    idp >> Rel('Returns identity token', technology='OIDC') >> web_app
