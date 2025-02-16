import os
from groq import Groq

class LlmSwitcher:
  def __init__(self, client_name = None, model_name = None):
    self.client_name = client_name
    self.model_name = model_name

  def get_client_info(self):
    match self.client_name:
      case 'openai':
        return { 
                  'client': '',
                  'model': ''
              }
      case _:
        return { 
                'client': Groq(api_key=os.environ.get('GROQ_API_KEY')),
                'model': self.model_name or 'llama-3.3-70b-versatile'
              }