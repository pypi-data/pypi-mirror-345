from beanie import Document
from bson.objectid import ObjectId
from pydantic import Field
from uuid import uuid4
from datetime import datetime,UTC
class BaseDocument(Document):
    """
    Base document class for all documents of NoSQL database
    """
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    uuid: str = Field(default_factory=lambda: str(uuid4()), unique=True, index=True,nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"
        
class BaseDraftDocument(BaseDocument):
    is_draft: bool = Field(default=False)

        