from authlib.jose import JsonWebKey
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from joserfc.jwk import RSAKey
import os
key_size = 2048
key = RSAKey.generate_key(key_size)
print('gen', key.alg)
rsa = RSAKey.import_key(open(os.getcwd()+"/private.pem", 'r').read())
print(rsa.alg)

# private_key = key.
# print('import', RSAKey.import_key(open(os.getcwd()+"/private.pem", 'r').read()))

# Step 1: Generate RSA private key
# private_key = rsa.generate_private_key(
#     public_exponent=65537,
#     key_size=2048,
#     backend=default_backend()
# )

# Step 2: Generate a JWK (JSON Web Key) from the RSA key
# jwk = JsonWebKey().generate_key(kty='RSA', crv_or_size=2048, options={'alg': 'RS256'})

# print(private_key.
# Convert the private key to JWK format
private_jwk = rsa.as_dict(is_private=True)
public_jwk = rsa.as_dict(is_private=False)

# print("Private JWK:", private_jwk)
# print("Public JWK:", public_jwk)
jwk_set = {
    "keys": [public_jwk]
}

# @app.route('/jwks')
# def jwks():
#     return jsonify(jwk_set)

# Save the keys as needed