from langchain_community.chat_models import ChatOllama


# # def load_llm(model_key, config_path=None):
#     try:
#         if config_path is None:
#             current_dir = os.path.dirname(__file__)
# #             config_path = os.path.join(current_dir,'..', 'config', 'config.json')

#         with open(config_path, 'r') as config_file:
#             config = json.load(config_file)

#         model_config = config['models'][model_key]

#         return ChatOllama(
#             model=model_config['name'],
#             service_url=model_config['service_url']
#         )
    
#     except KeyError:
#         raise ValueError(f"Model key '{model_key}' not found in config.")
#     except Exception as e:
#         raise RuntimeError(f"Failed to initialize LLM '{model_key}': {e}")

MODEL_POOL = {
    "word_explainer": ChatOllama(model="mistral:latest", base_url="http://localhost:11434"),
    "summarizer": ChatOllama(model="gemma3:4b", base_url="http://localhost:11434"),
    "alfo": ChatOllama(model="gemma3:4b", base_url="http://localhost:11434"),
    "persona": ChatOllama(model="samantha-mistral:latest", base_url="http://localhost:11434"),
    "context_explainer": ChatOllama(model="mistral:latest", base_url="http://localhost:11434"),
    "sentence_explainer": ChatOllama(model="gemma3:4b", base_url="http://localhost:11434"),
    "expressions_explainer": ChatOllama(model="gemma3:4b", base_url="http://localhost:11434"),
}   


def load_llm(task_type: str):
    model_entry = MODEL_POOL.get(task_type)
    if isinstance(model_entry, list):
        # If future you want to load-balance between 2 GPUs
        return model_entry[0]
    return model_entry
