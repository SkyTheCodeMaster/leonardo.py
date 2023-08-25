from __future__ import annotations

import json
from io import BytesIO
from datetime import datetime
from typing import TYPE_CHECKING

import aiohttp

from ..common.initinstructions import InitUploadInstructions
from ..common.userinfo import UserInformation
from ..const import API_BASE
from ..errors import *
from .generation import Generation
from .image import Image, InitImage
from .model import AsyncModel

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
      if resp.status != 200:
        return RequestError(f"Request returned HTTP{resp.status} {await resp.text()}")
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
    raise NotImplementedError("Coming Soon")
  
  async def get_model_by_id(self, id: str) -> AsyncModel:
    if id in self._model_cache:
      return self._model_cache[id]
    url = f"{API_BASE}/models/{id}"
    async with self._session.get(url) as resp:
      if resp.status != 200:
        return RequestError(f"Request returned HTTP{resp.status} {await resp.text()}")
      data = (await resp.json())["custom_models_by_pk"]
      model = AsyncModel(
        id,
        _session = self._session,
        _api = self,
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
      if resp.status != 200:
        return RequestError(f"Request returned HTTP{resp.status} {await resp.text()}")
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
        complete = bool(images), # If gen isnt complete, the api returns empty images, which leads to this being true/false
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
      if resp.status != 200:
        return RequestError(f"Request returned HTTP{resp.status} {await resp.text()}")
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
    
  async def get_init_image(self, image_id: str):
    url = f"{API_BASE}/init-image/{image_id}"
    async with self._session.get(url) as resp:
      if resp.status != 200:
        return RequestError(f"Request returned HTTP{resp.status} {await resp.text()}")
      data = (await resp.json())["init_images_by_pk"]
      return InitImage(
        created_at=data["createdAt"],
        id=data["id"],
        url=data["url"]
      )
    
  async def _upload_init_image(self, extension: str) -> InitUploadInstructions:
    url = f"{API_BASE}/init-image"

    if extension not in [
      "png", "jpg", "jpeg", "webp"
    ]: raise InvalidInitImageFormat(f"got: {extension}; expected: png, jpg, jpeg, webp")

    async with self._session.post(url, data={"extension": extension}) as resp:
      if resp.status != 200:
        raise RequestError(f"Request returned HTTP{resp.status} {await resp.text()}")
      data = (await resp.json())["uploadInitImage"]
      return InitUploadInstructions(
        id = data["id"],
        fields=json.loads(data["fields"]),
        key=data["key"],
        url=data["url"],
      )
    
  async def upload_init_image(self, *,
      filename: str = None,
      bytes: BytesIO = None,
      filetype: str = None,) -> InitImage:
    """
    File name and bytes are mutually exclusive.
    If file name is passed, do not pass bytes, and vice versa.
    If bytes is passed, filetype is required.
    If filetype is passed, it overrides the file name detection.
    """

    if filename and bytes:
      raise ValueError("File name and bytes both passed")
    if bytes and filetype is None:
      raise ValueError("Bytes passed, filetype not passed")
    if filename is None and bytes is None:
      raise ValueError("Bytes or file name not passed")
    if (filetype is None) and (filename is not None):
      filetype = filename.split(".")[-1]

    if filename:
      with open(filename, "rb") as f:
        bytes = BytesIO(f.read())
    instructions = await self._upload_init_image(filetype)
    print(instructions.fields)
    data = {**instructions.fields, "file": bytes}

    async with self._session.post(instructions.url, data=data, headers = {"authorization":instructions.key}) as resp:
      return await resp.text()