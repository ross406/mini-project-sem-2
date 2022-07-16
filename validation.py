import validators

def validatePostInput(data):
  errors = {}
  if validators.length(data["text"], min=10, max=300):
    errors["text"] = 'Post most be between 10 and 300 characters'
  
  # if validators.truthy(data["text"]):
  #   errors["text"] = 'Text Field is Required'
  
  return errors