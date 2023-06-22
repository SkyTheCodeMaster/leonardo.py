from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  import aiohttp
  from typing import Union,Any
  import io
  from os import PathLike

class Image:
  url: str
  nsfw: bool
  id: str
  like_count: int
  _session: aiohttp.ClientSession

  def __init__(
      self,
      *,
      url: str,
      nsfw: bool,
      id: str,
      like_count: int,
      _session: aiohttp.ClientSession
  ) -> None:
    self.url = url
    self.nsfw = nsfw
    self.id = id
    self.like_count = like_count
    self._session = _session

  async def read(self) -> bytes:
    "return the file bytes"
    async with self._session.get(self.url) as resp:
      data = await resp.read()
      return data
  
  async def save(self, fp: Union[io.BytesIO,PathLike[Any]]) -> int:
    "Save into a file-like object"
    data = await self.read()
    if isinstance(fp, io.BufferedIOBase):
      return fp.write(data)
    else:
      with open(fp, "wb") as f:
        return f.write(data)