from abc import abstractmethod

from xync_schema.models import Agent

from xync_client.Abc.Agent import BaseAgentClient


class BaseInAgentClient:
    def __init__(self, agent: Agent):
        self.agent_client: BaseAgentClient = agent.client()

    @abstractmethod
    async def start_listen(self) -> bool: ...

    # 3N: [T] - Уведомление об одобрении запроса на сделку
    @abstractmethod
    async def request_accepted_notify(self) -> int: ...  # id
