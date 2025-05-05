from letschatty.models.chat.chat import Chat
from letschatty.models.chat.client import Client
from letschatty.models.company.empresa import EmpresaModel
from datetime import datetime
from zoneinfo import ZoneInfo

class ChatFactory:
    @staticmethod
    def from_json(chat_json: dict) -> Chat:
        return Chat(**chat_json)

    @staticmethod
    def from_client(client: Client, empresa: EmpresaModel, channel_id: str) -> Chat:
        return Chat(
            client=client,
            channel_id=channel_id,
            company_id=empresa.id,
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC"))
        )