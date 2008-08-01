import grok

from zope.app.authentication.httpplugins import HTTPBasicAuthCredentialsPlugin
from zope.app.authentication.interfaces import ICredentialsPlugin

from zope.app.authentication.interfaces import (
    IAuthenticatorPlugin, IPrincipalInfo)

def setup_authentication(pau):
    """Set up plugguble authentication utility.

    Sets up an IAuthenticatorPlugin and
    ICredentialsPlugin (for the authentication mechanism)
    """    
    pau.credentialsPlugins = ['credentials']
    pau.authenticatorPlugins = ['users']

class CredentialsPlugin(grok.GlobalUtility,
                        HTTPBasicAuthCredentialsPlugin):
    grok.provides(ICredentialsPlugin)
    grok.name('credentials')
    
class UserAuthenticatorPlugin(grok.GlobalUtility):
    grok.provides(IAuthenticatorPlugin)
    grok.name('users')

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        account = self._getAccount(credentials['login'])

        if account is None:
            return None
        if not account.checkPassword(credentials['password']):
            return None
        return PrincipalInfo(id=account.name,
                             title=account.name,
                             description=account.name)

    def principalInfo(self, id):
        account = self._getAccount(id)
        if account is None:
            return None
        return PrincipalInfo(id=account.name,
                             title=account.name,
                             description=account.name)

    def _getAccount(self, login):
        return grok.getSite()['accounts'].get(login, None)

class PrincipalInfo(object):
    grok.implements(IPrincipalInfo)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.credentialsPlugin = None
        self.authenticatorPlugin = None
