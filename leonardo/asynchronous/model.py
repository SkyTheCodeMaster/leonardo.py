from __future__ import annotations

from ..const import API_BASE
from ..errors import RequestError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  import aiohttp
  from datetime import datetime

class AsyncModel:
  _session: aiohttp.ClientSession

  id: str
  name: str
  description: str
  model_height: int
  model_width: int
  status: str
  type: str
  updated_at: datetime
  created_at: datetime
  sd_version: str
  public: bool
  instance_prompt: str
  
  def __init__(
    self, id: str, *, 
    _session: aiohttp.ClientSession,
    name: str = None,
    description: str = None,
    model_width: int = None,
    model_height: int = None,
    status: str = None,
    type: str = None,
    updated_at: datetime = None,
    created_at: datetime = None,
    sd_version: str = None, # stable diffusion version?
    public: bool = None,
    instance_prompt: str = None
  ) -> None:
    self.id = id
    self._session = _session
    self.name = name
    self.description = description
    self.model_height = model_height
    self.model_width = model_width
    self.status = status
    self.type = type
    self.updated_at = updated_at
    self.created_at = created_at
    self.sd_version = sd_version
    self.public = public
    self.instance_prompt = instance_prompt

  async def generate(self,*,
    prompt: str,
    negative_prompt: str = None,
    sd_version: str = None,
    num_images: int = 1,
    width: int = None,
    height: int = None,
    num_inference_steps: int = 45,
    guidance_scale: int = 7,
    init_generation_image_id: str = None,
    init_image_id: str = None,
    init_strength: float = None,
    scheduler: str = "EULER_DISCRETE",
    preset_style: str = "LEONARDO",
    tiling: bool = False,
    public: bool = False,
    prompt_magic: bool = False,
    control_net: bool = False,
    control_net_type: str = None,
    return_generation: bool = False
  ) -> str:
    "take in a bunch of parameters, return generation id"

    # correct inputs
    if width:
      width -= width % 8
      width = max(32,min(1024,width))
    else:
      width = self.model_width
    if height:
      height -= height % 8
      height = max(32,min(1024,height))
    else:
      height = self.model_height
    
    guidance_scale = max(1,min(20,guidance_scale))
    num_inference_steps = max(30,min(60,num_inference_steps))
    if init_strength:
      init_strength = max(0.1,min(0.9,init_strength))
    if (width >= 768 or height >= 768):
      num_images = max(1,min(4,num_images))
    else:
      num_images = max(1,min(8,num_images))

    # correct string inputs
    scheduler = scheduler.upper()
    if scheduler not in [
      "KLMS",
      "EULER_ANCESTRAL_DISCRETE",
      "EULER_DISCRETE",
      "DDIM",
      "DPM_SOLVER",
      "PNDM",
    ]:
      scheduler = "EULER_DISCRETE"
    preset_style = preset_style.upper()
    if preset_style not in [
      "LEONARDO",
      "NONE"
    ]:
      preset_style = "LEONARDO"

    url = f"{API_BASE}/generations"
    params = {
      "prompt": prompt,
      "negative_prompt": negative_prompt,
      "modelId": self.id,
      "sd_version": sd_version,
      "num_images": num_images,
      "width": width,
      "height": height,
      "num_inference_steps": num_inference_steps,
      "guidance_scale": guidance_scale,
      "init_generation_image_id": init_generation_image_id,
      "init_image_id": init_image_id,
      "init_strength": init_strength,
      "scheduler": scheduler,
      "presetStyle": preset_style,
      "tiling": tiling,
      "public": public,
      "promptMagic": prompt_magic,
      "controlNet": control_net,
      "controlNetType": control_net_type
    }
    # Clear out the None things
    filtered = {k: v for k,v in params.items() if v is not None} # type: ignore
    params.clear()
    params.update(filtered)

    async with self._session.post(url, json=params) as resp:
      if resp.status == 200:
        return (await resp.json())["sdGenerationJob"]["generationId"]
      else:
        raise RequestError(f"attempted generation: {resp.status} {await resp.text()}")