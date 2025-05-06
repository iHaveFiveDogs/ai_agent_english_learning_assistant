from ai_service.tool.persona_tool import combine_tools
from langchain.agents import AgentType, initialize_agent

#STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
# Step 3: Initialize agent with the tool
async def initialize_persona_agent(llm):
    print("Initializing persona agent...")
    agent = initialize_agent(
        tools=combine_tools(),
        llm=llm,
        agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )
    return agent