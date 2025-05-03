from typing import Dict, Any, Optional

from .api import AlationAPI
from .tools import AlationContextTool


class AlationAIAgentSDK:
    def __init__(self, base_url: str, user_id: int, refresh_token: str):
        self.api = AlationAPI(base_url, user_id, refresh_token)
        self.context_tool = AlationContextTool(self.api)

    def get_context(self, question: str, signature: Optional[Dict[str, Any]] = None):
        return self.context_tool.run(question, signature)

    def get_tools(self):
        return [self.context_tool]
