from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from image import Image
  from model import AsyncModel
  from datetime import datetime

class Generation:
  images: list[Image]
  model_id: str
  model: AsyncModel
  prompt: str
  negative_prompt: str
  image_height: str
  image_width: str
  inference_steps: int
  seed: int
  public: bool
  scheduler: str
  sd_version: str
  status: str
  preset_style: str
  init_strength: int
  guidance_scale: int
  id: str
  created_at: datetime

  def __init__(
      self,
      *,
      images: list[Image],
      model_id: str,
      model: AsyncModel,
      prompt: str,
      negative_prompt: str,
      image_height: str,
      image_width: str,
      inference_steps: int,
      seed: int,
      public: bool,
      scheduler: str,
      sd_version: str,
      status: str,
      preset_style: str,
      init_strength: int,
      guidance_scale: int,
      id: str,
      created_at: datetime,
  ) -> None:
    self.images = images
    self.model_id = model_id
    self.model = model
    self.prompt = prompt
    self.negative_prompt = negative_prompt
    self.image_height = image_height
    self.image_width  = image_width
    self.inference_steps = inference_steps
    self.seed = seed
    self.public = public
    self.scheduler = scheduler
    self.sd_version = sd_version
    self.status = status
    self.preset_style = preset_style
    self.init_strength = init_strength
    self.guidance_scale = guidance_scale
    self.id = id
    self.created_at = created_at