from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from app.database import get_kolb_collection
from app.schemas import KolbProfileCreate, KolbProfileInDB, KolbProfileUpdate


async def ensure_indexes() -> None:
    collection = get_kolb_collection()
    await collection.create_index([( "alumno_id", ASCENDING)], unique=True)


def _serialize_profile(document: dict) -> KolbProfileInDB:
    document["id"] = str(document.pop("_id"))
    return KolbProfileInDB(**document)


async def create_profile(profile: KolbProfileCreate) -> KolbProfileInDB:
    collection = get_kolb_collection()
    now = datetime.now(timezone.utc)
    payload = profile.model_dump()
    payload["created_at"] = now
    payload["updated_at"] = now

    try:
        result = await collection.insert_one(payload)
    except DuplicateKeyError as exc:
        raise ValueError("Ya existe un perfil para ese alumno_id") from exc

    saved = await collection.find_one({"_id": result.inserted_id})
    return _serialize_profile(saved)


async def list_profiles() -> list[KolbProfileInDB]:
    collection = get_kolb_collection()
    cursor = collection.find().sort("created_at", -1)
    docs = await cursor.to_list(length=None)
    return [_serialize_profile(doc) for doc in docs]


async def get_profile_by_id(profile_id: str) -> KolbProfileInDB | None:
    if not ObjectId.is_valid(profile_id):
        return None
    collection = get_kolb_collection()
    doc = await collection.find_one({"_id": ObjectId(profile_id)})
    if not doc:
        return None
    return _serialize_profile(doc)


async def get_profile_by_alumno_id(alumno_id: str) -> KolbProfileInDB | None:
    collection = get_kolb_collection()
    doc = await collection.find_one({"alumno_id": alumno_id})
    if not doc:
        return None
    return _serialize_profile(doc)


async def update_profile(profile_id: str, data: KolbProfileUpdate) -> KolbProfileInDB | None:
    if not ObjectId.is_valid(profile_id):
        return None

    payload = data.model_dump(exclude_none=True)
    if not payload:
        return await get_profile_by_id(profile_id)

    payload["updated_at"] = datetime.now(timezone.utc)
    collection = get_kolb_collection()
    result = await collection.update_one({"_id": ObjectId(profile_id)}, {"$set": payload})

    if result.matched_count == 0:
        return None

    doc = await collection.find_one({"_id": ObjectId(profile_id)})
    return _serialize_profile(doc)


async def delete_profile(profile_id: str) -> bool:
    if not ObjectId.is_valid(profile_id):
        return False

    collection = get_kolb_collection()
    result = await collection.delete_one({"_id": ObjectId(profile_id)})
    return result.deleted_count == 1
