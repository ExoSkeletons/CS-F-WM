import firebase_admin
from firebase_admin import credentials, firestore

from ui.app import data_dir_path


def init_db():
    cred = credentials.Certificate(data_dir_path + 'serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

    return firestore.client()
