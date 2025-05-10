# ai_service Directory

This directory contains agents responsible for various AI-driven tasks within the application, including text explanation, summarization, and persona management.

## Purpose

The ai_service directory is designed to provide a collection of agents that can be used to perform various AI-driven tasks, making it easier to integrate AI capabilities into different parts of the application.

## Structure

- `agents/`: Agents for AI responses to user queries
- `tool/`: Tools for agents
    - `persona_tool.py`: `persona_tool_fn(query)`, `make_persona_tool(persona_name)`, `combine_tools()`
- `intelligence/`: Specific AI tasks
    - `alfo.py`: `alfo_handle_chunked_article_decision(article_id)`, `summarize_task(chunk_id, chunk_text, summary_updates)`, `explain_words_task(chunk_id, chunk_text, word_list, word_updates)`, `persona_task(article_id, chunk_id, persona_list, persona_updates)`
    - `summarizer.py`: `summarizer_handle_summary(chunk)`
    - `word_explainer.py`: `word_explainer_handle_word_sentences(chunk_id, chunk, word_list)`, `fetch_contextual_explanation(word, sentence)`
    - `persona.py`: `persona_handle_user_question(role, context, query)`, `persina_chain_detect_role(query, persona_list)`
- `memory/`: Memory management for agents
    - `persona_vector.py`: `get_retriever(raw_inputs)`, `get_relevant_docs_by_role(role, query)`, `build_vector_store_from_text_sources(raw_inputs)`
- `chain/`: Chain configurations for processing tasks
- `llm_loader/`: Language model loading utilities
    - `llm_ollama.py`: `load_llm(model_key, config_path=None)`
- `prompts/`: Prompt templates for agents
- `config/`: Configuration files for agents

## Redis Usage

This module uses [Redis](https://redis.io/) as an in-memory data store for tracking job progress during AI-driven tasks such as article upload and processing. Redis must be running and accessible (default: `localhost:6379`).

- Progress tracking functions are available in `services.utiles.upload_process_track` and are used by async agents (e.g., `alfo.py`).

## Main APIs

- AI agent orchestration and tool APIs for persona, summarization, and word explanation.
- All major async functions and tools listed above are intended for use by other modules and routes.

## Usage

Agents are modular and can be integrated into different parts of the application. Refer to individual agent documentation for specific usage instructions.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for suggestions and improvements.

## Contact

For questions or support, contact the project maintainer.
