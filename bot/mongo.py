from pymongo import AsyncMongoClient
from core.config import settings


client = AsyncMongoClient(
    host=settings.mongo_url,
    uuidRepresentation="standard",
)