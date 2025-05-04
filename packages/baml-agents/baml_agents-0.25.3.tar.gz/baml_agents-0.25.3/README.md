# baml‑agents

[![Status: Experimental](https://img.shields.io/badge/status-experimental-gold.svg?style=flat)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#experimental)
[![Maintained: yes](https://img.shields.io/badge/yes-43cd0f.svg?style=flat&label=maintained)](https://github.com/Elijas/baml-agents/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-43cd0f.svg?style=flat&label=license)](LICENSE)
[![PyPI Version](https://img.shields.io/badge/v0.25.3-version?color=43cd0f&style=flat&label=pypi)](https://pypi.org/project/baml-agents)
[![PyPI Downloads](https://img.shields.io/pypi/dm/baml-agents?color=43cd0f&style=flat&label=downloads)](https://pypistats.org/packages/baml-agents)
[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Building Agents with LLM structured generation ([BAML](https://www.boundaryml.com/)), [MCP Tools](https://modelcontextprotocol.io/docs/concepts/tools), and [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) principles**

This repository shares useful patterns I use when working with BAML. Note: The API may unexpectedly change with future minor versions; therefore, install with specific version constraints:

```bash
pip install "baml-agents>=0.25.3,<0.26.0"
```

Found this useful? Star the repo on GitHub to show support and follow for updates. Also, find me on Discord if you have questions or would like to join a discussion!

![GitHub Repo stars](https://img.shields.io/github/stars/elijas/baml-agents?style=flat&color=f0f0f0&labelColor=white&logo=github&logoColor=black)
&nbsp;<a href="https://discord.gg/hCppPqm6"><img alt="Discord server invite" src="https://img.shields.io/discord/1119368998161752075?logo=discord&logoColor=white&style=flat&color=f0f0f0&labelColor=7289da" height="20"></a>

## Disclaimer

This project is maintained independently by Elijas and is not affiliated with the official BAML project.

## Repository Structure

*   `/notebooks`: **Core Tutorials & Examples.** Contains curated Jupyter notebooks demonstrating key features and recommended patterns. Start here to learn `baml-agents`.
*   `/explorations`: **Experimental & Niche Content.** Holds prototypes, tests, and examples for specific or advanced use cases. Content may be less polished or stable. See the [explorations README](./explorations/README.md).
*   `/baml_agents/devtools`: **Developer Utilities.** Contains helper scripts for project maintenance, development workflows, and automating tasks (e.g., updating baml generator versions). See the [devtools README](./baml_agents/devtools/README.md).

## Contents (Core Tutorials)

The primary tutorials are located in the `/notebooks` directory:

1.  [Flexible LLM Client Management in BAML](notebooks/01_baml_llm_client_config.ipynb)
    - Effortlessly switch between different LLM providers (like OpenAI, Anthropic, Google) at runtime using simple helper functions.
    - Bridge compatibility gaps: Connect to unsupported LLM backends or tracing systems (e.g., Langfuse, LangSmith) via standard proxy setups.
    - Solve common configuration issues: Learn alternatives for managing API keys and client settings if environment variables aren't suitable.
2.  [Introduction to AI Tool Use with BAML](notebooks/02_baml_custom_tools.ipynb)
    - Learn how to define custom actions (tools) for your AI using Pydantic models, making your agents capable of _doing_ things.
    - See how to integrate these tools with BAML manually or dynamically using `ActionRunner` for flexible structured outputs.
    - Understand how BAML translates goals into structured LLM calls that select and utilize the appropriate tool.
3.  [Integrating Standardized MCP Tools with BAML](notebooks/03_baml_with_mcp_tools.ipynb)
    - Discover how to leverage the Model Context Protocol (MCP) to easily plug-and-play pre-built 3rd party tools (like calculators, web search) into your BAML agents.
    - See `ActionRunner` in action, automatically discovering and integrating tools from MCP servers with minimal configuration.
    - Learn techniques to filter and select specific MCP tools to offer to the LLM, controlling the agent's capabilities precisely.
4.  [Interactive BAML Development in Jupyter](notebooks/04_interactive_baml_jupyter.ipynb)
    - See BAML's structured data generation stream _live_ into your Jupyter output cell as the LLM generates it.
    - Interactively inspect the details: Use collapsible sections to view full LLM prompts and responses, optionally grouped by call or session, directly in the notebook.
    - Chat with your agent: Interactive chat widget right in the notebook, allowing you to chat with your agent in real-time.
5.  [Simple Agent Demonstration](notebooks/05_simple_agent_demo.ipynb)
    - Putting it all together: Build a simple, functional agent capable of tackling a multi-step task.
    - Learn how to combine custom Python actions (defined as `Action` classes) with standardized MCP tools (like calculators or time servers) managed by `ActionRunner`.
    - Follow the agent's decision-making loop driven by BAML's structured output generation (`GetNextAction`), see it execute tools, and observe how it uses the results to progress.
    - Includes demonstration of `JupyterBamlMonitor` for transparent inspection of the underlying LLM interactions.

## Simple example

> [!TIP]
> The code below is trimmed for brevity to **illustrate the core concepts**. Some function names or setup steps may differ slightly from the full notebook implementation for clarity in this example. The full, runnable code is available in the notebook <a href="notebooks/05_simple_agent_demo.ipynb">Simple Agent Demonstration (notebooks/05_simple_agent_demo.ipynb)</a>

<details>
  <summary>Show code for the example below</summary>

```python
def get_weather_info(city: str):
    return f"The weather in {city} is 63 degrees fahrenheit with cloudy conditions."

def stop_execution(final_answer: str):
    return f"Final answer: {final_answer}"

r = ActionRunner() # Doing an action means using a tool

# Adding a tool to allow the agent to do math
r.add_from_mcp_server(server="uvx mcp-server-calculator")

# Adding a tool to get the current time
r.add_from_mcp_server(server="uvx mcp-timeserver")  # Note: you can also add URLs

# Adding a tool to get the current weather
r.add_action(get_weather_info)

# Adding a tool to let the agent stop execution
r.add_action(stop_execution)

async def execute_task(llm, task: str) -> str:
    interactions = []
    while True:
        action = await llm.GetNextAction(task, interactions)
        if result := is_result_available(action):
            return result

        result = r.run(action)
        interactions.append(new_interaction(action, result))

llm = LLMClient("gpt-4.1-nano")
task = r.execute_task(llm, "State the current date along with avg temp between LA, NY, and Chicago in Fahrenheit.")
```

</details>

<br>

![BAML Agent execution trace in Jupyter showing LLM prompts and completions](https://github.com/user-attachments/assets/ea55c3e7-147d-41aa-99ce-40e4783f7818)

To try it yourself, check out the notebook [Simple Agent Demonstration (notebooks/05_simple_agent_demo.ipynb)](notebooks/05_simple_agent_demo.ipynb).

## Running the Notebooks

To run code from the `notebooks/` folder, you'll first need to:

- Install the [`uv` python package manager](https://docs.astral.sh/uv/).
- Install all dependencies: `uv sync --dev`
- Generate necessary BAML code: `uv run baml-cli generate`
  - Alternatively, you can use the [VSCode extension](https://marketplace.visualstudio.com/items?itemName=Boundary.baml-extension) to do it automatically every time you edit a `.baml` file.
