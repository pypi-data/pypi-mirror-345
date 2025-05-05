import requests
from authlib.jose import JsonWebToken, KeySet
from joserfc.jwk import RSAKey
import os

from adafri.v1.base.firebase_collection import FirebaseCollectionBase

# Set your JWKS URI and issuer (OIDC provider)
CLIENT_ID = os.environ.get('ADAFRI_CLIENT_ID', None)
AUDIENCE = os.environ.get('OAUTH_AUDIENCE', CLIENT_ID)

def getDefaultClaims(well_known, audience=None):
    default_claims = {
        "iss": {"essential": True, "value": well_known['issuer']},
        "aud": {"essential": True, "value": audience},
    }
    return default_claims
def fetch_well_known(well_known_uri):
    try:
        response = requests.get(well_known_uri)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print('exception occurated while fetching well_known uri')
        return None
def fetch_jwks(jwks_uri):
    try:
        response = requests.get(jwks_uri)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print('exception occurated while fetching jwks_uri')
        return None

# Step 2: Verify the JWT token
def verify_jwt_token(token, jwks, issuer, audience, algorithms=['RS256'], claims_options=None):
    # Create a JsonWebToken instance for decoding and verification
    jwt = JsonWebToken(algorithms=algorithms)  # Specify the algorithm(s) used by your provider
    key = KeySet(jwks)
    # Verify the token using the JWKS, issuer, and audience
    claims = jwt.decode(
        token,
        key.keys,
        claims_options=claims_options,
    )
    # print('algs', algorithms)
    # Ensure the token is not expired and other claims are valid
    claims.validate()
    # print('keys', claims)
    return claims

# Fetch JWKS and verify the token
from datetime import datetime

def check_token(token, well_known_uri=None, audience=AUDIENCE):
    if well_known_uri is None:
        well_known_uri = os.environ.get('WELL_KNOWN_URI', None)
    if well_known_uri is None:
        return None
    well_known = fetch_well_known(well_known_uri)
    if well_known is None:
        return None
    if 'issuer' in well_known and 'jwks_uri' in well_known and 'id_token_signing_alg_values_supported' in well_known:
        try:
            # jwks = fetch_jwks(jwks_uri)
            jwks = fetch_jwks(well_known['jwks_uri'])
            # print('jwks', jwks)
            algorithms = well_known['id_token_signing_alg_values_supported']
            claims = verify_jwt_token(token, jwks, well_known['issuer'], audience, algorithms, getDefaultClaims(well_known, audience=audience))
            # print('claims', claims)
            if claims is not None and 'iss' in claims:
                exp = datetime.fromtimestamp(claims['exp'])
                iat = datetime.fromtimestamp(claims['iat'])
                print('exp', exp)
                print('iat', iat)
                return claims
        except Exception as e:
            print("Token verification failed:", e)
            return None
    return None

def is_existing_token(_token: str):
    db = FirebaseCollectionBase(collection_name='clients_token_collection')
    token = db.custom_query([{"key": "access_token", "comp": "==", "value": _token}], True)
    if token is not None:
        return token
    return None