import json
from langchain_community.chat_models import ChatOllama  # Replace with the actual import path

def load_llm(model_key, config_path='config.json'):
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        model_config = config['models'][model_key]
        print(f"Loading model: {model_config['name']} from {model_config['service_url']}")
        return ChatOllama(
            model=model_config['name'],
            service_url=model_config['service_url']
        )
        
    except KeyError:
        raise ValueError(f"Model key '{model_key}' not found in config.")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize LLM '{model_key}': {e}")
