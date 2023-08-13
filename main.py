import streamlit as st
import random
import string
import os
import requests
from requests.structures import CaseInsensitiveDict


def get_response_fine_tuned(prompt):

  end_prompt = " ->"
  stop_sequence = "##STOP##"
  carriage_return = "\n"

  api_key = os.getenv('OPENAI_API_KEY')

  headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
  }

  data = {
    'model': 'davinci:ft-personal:product-design-220723-2023-07-22-16-56-20',
    'prompt': prompt,
    'temperature': 1,
    'max_tokens': 256,
    'top_p': 1,
    'frequency_penalty': 0,
    'presence_penalty': 0,
    'stop': [stop_sequence, end_prompt, carriage_return]
  }

  response = requests.post('https://api.openai.com/v1/completions',
                           json=data,
                           headers=headers)

  if response.status_code == 200:
    response_data = response.json()
    return response_data['choices'][0]['text']
  else:
    print(f"Error: {response.status_code} - {response.text}")


def get_response_da_vinci(prompt):
  api_key = os.getenv('OPENAI_API_KEY')

  headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
  }

  data = {
    'model': 'text-davinci-003',
    'prompt': prompt,
    'temperature': 1,
    'max_tokens': 256,
    'top_p': 1,
    'frequency_penalty': 0,
    'presence_penalty': 0,
    #'stop': [stop_sequence, end_prompt]
  }

  response = requests.post('https://api.openai.com/v1/completions',
                           json=data,
                           headers=headers)

  if response.status_code == 200:
    response_data = response.json()
    return response_data['choices'][0]['text']
  else:
    print(f"Error: {response.status_code} - {response.text}")


def get_response_gpt(prompt):
  api_key = os.getenv('OPENAI_API_KEY')

  headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
  }

  data = {'model': 'gpt-3.5-turbo', 'temperature': 1.0, 'messages': prompt}

  response = requests.post('https://api.openai.com/v1/chat/completions',
                           json=data,
                           headers=headers)

  if response.status_code == 200:
    response_data = response.json()
    return response_data['choices'][0]['message']['content']
  else:
    print(f"Error: {response.status_code} - {response.text}")


def get_response_dalle(prompt):
  api_key = os.getenv('OPENAI_API_KEY')

  headers = CaseInsensitiveDict()
  headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
  }

  data = {
    "model": "image-alpha-001",
    "prompt": prompt,
    "num_images": 1,
    "size": "256x256",
    "response_format": "url",
  }
  resp = requests.post('https://api.openai.com/v1/images/generations',
                       json=data,
                       headers=headers)

  if resp.status_code != 200:
    raise ValueError("Failed to generate image " + resp.text)

  response_text = resp.json()
  return response_text['data'][0]['url']


def generate_random_text(length=10):
  """Generate random text of the specified length."""
  characters = string.ascii_letters + string.digits + string.punctuation + " "
  return ''.join(random.choice(characters) for _ in range(length))


def main():
  st.title("Chat with Model")
  st.write("***WELCOME TO CHAT***")

  end_prompt = " ->"

  if "prompt" not in st.session_state:
    st.session_state.prompt = ""

  if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
  chat_history = st.session_state.chat_history

  if "messages" not in st.session_state:
    st.session_state.messages = [{
      "role":
      "system",
      "content":
      "You are a personal learning assistant called Model that speaks English"
    }]

  radio_choices = ["davinci", "gpt", "dalle", "fine_tuned"]
  add_gpt_prefix = st.radio("Select Model:", radio_choices, index=1)

  add_cls_prefix = st.checkbox("Clear history")

  with st.form("user_input_form", clear_on_submit=True):

    user_input = st.text_area("You:", value="")
    retrieve_response_button = st.form_submit_button("Retrieve Response")

  if retrieve_response_button:

    chat_history = st.session_state.chat_history
    prompt = st.session_state.prompt
    messages = st.session_state.messages

    if add_gpt_prefix == "davinci":
      user_input = "#DV# " + user_input
    elif add_gpt_prefix == "gpt":
      user_input = "#GPT# " + user_input
    elif add_gpt_prefix == "dalle":
      user_input = "#DALLE# " + user_input
    if add_cls_prefix:
      user_input = "#CLS# " + user_input

    #print(user_input)

    if user_input.startswith("#CLS#"):
      user_input = user_input.replace("#CLS#", "").strip()
      prompt = ""
      chat_history = []
      messages = [{
        "role":
        "system",
        "content":
        "You are a personal learning assistant called Model that speaks English"
      }]
    if user_input.startswith("#DV#"):
      user_input = user_input.replace("#DV#", "").strip()
      my_input = prompt + user_input + "\n"
      new_message = get_response_da_vinci(prompt=my_input)
      chat_history.append(("You", user_input))
      chat_history.append(("Model", new_message))
      messages.append({"content": user_input, "role": "user"})
      messages.append({"content": new_message, "role": "system"})
      prompt = prompt + "\n\n" + user_input + "\n\n" + new_message + "\n\n"
    elif user_input.startswith("#GPT#"):
      user_input = user_input.replace("#GPT#", "").strip()
      print(messages)
      new_message = get_response_gpt(prompt=messages)
      chat_history.append(("You", user_input))
      chat_history.append(("Model", new_message))
      messages.append({"content": user_input, "role": "user"})
      messages.append({"content": new_message, "role": "system"})
    elif user_input.startswith("#DALLE#"):
      user_input = user_input.replace("#DALLE#", "").strip()
      new_message = get_response_dalle(prompt=user_input)
      chat_history.append(("You", user_input))
      chat_history.append(
        ("Model", f"<img src='{new_message}' width='300' />"))
    else:
      my_input = prompt + user_input + end_prompt
      new_message = get_response_fine_tuned(prompt=my_input)
      chat_history.append(("You", user_input))
      chat_history.append(("Model", new_message))
      messages.append({"content": user_input, "role": "user"})
      messages.append({"content": new_message, "role": "system"})
      prompt = prompt + "\n" + user_input + "\n" + new_message + "\n"
      print(prompt)

  st.session_state.chat_history = chat_history

  with st.expander("Chat History", expanded=True):
    chat_history_styled = [
      f"<div class='chat-box' style='background-color: {'#f9f9f9' if role=='You' else '#e5e5e5'};'>"
      f"<strong>{role}:</strong> {message}</div>"
      for role, message in chat_history
    ]
    chat_history_html = "".join(chat_history_styled)
    chat_history_html = chat_history_html.replace('\n', '<br>')
    st.markdown(f"""
          <style>
          .chat-box {{
              border: 1px solid #ccc;
              background-color: #f9f9f9;
              padding: 10px;
              border-radius: 5px;
          }}
          </style>
          <div style="max-height: 300px; overflow-y: auto;">
          {chat_history_html}
          </div>
          """,
                unsafe_allow_html=True)

if __name__ == "__main__":
  main()
