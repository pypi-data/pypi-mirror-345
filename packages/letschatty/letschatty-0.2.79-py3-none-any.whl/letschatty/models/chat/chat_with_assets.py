
from .chat import Chat
from letschatty.models.chat.flow_link_state import FullState
from letschatty.models.company.assets.chat_assets import AssignedAssetToChat
from letschatty.models.company.assets import Product, Tag, Sale, ContactPoint

from letschatty.models.utils.types.serializer_type import SerializerType
from pydantic import BaseModel
from typing import List, Dict
import json

class ChatWithAssets(BaseModel):
    chat: Chat
    products: List[Product]
    tags: List[Tag]
    sales: List[Sale]
    contact_points: List[ContactPoint]
    flows_links_states: List[FullState]
