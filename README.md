# Dynamic Workflows Walkthrough

**Agents that write their own orchestration code.**

As models improve, they can now *write the orchestration loop themselves*. This repo walks through an example using the [OpenHands SDK](https://docs.openhands.dev/sdk).

> **About this implementation:** This is the OpenHands SDK's implementation of dynamic workflows,
> inspired by [Claude Code's Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code).
> We don't know exactly how Anthropic implements it — this is our interpretation using open source tools.
> See the [original PR](https://github.com/OpenHands/software-agent-sdk/pull/3426).

---

## The Problem

Building multi-agent systems today means **manually orchestrating sub-agents**. You write the loops, manage state, and coordinate everything.

[See the Old Way →](old-way.html)

---

## The Solution

What if the model wrote its own orchestration? With workflows, you **give the model a task and the tools**. The model decides how to structure the workflow.

```python
# Without Workflows: 25+ lines
market_agent = Agent(llm, "Research market...")
tech_agent = Agent(llm, "Research tech...")
# ... you manage everything

# With Workflows: 2 lines
conversation.send_message("Research X from multiple angles")
conversation.run()
# Agent writes: async def main(wf): ... map_agents() ... reduce_agent()
```

[See the New Way →](new-way.html) | [Side-by-Side Comparison →](comparison.html)

---

## Deep Research Example

Anthropic used deep research as their example. Here's **our version** using OpenHands workflows.

[See the Deep Research Demo →](deep_research/comparison.html)

### The Key Parts

**1. Skills** — Tell the model **when and how to use workflows**.

```python
ORCHESTRATOR_SKILL = {
    "name": "orchestrator",
    "content": """
When asked to research deeply:
1. Identify 4-6 distinct research angles
2. Use wf.map_agents() to fan out research in parallel
3. Use wf.reduce_agent() to synthesize findings
"""
}
```

**2. Sub-Agents** — **Pre-defined roles** the model can use.

```python
register_agent_if_absent("web_searcher", create_web_searcher, "Searches the web")
register_agent_if_absent("fact_checker", create_fact_checker, "Cross-checks claims")
register_agent_if_absent("synthesizer", create_synthesizer, "Creates reports")
```

**3. The Model Decides** — Based on the skill + question, the model picks angles and calls sub-agents.

```python
# This is what the model writes (you don't write this)
async def main(wf):
    angles = ['Market overview', 'Technical capabilities', 'Expert opinions', ...]
    market_data = await wf.map_agents(angles, 'web_searcher')
    verified = await wf.map_agents(market_data, 'fact_checker')
    return await wf.reduce_agent(verified, 'synthesizer')
```

**The model handles: which angles to research, which sub-agents to use when, parallel vs sequential execution, how to aggregate results.**

---

## Quick Start

```bash
# Add your API key
echo "OPENAI_API_KEY=sk-..." > .env

# Run the workflow version (agent writes the orchestration)
python deep_research/deep_research_workflow.py "What is the AI coding assistant market size?"

# Run the manual version (you write the orchestration)
python deep_research/deep_research_manual.py "What is the AI coding assistant market size?"
```

---

## Resources

- [OpenHands SDK](https://github.com/OpenHands/software-agent-sdk) — Our implementation
- [PR #3426: Dynamic Workflow Tool](https://github.com/OpenHands/software-agent-sdk/pull/3426) — The code
- [Claude Code: Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code) — Their blog post
- [LangChain: Deep Research](https://docs.langchain.com/oss/python/deepagents/deep-research) — Example of manual orchestration

