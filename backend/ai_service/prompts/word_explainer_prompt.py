from langchain.prompts import ChatPromptTemplate



word_cached_prompt = ChatPromptTemplate.from_messages([
    ("system",
    "You are a vocabulary etymologist and phonologist. For each English word:\n"
    "- Provide only the **IPA pronunciation** in **American English**, enclosed in slashes (e.g., /ˈleɪzi/). Use valid IPA symbols only.\n"
    "- Provide the **etymology** (word origin), including original languages and root words. Use Unicode characters where needed (e.g., Latin *licere*).\n"
    "\n"
    "⚠️ Respond with **valid JSON only**:\n"
    "{{\n"
    "  \"word\": \"...\",\n"
    "  \"ipa\": \"/.../\",\n"
    "  \"etymology\": \"...\"\n"
    "}}"),
    ("user", "Word: {word}")
])

batch_ipa_prompt = ChatPromptTemplate.from_messages([
    ("system",
        "You are a dictionary expert. For each word in the list:\n"
        "- Return IPA pronunciation (in American English, using slashes: /.../)\n"
        "- Return word etymology (origin, root, language)\n"
        "- Provide a **friendly etymology explanation** (easy-to-understand explanation, like explaining to a child)\n"
        "\n"
        "⚠️ Output must be a valid JSON **array** only — no extra text. Example format:\n"
        "[\n"
        "  {{\"word\": \"example\", \"ipa\": \"/ɪɡˈzæmpəl/\", \"etymology\": \"From Latin exemplum\"}},\n"
        "  {{\"word\": \"another\", \"ipa\": \"/əˈnʌðər/\", \"etymology\": \"Old English on oþer\"}}\n"
        "]"
    ),
    ("user", "Words: {words}")
])


contextual_explainer_prompt = ChatPromptTemplate.from_messages([
    ("system",
    "You are a friendly vocabulary teacher. For the word in the sentence:\n"
    "- Provide a **friendly explanation** (easy-to-understand definition, like explaining to a child).\n"
    "- Provide the **contextual meaning** (what it means in this specific sentence).\n"
    "- Generate **two example sentences** using the word naturally.\n"
    "- If no sentence is provided, generate regular word meaning.\n"
    "\n"
    "⚠️ Respond in **valid JSON only**, like:\n"
    "{{\n"
    "  \"word\": \"...\",\n"
    "  \"explanation\": \"...\",\n"
    "  \"contextual_meaning\": \"...\",\n"
    "  \"example_sentences\": [\"...\", \"...\"]\n"
    "}}"),
    ("user", "Word: {word}\nSentence: {sentence}")
])