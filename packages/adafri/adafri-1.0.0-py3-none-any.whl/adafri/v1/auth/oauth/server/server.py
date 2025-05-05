from authlib.integrations.flask_oauth2 import (
    AuthorizationServer,
    ResourceProtector,
)
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge

from ...oauth import (OAuthClient, OAuthToken, AuthorizationCodeGrant as AuthCodeGrant, 
                                TokenRevocationEndpoint, TokenValidator, RefreshTokenGrant, TokenGenerator)

class AuthServer(AuthorizationServer):
    OAUTH2_TOKEN_EXPIRES_IN = {
    'authorization_code': 86400,
    'implicit': 3600,
    'password': 86400,
    'client_credentials': 86400
    }
    def authenticate_client(self, request, methods, endpoint='token'):
        return super().authenticate_client(request, methods, endpoint)
    
    def handle_error_response(self, request, error):
        return self.handle_response(*error(self.get_error_uri(request, error)))
    

# authorization_server = AuthServer(
#     query_client=OAuthClient().get_by_client_id,
#     save_token=OAuthToken().save,
# )
authorization_server = AuthorizationServer()
require_oauth = ResourceProtector()

require_oauth = ResourceProtector()

def config_oauth(app, query_client=None, save_token=None, token_generators=[]):
    if query_client is None:
        query_client = OAuthClient().get_by_client_id
    if save_token is None:
        save_token = OAuthToken().save
    authorization_server.query_client = query_client
    authorization_server.save_token = save_token
    authorization_server.init_app(app)
    
    authorization_server.register_grant(grants.ImplicitGrant)
    #authorization_server.register_grant(AccessTokenGrant, [CodeChallenge(required=True)])
    authorization_server.register_grant(grants.ClientCredentialsGrant)
    authorization_server.register_grant(AuthCodeGrant, [CodeChallenge(required=True)])
    
    # authorization_server.register_grant(PasswordGrant)
    authorization_server.register_grant(RefreshTokenGrant)
    # support revocation
    # revocation_cls = create_revocation_endpoint()
    authorization_server.register_endpoint(TokenRevocationEndpoint)
    # for token_generator in token_generators:
    #     type = getattr(token_generator, 'type', None);
    #     generator = getattr(token_generator, 'generator', None);
    #     if None not in [type, generator]:
    #         authorization_server.register_token_generator(type, generator)
    authorization_server.register_token_generator("default", TokenGenerator.generate)
    authorization_server.register_token_generator("client_credentials", TokenGenerator.generate)
    # protect resource
    #bearer_cls = create_bearer_token_validator(TokenValidator)
    require_oauth.register_token_validator(TokenValidator())