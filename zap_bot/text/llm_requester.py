from app import connection
from tools.get_products import get_products
from tools.save_order import save_order
import json

AVAILABLE_ARGUMENTS = {
  "get_products": get_products,
  "save_order": save_order
}

class LlmRequester:
  def __init__(self, client_info, wa_id, messages, stream = False, max_tokens = 200):
    self.client_info = client_info
    self.wa_id = wa_id
    self.messages = messages
    self.stream = stream
    self.max_tokens = max_tokens

  def request(self, first_request = True):
    params = self.first_request_params() if first_request else self.second_request_params()
    return self.client_info['client'].chat.completions.create(**params)

  def send(self):
    if len(self.messages) == 2:
      self.persist_message_to_db(self.messages[0]['role'], self.messages[0]['content'])
    
    self.persist_message_to_db(self.messages[-1]['role'], self.messages[-1]['content'])

    first_response = self.request()

    print(first_response)

    response_message = first_response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
      tool_calls_list = []
      for tool_calls_item in tool_calls:
        tool_calls_list.append(
          {
            "id": tool_calls_item.id,
            "type": tool_calls_item.type,
            "function": {
                "name": tool_calls_item.function.name,
                "arguments": tool_calls_item.function.arguments
            }
          }
        )

      self.messages.append({ 'role': response_message.role, 'tool_calls': tool_calls_list })

      self.persist_message_to_db(response_message.role, tool_calls = json.dumps(tool_calls_list))

      for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = AVAILABLE_ARGUMENTS[function_name]
        function_args = json.loads(tool_call.function.arguments)

        function_response = json.dumps(function_to_call(**function_args))

        self.messages.append(
            {
                "tool_call_id": tool_call.id, 
                "role": "tool",
                "name": function_name,
                "content": function_response
            }
        )

        self.persist_message_to_db("tool", json.dumps(function_response), tool_call_id = tool_call.id, name = function_name)

      second_response = self.request(first_request = False)

      print(second_response)

      final_response = second_response.choices[0].message

    else:
      final_response = first_response.choices[0].message

    self.messages.append({ 'role': final_response.role, 'content': final_response.content })
    self.persist_message_to_db(final_response.role, final_response.content)

    return final_response

  def first_request_params(self):
    return {
      'messages': self.messages,
      'model': self.client_info['model'],
      'tools': self.tools(),
      'stream': self.stream,
      'max_tokens': self.max_tokens,
      "tool_choice": "auto"
    }

  def second_request_params(self):
    return {
      'model': self.client_info['model'],
      'messages': self.messages
    }

  def persist_message_to_db(self, role, content = None, tool_calls = None, tool_call_id = None, name = None):
    sql = "INSERT INTO messages(wa_id, role, content, tool_calls, tool_call_id, name) VALUES (?, ?, ?, ?, ?, ?)"

    cursor = connection.cursor()

    cursor.execute(sql, (self.wa_id, role, content, tool_calls, tool_call_id, name))

    connection.commit()
    cursor.close()

  def tools(self):
    # Search for a product by it name if the parameter product_name is passed or get all products if the parameter product_name is not passed
    # If the parameter product_name is passed, search for a product by it name. Else get all products
    return [
      {
        "type": "function",
        "function": {
          "name": "get_products",
          "description": "If the product name is passed, search for a product by it name. Else get all products",
          "parameters": {
            "type": "object",
            "properties": {
              "product_name": {
                "type": "string",
                "description": "The product name",
              }
            }
          }
        }
      },
      {
        "type": "function",
        "function": {
          "name": "save_order",
          "description": "Save order informations",
          "parameters": {
            "type": "object",
            "properties": {
              "customer_name": {
                "type": "string",
                "description": "The customer name",
              },
              "customer_phone": {
                "type": "string",
                "description": "The customer phone",
              },
              "customer_address": {
                "type": "string",
                "description": "The customer address",
              },
              "items": {
                "type": "array",
                "description": "A list with the items of the customer order",
                "items": {
                  "type": "object",
                  "properties": {
                    "product_id": {
                      "type": "integer",
                      "description": "The product id of the customer's order item",
                    },
                    "product_name": {
                      "type": "string",
                      "description": "The product name of the customer's order item",
                    },
                    "product_price": {
                      "type": "string",
                      "description": "The product price of the customer's order item",
                    },
                    "quantity": {
                      "type": "number",
                      "description": "The quantity of the product of the customer's order item",
                    }
                  }
                }
              },
              "total_price": {
                "type": "string",
                "description": "The order total price",
              }
            },
            "required": ["customer_name", "customer_phone", "customer_address", "items", "total_price"]
          }
        }
      }
    ]