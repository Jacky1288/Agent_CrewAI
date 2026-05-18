import os
from dotenv import load_dotenv, find_dotenv

# these expect to find a .env file at the directory above the lesson.                                                                                                                     # the format for that file is (without the comment)                                                                                                                                       #API_KEYNAME=AStringThatIsTheLongAPIKeyFromSomeService
def load_env():
    load_dotenv(find_dotenv())
    
    # Support for multi-provider proxy (DeepSeek, OpenRouter, etc.)
    api_base = os.getenv("OPENAI_API_BASE")
    if api_base:
        os.environ["OPENAI_API_BASE"] = api_base
        # Also set OPENAI_BASE_URL — used by the openai SDK (>=1.x) and CrewAI's own OpenAI provider
        os.environ["OPENAI_BASE_URL"] = api_base
        print(f"Using Custom API Base: {api_base}")

    model_name = os.getenv("OPENAI_MODEL_NAME")
    if model_name:
        os.environ["OPENAI_MODEL_NAME"] = model_name
        print(f"Using Model: {model_name}")

def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key

def get_exa_api_key():
    load_env()
    exa_api_key = os.getenv("EXA_API_KEY")
    return exa_api_key