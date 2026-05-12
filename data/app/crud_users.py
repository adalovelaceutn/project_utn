from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from app.database import get_users_collection
from app.schemas import UserCreate, UserPublic, UserUpdate
from app.security import hash_password, verify_password


def _serialize_user(document: dict) -> UserPublic:
    document["id"] = str(document.pop("_id"))
    document.pop("password_hash", None)
    return UserPublic(**document)


async def ensure_user_indexes() -> None:
    users = get_users_collection()
    await users.create_index([("username", ASCENDING)], unique=True)
    await users.create_index([("dni", ASCENDING)], unique=True)
    await users.create_index([("email", ASCENDING)], unique=True)


async def create_user(payload: UserCreate) -> UserPublic:
    users = get_users_collection()
    now = datetime.now(timezone.utc)
    user_doc = payload.model_dump(exclude={"password"})
    user_doc["password_hash"] = hash_password(payload.password)
    user_doc["created_at"] = now
    user_doc["updated_at"] = now

    try:
        result = await users.insert_one(user_doc)
    except DuplicateKeyError as exc:
        raise ValueError("username, dni o email ya existe") from exc

    created = await users.find_one({"_id": result.inserted_id})
    return _serialize_user(created)


async def list_users() -> list[UserPublic]:
    users = get_users_collection()
    docs = await users.find().sort("created_at", -1).to_list(length=None)
    return [_serialize_user(doc) for doc in docs]


async def get_user_by_id(user_id: str) -> UserPublic | None:
    if not ObjectId.is_valid(user_id):
        return None
    users = get_users_collection()
    doc = await users.find_one({"_id": ObjectId(user_id)})
    if doc is None:
        return None
    return _serialize_user(doc)


async def get_user_by_username(username: str) -> UserPublic | None:
    users = get_users_collection()
    doc = await users.find_one({"username": username})
    if doc is None:
        return None
    return _serialize_user(doc)


async def authenticate_user(username: str, password: str) -> UserPublic | None:
    users = get_users_collection()
    doc = await users.find_one({"username": username})
    if doc is None:
        return None
    if not verify_password(password, doc["password_hash"]):
        return None
    return _serialize_user(doc)


async def update_user(user_id: str, payload: UserUpdate) -> UserPublic | None:
    if not ObjectId.is_valid(user_id):
        return None

    updates = payload.model_dump(exclude_none=True, exclude={"password"})
    if payload.password:
        updates["password_hash"] = hash_password(payload.password)

    if not updates:
        return await get_user_by_id(user_id)

    updates["updated_at"] = datetime.now(timezone.utc)

    users = get_users_collection()
    try:
        result = await users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    except DuplicateKeyError as exc:
        raise ValueError("dni o email ya existe") from exc

    if result.matched_count == 0:
        return None

    updated = await users.find_one({"_id": ObjectId(user_id)})
    return _serialize_user(updated)


async def delete_user(user_id: str) -> bool:
    if not ObjectId.is_valid(user_id):
        return False
    users = get_users_collection()
    result = await users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count == 1
