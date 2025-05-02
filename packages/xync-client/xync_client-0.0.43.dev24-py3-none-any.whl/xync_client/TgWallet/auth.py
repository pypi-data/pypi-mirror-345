from x_client.http import Client as HttpClient
from xync_schema.models import Actor, User, Person

from xync_client.Abc.AuthTrait import BaseAuthTrait
from xync_client.Abc.Base import BaseClient
from xync_client.TgWallet.pyro import PyroClient


class AuthClient(BaseAuthTrait, BaseClient):
    async def _get_auth_hdrs(self) -> dict[str, str]:
        if not self.actor:
            self.actor = (
                await Actor.filter(ex=self.ex, agent__isnull=False).prefetch_related("person__user", "agent").first()
            )
        elif not isinstance(self.actor.person, Person) or not isinstance(self.actor.person.user, User):
            await self.actor.fetch_related("person__user")
        pyro = PyroClient(self.actor)
        init_data = await pyro.get_init_data()
        tokens = HttpClient("walletbot.me")._post("/api/v1/users/auth/", init_data)
        self.actor.exid = tokens["user_id"]
        await self.actor.save()
        pref = "" if self.__class__.__name__ == "AssetClient" else "Bearer "
        return {"Wallet-Authorization": tokens["jwt"], "Authorization": pref + tokens["value"]}
