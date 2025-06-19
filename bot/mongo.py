from pymongo import AsyncMongoClient
from config import settings


client = AsyncMongoClient(
    host=settings.mongo_url,
    uuidRepresentation="standard",
)
