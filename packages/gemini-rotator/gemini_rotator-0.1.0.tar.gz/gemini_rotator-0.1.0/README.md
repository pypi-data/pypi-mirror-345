# Gemini API Key Rotator for LlamaIndex

This utility monkey-patches `google.auth.api_key.Credentials` to rotate multiple Google API keys, useful with LlamaIndex to manage Gemini API request limits.

## How to Use

1.  **Install the package**: run this in command prompt `pip install gemini-rotator`.
2.  **Import and Patch**: Before initializing your Gemini LLM, call the `patch` function with your API keys. The script modifies the Google authentication library at runtime. When `patch` is called:
    *   It extends the `Credentials` class to cycle through your provided API keys.

### `patch(api_keys, api_main=None)`

*   `api_keys`: A list of your Google API key strings.
*   `api_main`: (Optional, but **Recommended**) An API key from `api_keys`. Rotation only occurs if the default key passed to LlamaIndex or generativeai.configure() matches `api_main`. This prevents interference with other Google services using different keys. If `None`, keys rotate on every use (use with caution as it might affect other Google clients).

### `restore()`

Call `restore()` to revert the monkey-patching and return the `google.auth.api_key.Credentials` class to its original state.

## Example with LlamaIndex

```python
# Assuming the rotator script is saved as gemini_key_rotator.py
from gemini_key_rotator import patch
from llama_index.llms.gemini import Gemini
from llama_index.core.base.llms.types import ChatMessage

# --- Configuration ---
MY_GEMINI_API_KEYS = [
    "YOUR_API_KEY_1", # Replace
    "YOUR_API_KEY_2", # Replace
    "YOUR_API_KEY_3", # Replace
]

MAIN_API_KEY = MY_GEMINI_API_KEYS[0] 
# Monkey patch
patch(MY_GEMINI_API_KEYS, MAIN_API_KEY)

llm = Gemini(model="gemini-2.0-flash", api_key=MAIN_API_KEY) # Initialize LlamaIndex with the main key

messages = [ChatMessage(content="Hello Gemini", role="user")] # Example messages
response = llm.chat(messages=messages) # Send message to Gemini

print(response.message.content) # Print the response

```

The patch will take care of rotating the API keys for you. The `Gemini` class will use the main key for initialization, and the rotation will happen automatically when making requests.

## Important Notes

*   **`api_main`**: Using `api_main` is strongly advised to ensure rotation only affects the intended Gemini client.
*   **Get API Keys**: Obtain your API keys from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials) under "Credentials". You should have [Gemini API](https://console.cloud.google.com/marketplace/product/google/generativelanguage.googleapis.com) enabled in your project and its limited to one api key per project. You can create multiple projects to get more keys.
*   **Risks**: Abusing the api may lead to account suspension. Use responsibly and ensure compliance with Google's API usage policies.
*   **Use Cases**: This is not for production use. It's a temporary solution for testing that requires slightly more thant gemini rate limits to effectively test and benchmark.

## Disclaimer

Use at your own risk. Comply with Google's API terms.