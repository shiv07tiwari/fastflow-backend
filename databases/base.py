import json
import os

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage

load_dotenv()

firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
cred_dict = json.loads(firebase_credentials)
cred = credentials.Certificate(cred_dict)
# cred = credentials.Certificate(os.getenv('FIRESTORE_CRED_PATH'))

firebase = firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv('FIRESTORE_STORAGE_BUCKET')
})
db = firestore.client()

bucket = storage.bucket(app=firebase)
