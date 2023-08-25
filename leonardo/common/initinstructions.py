class InitUploadInstructions:
  id: str
  fields: dict[str,str]
  key: str
  url: str

  def __init__(self, *,
      id: str,
      fields: dict[str,str],
      key: str,
      url: str
    ) -> None:
    self.id = id
    self.fields = fields
    self.key = key
    self.url = url