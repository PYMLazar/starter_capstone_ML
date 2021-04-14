import json
import os
import sys
from flask import request, _request_ctx_stack, abort, session
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from os import environ


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
        print("token is leeg")
        return token



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


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    print("unver_header", unverified_header)
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
            print("payload",payload)
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError("token has expired", 401)
        except jwt.JWTClaimsError:
            raise AuthError("invalid claims (Error): check the audience", 401)
        except Exception:
            raise AuthError("invalid header: Unable to parse token", 401)

    print("rsa_key",rsa_key)     
    raise AuthError("invalid header: Unable to find right key", 401)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        #print(permission)
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # print("test abort 0")
				# print("token", token)
                # token = None
                # if session['token']:
                #     token = session['token']
                print("test requires_auth_abort 0.1")
                # else:
                token = get_token_auth_header()
                print("test requires_auth_abort 0.2",  token)
                # print('token at authorization time: {}'.format(token))
                # if token is None:
                #     print("test abort 0.3")
                #     abort(400)
                payload = verify_decode_jwt(token)
                #print("PAYLOAD_test abort 3")
                print('Payload is: {}'.format(payload))
                print(f'testing for permission: {permission}')
                if check_permissions(permission, payload):
                    print('Permission is in permissions!')
                
                return f(payload, *args, **kwargs)
            except Exception:
                abort(401)


        return wrapper
    return requires_auth_decorator
