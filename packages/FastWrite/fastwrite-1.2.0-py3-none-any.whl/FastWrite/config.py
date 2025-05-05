import os
from pathlib import Path
from dotenv import load_dotenv

# Define path to the .env file (saved in the module's root folder)
ENV_PATH = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=ENV_PATH)

def get_api_key(key_name: str) -> str:
    """
    Returns the API key from the environment. If the key is not found,
    prompts the user for input and saves it to the .env file.

    :param key_name: The name of the API key environment variable.
    :return: The API key as a string.
    """
    key = os.getenv(key_name)
    if not key:
        key = input(f"Enter {key_name}: ").strip()
        # Append key to the .env file
        with open(ENV_PATH, "a") as env_file:
            env_file.write(f"\n{key_name}={key}\n")
    return key

def get_groq_api_key() -> str:
    """
    Returns the Groq API key.
    """
    return get_api_key("GROQ_API_KEY")

def get_gemini_api_key() -> str:
    """
    Returns the Gemini API key.
    """
    return get_api_key("GEMINI_API_KEY")

def get_openai_api_key() -> str:
    """
    Returns the OpenAI API key.
    """
    return get_api_key("OPENAI_API_KEY")

def get_openrouter_api_key() -> str:
    """
    Returns the OpenRouter API key.
    """
    return get_api_key("OPENROUTER_API_KEY")