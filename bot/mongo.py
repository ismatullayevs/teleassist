from config import settings
from pymongo import AsyncMongoClient

client = AsyncMongoClient(
    host=settings.mongo_url,
    uuidRepresentation="standard",
)
