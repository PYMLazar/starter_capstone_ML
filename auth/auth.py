import json
import os
import sys
from flask import request, _request_ctx_stack, abort, session
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from os import environ


#AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_DOMAIN = 'fsnd-ml-casting-agency.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'Casting'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
# def get_token_auth_header():
# #     """Obtains the Access Token from the Authorization Header
# #     """
#     if "Authorization" in request.headers:
#         auth_header = request.headers["Authorization"]
#         if auth_header:
#             bearer_token_array = auth_header.split(' ')
#             if bearer_token_array[0] and bearer_token_array[0].lower() == "bearer" and bearer_token_array[1]:
#                 return bearer_token_array[1]

#     raise AuthError({
#         'success': False,
#         'message': 'JWT not found',
#         'error': 401
#     }, 401) 


def get_token_auth_header():
        auth = request.headers.get('Authorization', None)
        print(auth)
        if not auth:
            raise AuthError({
                'code': 'authorization_header_missing',
                'description': 'Authorization header is expected.'
            }, 401)

        parts = auth.split()
        if parts[0].lower() != 'bearer':
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Authorization header must start with "Bearer".'
            }, 401)

        elif len(parts) == 1:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Token not found.'
            }, 401)

        elif len(parts) > 2:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Authorization header must be bearer token.'
            }, 401)

        token = parts[1]
        return token

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload
    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in
         Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        #raise AuthError('Permissions not included in JWT', 400)
        print('permissions not in payload')
        abort(400)

    if permission not in payload['permissions']:
        print(f'{permission} not in {payload["permissions"]}')
        raise AuthError({
            'success': False,
            'message': 'Permission not found in JWT',
            'error': 401
        }, 401)

    return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)
    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload
    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    #print("jwsks",jwks)
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
           
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://"+AUTH0_DOMAIN+"/"
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError("token has expired", 401)
        except jwt.JWTClaimsError:
            raise AuthError("invalid claims (Error): check the audience", 401)
        except Exception:
            raise AuthError("invalid header: Unable to parse token", 401)

    print("rsa_key",rsa_key)     
    raise AuthError("invalid header: Unable to find right key", 401)



'''
@TODO implement @
(permission) decorator method
    @INPUTS
    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        #print(permission)
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                print("test_abort_0")
                token = None
                if session['token']:
                    token = session['token']
                    #print (test abort 0.1)
                else:
                    token = get_token_auth_header()
                    #print (test abort 0.2)
                print('token at authorization time: {}'.format(token))
                if token is None:
                    #print (test abort 0.3)
                    abort(400)
                payload = verify_decode_jwt(token)
                print('Payload is: {}'.format(payload))
                print(f'testing for permission: {permission}')
                if check_permissions(permission, payload):
                    print('Permission is in permissions!')
                
                return f(payload, *args, **kwargs)
            except Exception:
                abort(401)


        return wrapper
    return requires_auth_decorator  

# def requires_auth(permission=''):
#     def requires_auth_decorator(f):
#         @wraps(f)
#         def wrapper(*args, **kwargs):
#             jwt = get_token_auth_header()
#             try:
#                 payload = verify_decode_jwt(jwt)
#             except:
#                 abort(401)

#             check_permissions(permission, payload)    
            
#             return f(payload, *args, **kwargs)
#         return wrapper
#     return requires_auth_decorator    

