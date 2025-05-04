# Services Directory

This directory contains service modules that provide core, reusable functionalities to the application. Services are designed to be stateless and accessible from different components.

## Purpose

The services directory centralizes business logic and operations, supporting features such as word explanation, summarization, and persona management.

## Structure

- `word_explainer_service.py`: Services for word explanation and processing
    - APIs: `make_word_explanation_update(chunk_id, words)`, `store_combined_word_explanation_to_mongodb(article_id)`, `store_word_explanation_to_mongodb(chunk_id, word_list)`, `if_there_are_word_explain(chunk_id)`, `extract_word_sentences(chunk, word_list)`, `load_word_list(path)`, `fetch_word_from_cached_db(word)`, `save_words_to_cached_db(word, ipa, etymology)`
- `summerizer_service.py`: Text summarization services
    - APIs: `combine_summaries(article_id)`, `store_combined_summaries_to_mongodb(article_id, summary)`, `store_chunked_summaries_to_mongodb(chunk_id, chunk_summary)`, `make_summary_update(chunk_id, summary)`, `if_there_are_summary_summarized(chunk_id)`
- `persona_service.py`: Persona management operations
    - APIs: `make_persona_update(chunk_id, persona_list)`, `store_combined_persona_to_mongodb(article_id)`, `upsert_persona_entries(article_id, chunk_id, persona_list)`, `gather_single_persona_docs(persona_name)`, `gather_all_persona_docs()`, `fetch_all_persona_names()`, `merge_persona_documents(persona_name, collection)`, `merge_all_personas()`, `if_there_are_persona(chunk_id)`

## Main APIs

All major async functions and helpers listed above are intended for use by other modules and AI agents.

## Usage

Services are designed to be stateless and can be called from any part of the application. Refer to the service interface for correct usage patterns.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for suggestions and improvements.

## Contact

For questions or support, contact the project maintainer.
