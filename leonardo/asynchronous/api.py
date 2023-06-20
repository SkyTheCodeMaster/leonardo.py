from __future__ import annotations

import aiohttp

from model import AsyncModel
from common.userinfo import UserInformation
from .. import API_BASE

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from typing import Union

class LeonardoAsync:
  token: str
  _session: aiohttp.ClientSession
  user_information: UserInformation
  def __init__(self, token: str) -> None:
    self.token = token
    self.session = aiohttp.ClientSession()

  async def setup(self) -> None:
    self.user_information = await self.me()

  async def close(self) -> None:
    await self.session.close()

  async def me(self) -> UserInformation:
    url = f"{API_BASE}/me"
    async with self._session.get(url) as resp:
      data: dict[str,Union[str,int]] = await resp.json()
      return UserInformation(
        id=data["id"],
        username=data["username"],
        token_renewal_date=data["tokenRenewalDate"],
        subscription_tokens=data["subscriptionTokens"],
        subscription_gpt_tokens=data["subscriptionGptTokens"],
        subscription_model_tokens=data["subscriptionModelTokens"],
        api_credit=data["apiCredit"]
      )

  async def models(self) -> list[AsyncModel]:
    pass