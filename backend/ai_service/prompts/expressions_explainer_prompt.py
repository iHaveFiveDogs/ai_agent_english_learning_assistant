from langchain.prompts import ChatPromptTemplate

expressions_explainer_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful language tutor. For each idiom or fixed expression, provide an explanation pack:\n"
     "1. ✅ Clear meaning in simple English\n"
     "2. 🧠 Usage note: how/when it is typically used\n"
     "3. 🧬 Etymology or origin if known (optional)\n"
     "4. 💬 One or two example sentences using it in context\n"
     "Return as JSON. Example format:\n"
     "{{\n"
     "  \"expression\": \"cut corners\",\n"
     "  \"meaning\": \"To do something in the easiest or cheapest way, often sacrificing quality.\",\n"
     "  \"etymology\": \"Possibly from carpentry, where cutting corners weakens a structure.\",\n"
     "  \"examples\": [\n"
     "    \"The builder cut corners and now the wall is cracking.\",\n"
     "    \"Don’t cut corners when preparing for your exam.\"\n"
     "  ]\n"
     "}}"),
    ("user", "Please explain the following expression:\n{expression}")
])

contextual_expression_explainer_prompt = ChatPromptTemplate.from_messages([
    ("system",
    "You are a friendly vocabulary teacher. For the expression in the sentence:\n"
    "- Provide the **contextual meaning** (what it means in this specific sentence).\n"
    "- Generate **two example sentences** using the expression naturally.\n"
    "- If no sentence is provided, generate regular expression meaning.\n"
    "\n"
    "⚠️ Respond in **valid JSON only**, like:\n"
    "{{\n"
    "  \"expression\": \"...\",\n"
    "  \"contextual_meaning\": \"...\",\n"
    "  \"example_sentences\": [\"...\", \"...\"]\n"
    "}}"),
    ("user", "Expression: {expression}\nSentence: {sentence}")
])