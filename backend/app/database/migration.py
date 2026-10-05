import asyncio
import os
import sys

# Add backend directory to sys path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.mongodb import get_database, connect_to_mongo, close_mongo_connection
from app.services.models.model_router import normalize_scan_type
import pymongo

async def run_migration():
    print("Connecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()

    print("--- 1. Creating Indexes ---")
    
    # Fix null IDs before indexing
    try:
        import uuid
        collections_and_fields = [
            (db.patients, "patientId", "PAT-MIG-"),
            (db.scans, "scanId", "SCAN-MIG-"),
            (db.reports, "reportId", "REP-MIG-"),
            (db.predictions, "predictionId", "PRED-MIG-"),
            (db.notifications, "notificationId", "NOTIF-MIG-"),
            (db.emergency_cases, "emergencyCaseId", "EMERG-MIG-")
        ]
        
        for coll, field, prefix in collections_and_fields:
            docs = await coll.find({field: None}).to_list(length=None)
            for doc in docs:
                new_id = f"{prefix}{uuid.uuid4().hex[:8].upper()}"
                await coll.update_one({"_id": doc["_id"]}, {"$set": {field: new_id}})
            if docs:
                print(f"Fixed {len(docs)} null {field}s in {coll.name}.")
    except Exception as e:
        print(f"Error fixing null IDs: {e}")

    # Unique Indexes
    index_fields = [
        (db.patients, "patientId"),
        (db.scans, "scanId"),
        (db.reports, "reportId"),
        (db.predictions, "predictionId"),
        (db.notifications, "notificationId"),
        (db.emergency_cases, "emergencyCaseId")
    ]
    
    for coll, field in index_fields:
        try:
            await coll.create_index(field, unique=True)
            print(f"Created unique index for {field} in {coll.name}.")
        except Exception as e:
            print(f"Error creating unique index for {field} in {coll.name}: {e}")

    # Standard Indexes
    try:
        await db.scans.create_index("patientId")
        await db.reports.create_index("patientId")
        await db.emergency_cases.create_index("patientId")
        print("Standard indexes created.")
    except Exception as e:
        print(f"Error creating standard indexes: {e}")

    print("--- 2. Normalizing Existing Data ---")

    collections_to_normalize = [
        db.scans,
        db.reports,
        db.predictions,
        db.emergency_cases
    ]

    for collection in collections_to_normalize:
        docs = await collection.find({}).to_list(length=None)
        updated_count = 0
        for doc in docs:
            if "scanType" in doc and doc["scanType"]:
                old_val = doc["scanType"]
                new_val = normalize_scan_type(old_val)
                if old_val != new_val:
                    await collection.update_one({"_id": doc["_id"]}, {"$set": {"scanType": new_val}})
                    updated_count += 1
        print(f"Normalized {updated_count} records in {collection.name}.")

    print("--- 3. Fixing Missing Fields in Users ---")
    # Ensure users have basic preferences structure
    users = await db.users.find({}).to_list(length=None)
    for user in users:
        updates = {}
        if "twoFactorEnabled" not in user:
            updates["twoFactorEnabled"] = False
            updates["twoFactorSecret"] = None
        if "preferences" not in user:
            updates["preferences"] = {
                "dashboard": {
                    "showRecentScans": True,
                    "showScanDistribution": True,
                    "showEmergencySummary": True,
                    "showPendingReviews": True
                },
                "dateFormat": "DD/MM/YYYY",
                "notifications": {
                    "systemNotifications": True,
                    "emergencyAlerts": True,
                    "reportAlerts": True,
                    "pendingReviewAlerts": True
                }
            }
        
        if updates:
            await db.users.update_one({"_id": user["_id"]}, {"$set": updates})
            print(f"Updated preferences/2FA baseline for user: {user.get('email')}")

    print("Migration completed successfully.")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(run_migration())
