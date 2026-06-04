# Dynamic Workflows Walkthrough

**Agents that write their own orchestration code.**

As models improve, they can now *write the orchestration loop themselves*. This repo walks through examples using the [OpenHands SDK](https://docs.openhands.dev/sdk).

Watch the companion deep dive: [Dynamic Workflows deep-dive video](https://www.youtube.com/watch?v=PtbrKTgj3X8).

> **About this implementation:** This is the OpenHands SDK's implementation of dynamic workflows,
> inspired by [Claude Code's Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code).
> We don't know exactly how Anthropic implements it — this is our interpretation using open source tools. See the [original PR](https://github.com/OpenHands/software-agent-sdk/pull/3426).

---

## The Problem

Building multi-agent systems today means **manually orchestrating sub-agents**. You write the loops, manage state, and coordinate everything.

[See the Old Way →](https://rajshah4.github.io/workflow-demos/old-way.html)

---

## The Solution

What if the model wrote its own orchestration? With workflows, you **give the model a task and the tools**. The model decides how to structure the workflow.

[See the New Way →](https://rajshah4.github.io/workflow-demos/new-way.html)

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

---

## Deep Research Example

Anthropic used deep research as their example. Here's **our version** using OpenHands workflows.

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

**3. You Write the Setup** — Create the parent agent with skills and sub-agents.

```python
parent_agent = Agent(
    llm=LLM(model="gpt-4o-mini"),
    tools=[Tool(name=WorkflowToolSet.name)],
    agent_context=AgentContext(skills=[ORCHESTRATOR_SKILL])
)
```

**4. The Model Writes the Orchestration** — Behind the scenes, the model generates and runs this:

```python
# This is what the model writes (you never see this)
async def main(wf):
    # Model decides: which angles to research
    angles = ['Market overview', 'Technical capabilities', 'Expert opinions', ...]
    
    # Model calls: fan out to web_searcher agents in parallel
    market_data = await wf.map_agents(angles, 'web_searcher')
    
    # Model calls: cross-check with fact_checker
    verified = await wf.map_agents(market_data, 'fact_checker')
    
    # Model calls: synthesize into final report
    return await wf.reduce_agent(verified, 'synthesizer')
```

**The model handles: which angles to research, which sub-agents to use when, parallel vs sequential execution, how to aggregate results.**

---

## Multi-Expert Code Review Example

Another use case: parallel code review with specialized agents.

```python
# Run 4 reviewers in parallel (workflow version)
python multi_expert_review/multi_expert_review.py <file_path>

# Run 4 reviewers sequentially (manual version)
python multi_expert_review/multi_expert_review_manual.py <file_path>
```

---

## Quick Start

### 1. Install the SDK (with workflow support)

The workflow tool is in [PR #3426](https://github.com/OpenHands/software-agent-sdk/pull/3426). If it hasn't been merged yet:

```bash
# Clone the SDK
git clone https://github.com/OpenHands/software-agent-sdk.git
cd software-agent-sdk

# Checkout the PR branch
git fetch origin pull/3426/head:workflow-pr
git checkout workflow-pr

# Install
pip install -e .
```

Or just `pip install openhands` if the PR is merged.

### 2. Run the demos

```bash
# Add your API key
echo "OPENAI_API_KEY=sk-..." > .env

# Deep research demos
python deep_research/deep_research_workflow.py "What is the AI coding assistant market size?"
python deep_research/deep_research_manual.py "What is the AI coding assistant market size?"

# Multi-expert review demos
python multi_expert_review/multi_expert_review.py <file_path>
python multi_expert_review/multi_expert_review_manual.py <file_path>
```

---

## Resources

- [Dynamic Workflows deep-dive video](https://www.youtube.com/watch?v=PtbrKTgj3X8) — Walkthrough of this repo's deep-research workflow demo
- [OpenHands SDK](https://github.com/OpenHands/software-agent-sdk) — Our implementation
- [PR #3426: Dynamic Workflow Tool](https://github.com/OpenHands/software-agent-sdk/pull/3426) — The code
- [Claude Code: Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code) — Their blog post
- [LangChain: Deep Research](https://docs.langchain.com/oss/python/deepagents/deep-research) — Example of manual orchestration
