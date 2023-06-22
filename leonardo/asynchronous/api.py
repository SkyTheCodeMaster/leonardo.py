from __future__ import annotations

import aiohttp

from .model import AsyncModel
from ..common.userinfo import UserInformation
from ..const import API_BASE
from .generation import Generation
from .image import Image
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from typing import Union

class LeonardoAsync:
  token: str
  _session: aiohttp.ClientSession
  _model_cache: dict[str,AsyncModel]
  user_information: UserInformation
  def __init__(self, token: str) -> None:
    self.token = token
    self._model_cache = {}
    self._session = aiohttp.ClientSession(
      headers = {
        "accept": "application/json",
        "authorization": f"Bearer {self.token}"
      }
    )

  async def setup(self) -> None:
    self.user_information = await self.me()

  async def close(self) -> None:
    await self.session.close()

  async def me(self) -> UserInformation:
    url = f"{API_BASE}/me"
    async with self._session.get(url) as resp:
      data: dict[str,Union[str,int]] = (await resp.json())["user_details"][0]
      return UserInformation(
        id=data["user"]["id"],
        username=data["user"]["username"],
        token_renewal_date=data["tokenRenewalDate"],
        subscription_tokens=data["subscriptionTokens"],
        subscription_gpt_tokens=data["subscriptionGptTokens"],
        subscription_model_tokens=data["subscriptionModelTokens"],
        api_credit=data["apiCredit"]
      )

  async def models(self) -> list[AsyncModel]:
    raise NotImplementedError("Yikes")
  
  async def get_model_by_id(self, id: str) -> AsyncModel:
    if id in self._model_cache:
      return self._model_cache[id]
    url = f"{API_BASE}/models/{id}"
    async with self._session.get(url) as resp:
      data = (await resp.json())["custom_models_by_pk"]
      model = AsyncModel(
        id,
        _session = self._session,
        name = data["name"],
        description = data["description"],
        model_height = data["modelHeight"],
        model_width = data["modelWidth"],
        status = data["status"],
        type = data["type"],
        updated_at=datetime.fromisoformat(data["updatedAt"]),
        created_at=datetime.fromisoformat(data["createdAt"]),
        sd_version=data["sdVersion"],
        public=data["public"],
        instance_prompt=data["instancePrompt"]
      )
      self._model_cache[id] = model
      return model
    
  async def get_generation(self,generation_id: str) -> Generation:
    url = f"{API_BASE}/generations/{generation_id}"
    async with self._session.get(url) as resp:
      data = (await resp.json())["generations_by_pk"]
      images: list[Image] = []
      for image in data["generated_images"]:
        i = Image(
          id=image["id"],
          url=image["url"],
          nsfw=image.get("nsfw",False),
          like_count=image.get("like_count",0),
          _session = self._session
        )
        images.append(i)
      gen = Generation(
        images=images,
        model_id=data["modelId"],
        model = self._model_cache.get(data["modelId"],None),
        prompt=data.get("prompt",None),
        negative_prompt=data.get("negative_prompt",None),
        image_height=data.get("imageHeight",None),
        image_width=data.get("imageWidth",None),
        inference_steps=data.get("inferenceSteps",None),
        seed=data.get("seed",None),
        public=data.get("public",None),
        scheduler=data.get("scheduler",None),
        sd_version=data.get("sdVersion",None),
        status=data.get("status",None),
        preset_style=data.get("presetStyle",None),
        init_strength=data.get("initStrength",None),
        guidance_scale=data.get("guidanceScale",None),
        id=data.get("id",None),
        created_at=datetime.fromisoformat(data.get("createdAt",None))
      )
      return gen
    
  async def get_generations(self, user_id: str = None, *, offset: int = 0, limit: int = 10) -> list[Generation]:
    if user_id == None: # type: ignore
      if not self.user_information:
        await self.setup()
      user_id = self.user_information.id
    url = f"{API_BASE}/generations/user/{user_id}?offset={offset}&limit={limit}"
    async with self._session.get(url) as resp:
      gens: list[Generation] = []
      top_data = await (resp.json())["generations"]
      for data in top_data:
        images: list[Image] = []
        for image in data["generated_images"]:
          i = Image(
            id=image["id"],
            url=image["url"],
            nsfw=image.get("nsfw",False),
            like_count=image.get("like_count",0),
            _session = self._session
          )
          images.append(i)
        gen = Generation(
          images=images,
          model_id=data["modelId"],
          model = self._model_cache.get(data["modelId"],None),
          prompt=data.get("prompt",None),
          negative_prompt=data.get("negative_prompt",None),
          image_height=data.get("imageHeight",None),
          image_width=data.get("imageWidth",None),
          inference_steps=data.get("inferenceSteps",None),
          seed=data.get("seed",None),
          public=data.get("public",None),
          scheduler=data.get("scheduler",None),
          sd_version=data.get("sdVersion",None),
          status=data.get("status",None),
          preset_style=data.get("presetStyle",None),
          init_strength=data.get("initStrength",None),
          guidance_scale=data.get("guidanceScale",None),
          id=data.get("id",None),
          created_at=datetime.fromisoformat(data.get("createdAt",None))
        )
        gens.append(gen)
    return gens
  
  async def delete_generation(self, gen_id: str) -> bool:
    url = f"{API_BASE}/generations/{gen_id}"
    async with self._session.delete(url) as resp:
      return resp.status == 200
    
  