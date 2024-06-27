import os

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

cred = credentials.Certificate(os.getenv('FIRESTORE_CRED_PATH'))

firebase = firebase_admin.initialize_app(cred)
db = firestore.client()
