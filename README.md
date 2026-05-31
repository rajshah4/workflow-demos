# Dynamic Workflows Walkthrough

**Dive into agents that write their own orchestration code.**

As models improve, we are now seeing agents can now *write the orchestration loop themselves*. This repo walks through an example using the [OpenHands SDK](https://docs.openhands.dev/sdk)

> **About this implementation:** This is the OpenHands SDK's implementation of dynamic workflows,
> inspired by [Claude Code's Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code).
> We don't know exactly how Anthropic implements it — this is our interpretation using open source tools. You can peek at the [original PR](https://github.com/OpenHands/software-agent-sdk/pull/3426) adding workflows.

---

## The Problem

Everyone's building multi-agent systems. You end up having to manually orchestrate sub-agents. People often use frameworks like [LangChain](https://docs.langchain.com/oss/python/deepagents/deep-research) to orchestrate agents. 

Here is a visualization of [The Old Way](old-way.html)

---

## The Solution

What if the model wrote it's own orchestration?  With workflows, you tell the model to go solve the problem using workflows and subagents. The model is then reponsisble for handling all the orchestration code. So intead of 25+ lines of orchestration code, you move to 2 lines handing that task over to the model.

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

Here are some visualziations doing a [Side-by-Side Comparison](comparison.html) for th's new [workflows](new-way.html) approach. 

---

## Deep Research Example

The Anthropic example used deep research as an example use case. So let's walkthrough a [Deep Research Demo](deep_research/comparison.html) to illustrate this. 

---

## Quick Start

```bash
# Add your API key
echo "OPENAI_API_KEY=sk-..." > .env

# Run the demo
python deep_research/deep_research.py "What is the AI coding assistant market size?"
```

Or just open any of the HTML pages in a browser — no API key needed for the demos.

---

## The Primitives Stack

Before dynamic workflows, there were two other patterns:

| Primitive | Limitation |
|-----------|------------|
| **Subagents** | Can't talk to each other, main agent is bottleneck |
| **Agent Teams** | Top out at 3-5 teammates, sessions die with interruption |

Dynamic workflows solve both: up to 16 concurrent agents, 1,000 total per workflow, with context isolation.

---

## Resources

- [OpenHands SDK](https://github.com/OpenHands/software-agent-sdk) — Our implementation
- [PR #3426: Dynamic Workflow Tool](https://github.com/OpenHands/software-agent-sdk/pull/3426) — The code
- [Claude Code: Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code) — Their blog post (we don't have source code)
- [LangChain: Deep Research](https://docs.langchain.com/oss/python/deepagents/deep-research) — Example of manual orchestration

---

## What We Know vs Don't Know

| What | Status |
|------|--------|
| **Pattern**: Agent writing orchestration | Known (from blog post) |
| **Skill pattern**: Guidance for agent | Known (inferred from blog) |
| **Sub-agents**: Pre-defined roles | Known (inferred from blog) |
| **OpenHands implementation** | Known (our code) |
| **Anthropic's actual implementation** | Unknown (proprietary) |

This repo shows the OpenHands implementation of the pattern described in Anthropic's blog.

