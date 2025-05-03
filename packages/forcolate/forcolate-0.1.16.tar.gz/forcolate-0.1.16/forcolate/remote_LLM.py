import requests
import json

# These functions are not injected directly in the default set of tools because they use remote servers with specific API keys
# and are not open source. They are provided as examples of how to use the tools.



def get_LLM_response(query, folder_in="", folder_out=""):

  # get the url, model and key from a config file

  config_file = "config.json"
  with open(config_file, 'r') as f:
    config = json.load(f)
    url = config["LLMurl"]
    model = config["LLMmodel"]
    key = config["LLMkey"]

  # example of the config file
  # {
  #   "LLMurl": "https://openrouter.ai/api/v1/chat/completions",
  #   "LLMmodel": "qwen/qwen3-4b:free",
  #   "LLMkey": "your_api_key"
  # }

  # check if the url, model and key are not empty       
    if not url or not model or not key:
        raise ValueError("Please provide a valid url, model and key in the config file")


  # read all files in the folder_in directory
  prompt_and_query = "Answer the question based on the context below : \n QUESTION: " + query + "\n"

  context = "Below is the context from the files in the folder:\n CONTEXT: " 
  if folder_in:
    import os
    for filename in os.listdir(folder_in):
      if filename.endswith(".txt") or filename.endswith(".md"):
        with open(os.path.join(folder_in, filename), 'r') as f:
          context += f.read() + "\n"
 
  # Combine the context and query
  context_and_query = prompt_and_query + context
 
  response = requests.post(
    url=url,
    headers={
      "Authorization": "Bearer " + key,
    },
    data=json.dumps({
      "model": model,
      "messages": [
        {
          "role": "user",
          "content": context_and_query
        }
      ]
    })
  )

  response_json = response.json()['choices'][0]['message']['content']

  # Save the response to a file
  if folder_out:
    with open(f"{folder_out}/answer.md", "w") as f:
      f.write(response_json)

  return response_json


LLM_TOOLS = [(
    "Ask LLM",
    "Ask LLM : this tool will ask the LLM to answer the question based on the context provided in the folder directory",
    get_LLM_response
)]
