from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    content: str


@dataclass
class AgentLogEvent:
    agent_description: str
    sender_topic: str
    receiver_topic: str
    system_message: str
    user_prompt: str
    response: str
    model: str
    timestamp: datetime = datetime.now()
