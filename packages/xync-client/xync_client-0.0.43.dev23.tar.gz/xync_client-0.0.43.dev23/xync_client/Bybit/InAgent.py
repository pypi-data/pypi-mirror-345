from asyncio import run

from x_model import init_db
from xync_schema import models

from xync_client.Abc.InAgent import BaseInAgentClient
from xync_client.Bybit.agent import AgentClient
from xync_client.Bybit.ws import prv
from xync_client.TgWallet.pyro import PyroClient
from xync_client.loader import PG_DSN, bot


class InAgentClient(BaseInAgentClient):
    agent_client: AgentClient

    async def start_listen(self):
        t = await self.agent_client.ott()
        ts = int(float(t["time_now"]) * 1000)
        await prv(self.agent_client.agent.auth["deviceId"], t["result"], ts, listen)

    # 3N: [T] - Уведомление об одобрении запроса на сделку
    async def request_accepted_notify(self) -> int: ...  # id


def listen(data: dict):
    print(data)


async def main():
    _ = await init_db(PG_DSN, models, True)
    pbot = PyroClient(bot)
    await pbot.app.start()
    await pbot.app.create_channel("tc")
    await pbot.app.stop()

    agent = await models.Agent.filter(actor__ex_id=9, auth__isnull=False).prefetch_related("actor__ex").first()
    cl: InAgentClient = agent.in_client()
    await cl.agent_client.close()


if __name__ == "__main__":
    run(main())
