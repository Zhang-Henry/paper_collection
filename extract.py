class Extractor:
  def __init__(self, fields, subfields, include_subfield=False):
    self.fields = fields
    self.subfields = subfields
    self.include_subfield = include_subfield
  
  def __call__(self, paper):
    return self.extract(paper)

  def extract(self, paper):
    trimmed_paper = {}
    for field in self.fields:
      trimmed_paper[field] = getattr(paper, field, None)
    for subfield, fields in self.subfields.items():
      if self.include_subfield:
        trimmed_paper[subfield] = {}
      subfield_data = getattr(paper, subfield, {})
      for field in fields:
        if isinstance(subfield_data, dict) and field in subfield_data:
          field_value = subfield_data[field]
        else:
          field_value = None  # 如果字段不存在，设为None

        if self.include_subfield:
          trimmed_paper[subfield][field] = field_value
        else:
          trimmed_paper[field] = field_value
    return trimmed_paper