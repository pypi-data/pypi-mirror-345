import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore as f
from firebase_admin.firestore import firestore
from firebase_admin.exceptions import FirebaseError
from firebase_admin.auth import TokenSignError
from firebase_admin.auth import ActionCodeSettings

import os

import pydash

from firebase_admin import auth

def create_firebase_user(email, password) -> 'auth.UserRecord':
    try:
        return auth.create_user(email=email, password=password)
    except ValueError as e:
        raise e
    except FirebaseError as e:
        raise e;  

def create_firebase_custom_token(uid) -> 'auth.UserRecord':
    try:
        return auth.create_custom_token(uid)
    except ValueError as e:
        raise e
    except TokenSignError as e:
        raise e;  

def generate_email_verification_link(email, url) -> 'str':
    try:
        return auth.generate_email_verification_link(email, action_code_settings=ActionCodeSettings(url=url))
    except ValueError as e:
        return None
    except FirebaseError as e:
        return None;  

def generate_password_reset_link(email, url) -> 'str':
    try:
        return auth.generate_password_reset_link(email, action_code_settings=ActionCodeSettings(url=url))
    except ValueError as e:
        return None
    except FirebaseError as e:
        return None;  

def get_user_by_uid(uid) -> 'auth.UserRecord':
    try:
        return auth.get_user(uid)
    except ValueError as e:
        return None;
    except FirebaseError as e:
        return None; 


def get_user_by_email(email) -> 'auth.UserRecord':
    try:
        return auth.get_user_by_email(email)
    except ValueError as e:
        return None;
    except FirebaseError as e:
        return None; 

def get_user_by_phone_number(phone_number) -> 'auth.UserRecord':
    try:
        return auth.get_user_by_phone_number(phone_number)
    except ValueError as e:
        return None;
    except FirebaseError as e:
        return None; 

def update_firebase_user(uid, **kwargs) -> 'auth.UserRecord':
    """
    Keyword Args:
    display_name: The user's display name (optional). Can be removed by explicitly passing
        auth.DELETE_ATTRIBUTE.
    email: The user's primary email (optional).
    email_verified: A boolean indicating whether or not the user's primary email is
        verified (optional).
    phone_number: The user's primary phone number (optional). Can be removed by explicitly
        passing auth.DELETE_ATTRIBUTE.
      photo_url: The user's photo URL (optional). Can be removed by explicitly passing
        auth.DELETE_ATTRIBUTE.
    password: The user's raw, unhashed password. (optional).
    disabled: A boolean indicating whether or not the user account is disabled (optional).
    custom_claims: A dictionary or a JSON string containing the custom claims to be set on the
        user account (optional). To remove all custom claims, pass auth.DELETE_ATTRIBUTE.
    valid_since: An integer signifying the seconds since the epoch (optional). This field is
        set by revoke_refresh_tokens and it is discouraged to set this field directly.
    app: An App instance (optional).

    Returns:
        UserRecord: An updated user record instance for the user."""
    try:
        return auth.update_user(uid, **kwargs)
    except ValueError as e:
        return None
    except FirebaseError as e:
        return None;  

def set_custom_claims(uid, claims):
    try:
        user = auth.get_user(uid)
        current_claims = user.custom_claims;
        if current_claims is None:
            current_claims = {}
        for key in pydash.keys(claims):
            current_claims[key] = claims[key]
        auth.set_custom_user_claims(uid, current_claims)
        docRef = FirestoreApp().firestore_client().collection('users').document(uid)
        docRef.set({"current_claims": current_claims}, merge=True)
        return docRef.get().to_dict()
    except Exception as e:
        return None

DEFAULT_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH');

def initializeApp(path: str):
    if path is None:
        return None;
    try:
        absolute_path = os.path.dirname(__file__)
        relative_path = path
        # print('relative_path',relative_path)
        if relative_path.startswith('http'):
            credentials_path = relative_path
        else:
            credentials_path = os.path.join(absolute_path, relative_path)
        cred = credentials.Certificate(credentials_path);
        if len(firebase_admin._apps)==0:
            app = firebase_admin.initialize_app(cred);
            return app;
        return firebase_admin.get_app()
    except Exception as e:
        print(e)
        return None
    
class FirestoreApp:
    def __init__(self, credentials_path: str=DEFAULT_PATH) -> None:
        # print("Initializing Firestore from", credentials_path)
        app = initializeApp(credentials_path);
        if app is not None:
            self.app = app;
            
    
    def firestore_client(self) -> firestore.Client:
        app = getattr(self, 'app', None)
        if app is None:
            return None;
        firestore_database = f.client(self.app);
        return firestore_database;
