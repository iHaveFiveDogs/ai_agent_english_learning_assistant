import json
from langchain_community.chat_models import ChatOllama
import os

def load_llm(model_key, config_path=None):
    try:
        if config_path is None:
            current_dir = os.path.dirname(__file__)
            config_path = os.path.join(current_dir,'..', 'config', 'config.json')

        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        model_config = config['models'][model_key]

        return ChatOllama(
            model=model_config['name'],
            service_url=model_config['service_url']
        )
    
    except KeyError:
        raise ValueError(f"Model key '{model_key}' not found in config.")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize LLM '{model_key}': {e}")
