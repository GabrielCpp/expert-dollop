import os
from google.cloud import firestore

os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8806"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "firestore-328801-55cbd35d6877.json"

# Add a new document
db = firestore.Client()
doc_ref = db.collection(u"users").document(u"alovelace")
doc_ref.set(
    {
        u"first": u"Ada",
        u"last": u"Lovelace",
        u"born": 1815,
        "config": {"triggers": [{"name": "TOGGLE_VISIBILITY"}]},
    }
)

# Then query for documents
users_ref = db.collection(u"users")

for doc in users_ref.stream():
    print(u"{} => {}".format(doc.id, doc.to_dict()))
