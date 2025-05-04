# AgentAmi

AgentAmi is a flexible agentic framework built using [LangGraph](https://python.langchain.com/docs/langgraph/), designed
to scale with large numbers of tools and intelligently select the most relevant ones for a given user query. 
It helps with decreasing token size **significantly**.

It supports:

- Dynamic tool selection via inbuilt runtime RAG (very efficient) with an option to **easily** replace it with your own tool_selector.
- Pruner to limit context length and improve performance (it's inbuilt, you don't have to do anything).

---

## Quick start
> ***Refer the [main.py](https://github.com/Ami-sh/agentami/blob/main/main.py) file for a complete sample usage.***

```zsh
pip install agentami
from agentami import AgentAmi
```

```python
from langchain.chat_models import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from agentami.agents.ami import AgentAmi

# Replace ... (ellipsis) with the commented instructions

tools = [...]  # List of LangChain-compatible tools
agent = AgentAmi(
    model=ChatOpenAI(model="gpt-4o"),
    tools=tools,  # List of LangChain-compatible tools
    checkpointer=InMemorySaver(),  # Optional. No persistence if omitted.

    # Optional parameters:
    tool_selector=...,  # Custom function to select relevant tools. Defaults to internal tool_selector.
    top_k=...,  # Number of top tools to use. Defaults to 3.
    context_size=...,  # Number of past user prompts to retain. Defaults to 7.
    disable_pruner=...,  # If True, disables pruning & will increase token usage. Defaults to False
    prompt_template=...  # Custom prompt template. Defaults to a generic bot template.
)
agent_ami = agent.graph # Your regular langgraph's graph.
```
---
## Things you should be aware about: 

 - Running for the first time **will** take time as it installs the dependencies (models used by internal tool_selector).
 - Your first `agent_ami.invoke() or agent_agent_ami.astream()` may take time if you have hundreds of tools, because it initialises a vector store and embeds the tool descriptions at runtime for each AgentAmi() object
 - Your eventual prompts' response time would be fine.
 - Checkout ROADMAP.md file for future features.

---
## How to integrate your own tool selector?

Just make a function that accepts `(query: str, top_k: int)` and parameters and returns `List[str] #List of tool names`.

```python
from typing import List


# function template:
def my_own_tool_selector(query: str, top_k: int) -> List[str]:
    # Your logic to select tools based on the query
    return ["tool1", "tool2", "tool3"]  # Return top_k selected tool names
```
---

<div align="center">
  <img src="AgentAmi.jpg" alt="AgentAmi" width="300"/>
</div>
