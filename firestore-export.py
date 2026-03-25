
import argparse
import json
from datetime import datetime
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import DocumentReference, GeoPoint


# ---------- Firestore serialization ----------

def serialize(value):
    """Convert Firestore types to JSON-safe types."""
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, GeoPoint):
        return {"lat": value.latitude, "lng": value.longitude}

    if isinstance(value, DocumentReference):
        return value.path

    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}

    if isinstance(value, list):
        return [serialize(v) for v in value]

    return value


# ---------- recursive export ----------

def export_document(doc_ref):
    """Export a document and its subcollections recursively."""
    snapshot = doc_ref.get()
    data = serialize(snapshot.to_dict() or {})

    # enumerate subcollections
    for subcol in doc_ref.collections():
        sub_data = {}

        for subdoc in subcol.stream():
            sub_data[subdoc.id] = export_document(subdoc.reference)

        data[subcol.id] = sub_data

    return data


def export_collection(collection_ref):
    """Export a full collection."""
    result = {}

    for doc in collection_ref.stream():
        result[doc.id] = export_document(doc.reference)

    return result

# ---------- List ---------

def list_collections(db):
    print("Root collections:")
    for col in db.collections():
        print(f" - {col.id}")


# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(
        description="Export Firestore collection recursively to JSON"
    )

    parser.add_argument(
        "-p",
        "--path",
        help="Firestore collection path (example: responses or users/user123/posts)",
        default="/",
        required=False
    )

    parser.add_argument(
        "--cred",
        default="serviceAccountKey.json",
        required=False,
        help="Path to service account key"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List root collections and exit"
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output JSON file"
    )

    args = parser.parse_args()

    cred = credentials.Certificate(args.cred)
    firebase_admin.initialize_app(cred)

    db = firestore.client()

    if args.list:
        list_collections(db)
        return

    path = args.path.strip("/")

    parts = path.split("/")

    if len(parts) % 2 == 1:
        # collection path
        parent_doc_path = "/".join(parts[:-1])

        if parent_doc_path:
            parent_doc = db.document(parent_doc_path).get()
            if not parent_doc.exists:
                raise ValueError(f"Parent document does not exist: {parent_doc_path}")

        collection_ref = db.collection(path)

    else:
        # subcollection path
        doc_path = "/".join(parts[:-1])
        subcollection = parts[-1]

        doc_ref = db.document(doc_path)
        doc_snapshot = doc_ref.get()

        if not doc_snapshot.exists:
            raise ValueError(f"Document path does not exist: {doc_path}")

        collection_ref = doc_ref.collection(subcollection)

    print(f"Exporting: {path}")

    data = export_collection(collection_ref)

    if not args.output:
        args.output = f"{path}.json"
    out_path = Path(args.output)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Export complete → {out_path}")


if __name__ == "__main__":
    main()