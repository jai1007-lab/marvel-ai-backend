from pydantic import BaseModel
from typing import Optional, List, Any
from enum import Enum
from app.services.tool_registry import BaseTool


class User(BaseModel):
    id: str
    fullName: str
    email: str
    
class Role(str, Enum):
    human = "human"
    ai = "ai"
    system = "system"

class MessageType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    file = "file"

class MessagePayload(BaseModel):
    text: str

class Message(BaseModel):
    role: Role
    type: MessageType
    timestamp: Optional[Any] = None
    payload: MessagePayload
    
class RequestType(str, Enum):
    chat = "chat"
    tool = "tool"

class GenericRequest(BaseModel):
    user: User
    type: RequestType
    
class ChatRequest(GenericRequest):
    messages: List[Message]
    
class ToolRequest(GenericRequest):
    tool_data: BaseTool
    
class ChatResponse(BaseModel):
    data: List[Message]

class ToolResponse(BaseModel):
    data: Any
    
class ChatMessage(BaseModel):
    role: str
    type: str
    text: str

class InputData(BaseModel):
    grade: str
    subject: str
    Syllabus_type: Optional[str] = 'exam_based'
    instructions : Optional[str] = 'None'

class AIRAGRequest(BaseModel):
    grade: str
    assignment: str
    description: Optional[str] = 'None'

class RUBRICRequest(BaseModel):
    grade: str
    points:str
    standard:str
    assignment: str

class NotesRequest(BaseModel):
    file_url: Optional[str] = None
    orientation: Optional[str] = "portrait"
    columns: Optional[int] = 1