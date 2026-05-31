# Dynamic Workflows Demo

**When agents write their own orchestration code.**

The breakthrough isn't that agents can use other agents. It's that agents can now *write the orchestration loop themselves*.

> **About this implementation:** This is the OpenHands SDK's implementation of dynamic workflows,
> inspired by [Claude Code's Dynamic Workflows](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code).
> We don't know exactly how Anthropic implements it — this is our interpretation using open source tools.

---

## The Question

Everyone's building multi-agent systems. Most of them are secretly a mess:

- Sub-agents pollute the main context
- Parallelism requires manual orchestration
- You end up writing more framework than code

**The interesting question isn't "can agents use other agents?" It's *where the orchestration logic lives*.**

---

## The Pattern

| Approach | You Write | Agent Writes |
|----------|-----------|--------------|
| **Manual** (LangChain style) | The loop, the agents, the aggregation | Nothing |
| **Dynamic** (Workflows) | Just the objective | The entire orchestration |

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

## Explore the Story

### [Comparison Guide](https://rajshah4.github.io/workflow-demos/comparison.html)
Side-by-side code comparison: what *you* write vs what the *agent* writes.

### [The Bitter Lesson](https://rajshah4.github.io/workflow-demos/bitter-lesson.html)
The progression: Year 1 (you write the loop) → Year N (model writes everything).

### [The Org Chart](https://rajshah4.github.io/workflow-demos/org-chart.html)
"Subagents are workers. Workflows are the management system."

### [Stack Overview](https://rajshah4.github.io/workflow-demos/index.html)
The L1-L4 stack model for agent orchestration.

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

---

## For Content Creators

### [Video Script](VIDEO_SCRIPT.md)
Complete script with speaker notes for an 18-20 minute YouTube video covering:
- The Old Way: Manual orchestration (40 lines)
- The New Way: Agent-written orchestration (12 lines)
- Live demo with real trace
- Deep dive into sub-agents and Laminar

### [Deep Dive Document](DEEP_DIVE.md)
Technical reference covering:
- Architecture deep dive
- WorkflowToolSet API
- Live trace analysis
- Sub-agent lifecycle
- Laminar observability

### [Live Trace (from real run)](https://rajshah4.github.io/workflow-demos/index.html#live-trace)
The actual trace from running the deep research workflow:
- 81.24s total time
- 180K tokens ($0.0186)
- 11 sub-agents in parallel