# Dynamic Workflows Demo - OpenHands SDK

**PR #3426: When agents write their own orchestration code**

## The Key Insight

> "Subagents are workers. Workflows are the management system."

The breakthrough isn't that agents can use other agents. It's that **agents can now write the orchestration loop themselves**.

## Manual vs Dynamic

| | Manual (No Workflows) | Dynamic (Workflows) |
|---|---|---|
| **Example** | [LangChain Deep Research](https://docs.langchain.com/oss/python/deepagents/deep-research) | [Claude Code Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code) |
| **Who writes loop** | You (developer) | Agent (at runtime) |
| **Code you write** | 25+ lines of orchestration | 2 lines (the objective) |
| **Parallelism** | Manual | Native via `wf.map_agents()` |

## How It Works

```
┌─────────────────────────────────────────────────────┐
│ YOU                                               │
│  - Create parent agent with WorkflowToolSet        │
│  - Give the objective                             │
└──────────────────────┬────────────────────────────┘
                       │ "Research X from multiple angles"
                       ▼
┌─────────────────────────────────────────────────────┐
│ PARENT AGENT                                      │
│  - Has skill: "research_orchestrator"             │
│  - Decides: use workflow for multi-angle research │
│  - Writes: async def main(wf): ...                │
└──────────────────────┬────────────────────────────┘
                       │ WorkflowAction(script)
                       ▼
┌─────────────────────────────────────────────────────┐
│ WORKFLOW EXECUTION                                 │
│  - wf.map_agents("researcher", angles)            │
│  - Parallel execution                             │
│  - wf.reduce_agent("synthesizer", findings)       │
│  - Results isolated from main context             │
└─────────────────────────────────────────────────────┘
```

## The Skill That Triggers Workflows

The agent knows when to use workflows via a **skill**:

```python
Skill(
    name="research_orchestrator",
    content=(
        "When asked to research a topic deeply, write a Python workflow: "
        "(1) fan out web_searcher agents across multiple angles, "
        "(2) cross-check with fact_checker, "
        "(3) use reduce_agent with synthesizer for final report."
    ),
)
```

## Files

```
workflow-demos/
├── index.html                    # Landing page with stack overview
├── comparison.html               # Side-by-side: Manual vs Dynamic
├── README.md                     # This file
├── .env                          # Your API key (create this)
├── deep_research/
│   ├── deep_research.py          # SDK demo (real code)
│   └── deep_research_visual.html # Animated visualization
└── multi_expert_review/
    ├── multi_expert_review.py    # SDK demo (real code)
    └── multi_expert_review_visual.html
```

## Quick Start

```bash
# 1. Add your API key
echo "OPENAI_API_KEY=sk-..." > .env

# 2. Run the demo
cd ~/Code/workflow-demos
python deep_research/deep_research.py "What is the AI coding assistant market size?"

# 3. Or open in browser (no API key needed)
open index.html
open comparison.html
```

## The Two Patterns

### Without Workflows (Manual)
```python
# You write: agents, conversations, loop, aggregation
market_agent = Agent(llm, "Research market...")
tech_agent = Agent(llm, "Research tech...")

market_conv = Conversation(market_agent)
tech_conv = Conversation(tech_agent)

market_result = market_conv.run()  # Wait
tech_result = tech_conv.run()      # Wait

# Aggregate yourself
synthesize([market_result, tech_result])
```

### With Workflows (Dynamic)
```python
# You write: just the objective
conversation.send_message(
    "Research X from multiple angles, then synthesize"
)
conversation.run()

# Agent writes the workflow:
# async def main(wf):
#     findings = await wf.map_agents("researcher", angles)
#     return await wf.reduce_agent("synthesizer", findings)
```

## Resources

- [Claude Code: Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)
- [LangChain: Deep Research (manual pattern)](https://docs.langchain.com/oss/python/deepagents/deep-research)
- [OpenHands SDK PR #3426](https://github.com/OpenHands/software-agent-sdk/pull/3426)