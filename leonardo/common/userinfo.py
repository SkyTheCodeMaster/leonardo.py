from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from datetime import datetime

class UserInformation:
  id: str
  username: str
  token_renewal_date: datetime
  subscription_tokens: int
  subscription_gpt_tokens: int
  subscription_model_tokens: int
  api_credit: int

  def __init__(
    self,
    *,
    id: str = None,
    username: str = None,
    token_renewal_date: datetime = None,
    subscription_tokens: int = None,
    subscription_gpt_tokens: int = None,
    subscription_model_tokens: int = None,
    api_credit: int = None
  ) -> None:
    self.id = id
    self.username = username
    self.token_renewal_date = token_renewal_date
    self.subscription_tokens = subscription_tokens
    self.subscription_gpt_tokens = subscription_gpt_tokens
    self.subscription_model_tokens = subscription_model_tokens
    self.api_credit = api_credit