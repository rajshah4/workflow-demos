# Dynamic Workflows Deep Dive

**A technical exploration of agent-written orchestration with the OpenHands SDK**

*This document is the foundation for a YouTube video series. It walks through the architecture, implementation, and live trace analysis of dynamic workflows.*

---

## Table of Contents

1. [The Problem with Manual Orchestration](#1-the-problem-with-manual-orchestration)
2. [The Solution: Agent-Written Workflows](#2-the-solution-agent-written-workflows)
3. [Architecture Deep Dive](#3-architecture-deep-dive)
4. [The WorkflowToolSet API](#4-the-workflowtoolset-api)
5. [Live Trace Analysis](#5-live-trace-analysis)
6. [How Sub-Agents Work](#6-how-sub-agents-work)
7. [Laminar Observability](#7-laminar-observability)
8. [Running the Demo](#8-running-the-demo)

---

## 1. The Problem with Manual Orchestration

When you build multi-agent systems today, you end up writing something like this:

```python
# Every. Single. Time.
prompts = {
    "market": "Research market trends...",
    "tech": "Research tech...",
    "legal": "Research legal...",
}

agents = [Agent(llm, prompts[k]) for k in prompts]

# You write the loop
results = []
for agent in agents:
    conv = Conversation(agent)
    conv.send_message(f"Research {key}")
    results.append(conv.run())

# You aggregate
synth = Conversation(synthesizer)
synth.send_message(f"Combine: {results}")
report = synth.run()
```

**Problems:**
- 30+ lines of orchestration code
- You control the loop — not the agent
- If you want parallel, you have to thread/batch it yourself
- Every project repeats this pattern
- The agent that should be *doing* the work is just a worker

### The Manual Orchestration Stack

| Layer | Who Controls | Code |
|-------|--------------|------|
| Orchestration | You | `for agent in agents:` |
| Agent routing | You | `Conversation(agent)` |
| Result aggregation | You | `results.append()` |
| Agent execution | Agent | `conv.run()` |

You write everything except the agent itself.

---

## 2. The Solution: Agent-Written Workflows

What if instead of writing the loop yourself, you give the agent a **tool** that lets it write the loop?

```python
# You just write this:
parent_agent = Agent(
    llm=llm,
    tools=[Tool(name=WorkflowToolSet.name)],  # ← The magic
    agent_context=AgentContext(skills=[
        Skill(name="orchestrator", content="When asked to research deeply, write a workflow...")
    ])
)

conversation = Conversation(agent=parent_agent)
conversation.send_message("Research the AI market from multiple angles")
conversation.run()

# The agent writes the orchestration:
# async def main(wf):
#     data = await wf.map_agents(angles, subagent_type='researcher')
#     return await wf.reduce_agent(data, subagent_type='synthesizer')
```

### The Agent Workflow Stack

| Layer | Who Controls | Code |
|-------|--------------|------|
| Orchestration | Agent | `async def main(wf):` |
| Agent routing | Agent | `wf.map_agents()` |
| Result aggregation | Agent | `wf.reduce_agent()` |
| Agent execution | Agent | (handled by SDK) |

**You write 2 lines. The agent writes 20+.**

---

## 3. Architecture Deep Dive

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Application                         │
│                                                                 │
│  conversation.send_message("Research the AI market")            │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Parent Agent                           │  │
│  │                                                           │  │
│  │   System: You are OpenHands agent...                      │  │
│  │   Skills: research_orchestrator                           │  │
│  │   Tools: [terminal, file_editor, workflow]                │  │
│  │                                                           │  │
│  │   Thinking: I should write a parallel research workflow  │  │
│  │                         │                                 │  │
│  │                         ▼                                 │  │
│  │   Tool: workflow                                         │  │
│  │   Script: async def main(wf):                            │  │
│  │              data = await wf.map_agents(angles,          │  │
│  │                       subagent_type='web_searcher')      │  │
│  │              return await wf.reduce_agent(data,          │  │
│  │                       subagent_type='synthesizer')        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │               WorkflowContext (wf)                       │  │
│  │                                                           │  │
│  │   .map_agents(items, subagent_type) → [results]          │  │
│  │   .reduce_agent(items, subagent_type) → result           │  │
│  │   .run_agent(prompt, subagent_type) → result             │  │
│  │                                                           │  │
│  │   Manages sub-agent lifecycle and aggregation             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐      │
│  │ web_searcher│ web_searcher│ web_searcher│ web_searcher│ ...  │
│  │   (Task 1)  │   (Task 2)  │   (Task 3)  │   (Task 4)  │      │
│  │  parallel   │  parallel   │  parallel   │  parallel   │      │
│  └─────────────┴─────────────┴─────────────┴─────────────┘      │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐      │
│  │fact_checker │fact_checker │fact_checker │fact_checker │ ...  │
│  │   (Task 1)  │   (Task 2)  │   (Task 3)  │   (Task 4)  │      │
│  └─────────────┴─────────────┴─────────────┴─────────────┘      │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    synthesizer                          │    │
│  │              (Creates final report)                     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **WorkflowToolSet** — The tool that exposes workflow capabilities to agents
2. **WorkflowContext (wf)** — The runtime object the agent uses to call `map_agents`, `reduce_agent`, etc.
3. **TaskManager** — Manages sub-agent lifecycle (create, run, aggregate results)
4. **LocalConversation** — Each sub-agent runs in its own conversation

---

## 4. The WorkflowToolSet API

The `WorkflowToolSet` exposes three primary methods:

### `wf.map_agents()`

Run one sub-agent per item in parallel.

```python
results = await wf.map_agents(
    items=['angle1', 'angle2', 'angle3'],  # Items to process
    prompt='Research: {item}',              # Template with {item} placeholder
    subagent_type='web_searcher',          # Registered sub-agent type
    max_concurrency=3,                      # Max parallel tasks (optional)
    description=None                        # Task description (optional)
)
```

**Returns:** List of results, one per item (in order).

**Use case:** Fan-out parallel work (research multiple angles simultaneously).

### `wf.reduce_agent()`

Run a single sub-agent to aggregate results.

```python
final_report = await wf.reduce_agent(
    items=[result1, result2, result3],     # Items to aggregate
    prompt='Synthesize: {items}',           # Template with {items} placeholder
    subagent_type='synthesizer'            # Registered sub-agent type
)
```

**Returns:** Single aggregated result.

**Use case:** Reduce/fold pattern (combine multiple findings into one report).

### `wf.run_agent()`

Run a single sub-agent with a prompt.

```python
result = await wf.run_agent(
    prompt='Run this specific task',
    subagent_type='general-purpose',
    description='One-off task'
)
```

**Returns:** Single result.

**Use case:** Simple delegation without aggregation.

---

## 5. Live Trace Analysis

We ran the deep research workflow to answer: **"What is the AI coding assistant market size in 2024?"**

### Metrics

| Metric | Value |
|--------|-------|
| Total Time | 81.24s |
| Total Tokens | 180K (141K cached) |
| Total Cost | $0.0186 |
| Sub-agents Spawned | 11 |

### Hierarchical Trace

```
Deep Research Agent (81.24s)
└── WorkflowAction (74.36s, $0.0173)
    ├── [Parallel] web_searcher agents (54.93s)
    │   ├── Task 1: "Research AI coding assistant market overview..." (9.86s)
    │   ├── Task 2: "Search for AI coding assistant market size..." (8.99s)
    │   ├── Task 3: "Search for AI coding assistant key players..." (11.75s)
    │   ├── Task 4: "Research AI coding assistant expert opinions..." (10.37s)
    │   └── Task 5: "Research AI coding assistant trends..." (11.75s)
    │
    ├── [Parallel] fact_checker agents (34.63s)
    │   ├── Task 1: "Fetch information on market size..." (9.24s)
    │   ├── Task 2: "Fetch details on growth data..." (9.59s)
    │   ├── Task 3: "Gather from alternative sources..." (9.51s)
    │   ├── Task 4: (continued)
    │   └── Task 5: (continued)
    │
    └── [Final] synthesizer agent
        └── Created executive summary report
```

### What Each Layer Did

#### Layer 1: Parent Agent
- Received the task
- Decided to write a workflow
- Used `WorkflowToolSet` to execute the workflow
- **Total: 81.24s, $0.0186**

#### Layer 2: Workflow Execution
- Wrote the orchestration script
- Called `wf.map_agents()` for web_searchers (5 parallel)
- Called `wf.map_agents()` for fact_checkers (5 parallel)
- Called `wf.reduce_agent()` for synthesis
- **Total: 74.36s, $0.0173**

#### Layer 3: Web Searcher Agents
- Each ran `curl` or `wget` to fetch data
- Returned findings with sources
- **Total: 54.93s (5 parallel)**

#### Layer 4: Fact Checker Agents
- Cross-referenced claims from web searchers
- Assigned confidence scores
- **Total: 34.63s (5 parallel)**

#### Layer 5: Synthesizer Agent
- Combined all verified findings
- Created executive summary with citations
- **Single agent, final output**

---

## 6. How Sub-Agents Work

### Registration

Before the workflow runs, sub-agents are registered:

```python
from openhands.sdk.subagent import register_agent_if_absent

register_agent_if_absent(
    "web_searcher",
    create_web_searcher,
    "Searches the web for information"
)

register_agent_if_absent(
    "fact_checker",
    create_fact_checker,
    "Cross-checks claims against sources"
)

register_agent_if_absent(
    "synthesizer",
    create_synthesizer,
    "Synthesizes research into reports"
)
```

### Factory Pattern

Each sub-agent type is a factory that creates agents with the same LLM but different system prompts:

```python
def create_web_searcher(llm: LLM) -> Agent:
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name)],
        agent_context=AgentContext(
            skills=[Skill(name="web_researcher", content="You are a thorough web researcher...")],
            system_message_suffix="You cite sources for every claim."
        )
    )
```

### TaskManager

The `TaskManager` handles sub-agent lifecycle:

```python
class TaskManager:
    def start_task(self, prompt, subagent_type, conversation):
        # 1. Get factory for subagent_type
        # 2. Create agent with parent's LLM
        # 3. Create new LocalConversation
        # 4. Run conversation
        # 5. Return result
```

### Isolation

Each sub-agent runs in its own `LocalConversation`:
- Separate conversation ID
- Separate event log
- Separate workspace
- Parent's LLM (but with streaming disabled)

This isolation ensures:
- Sub-agent failures don't crash the parent
- Each sub-agent can be independently traced
- Memory doesn't leak between sub-agents

---

## 7. Laminar Observability

The OpenHands SDK integrates with Laminar for observability. Every workflow run produces detailed traces.

### What Gets Traced

| Event | Traced As |
|-------|-----------|
| Parent agent thinking | Span |
| WorkflowAction | Span with script |
| Sub-agent creation | Child span |
| Sub-agent execution | Child span |
| Terminal actions | Child span |
| Errors | Error events |

### Trace Structure

```json
{
  "conversation_id": "df52139c-5b7b-430b-9568-6c24eab202fb",
  "spans": [
    {
      "name": "Deep Research Agent",
      "duration_ms": 81240,
      "children": [
        {
          "name": "WorkflowAction",
          "duration_ms": 74360,
          "attributes": {
            "script": "async def main(wf): ...",
            "result": "### Executive Summary ..."
          },
          "children": [
            {
              "name": "web_searcher Task 1",
              "duration_ms": 9860
            },
            {
              "name": "web_searcher Task 2",
              "duration_ms": 8990
            }
          ]
        }
      ]
    }
  ]
}
```

### Enabling Laminar

```python
# Set environment variables
export LMNR_PROJECT_API_KEY=your_key

# Or in code
from lmnr import Laminar
Laminar.initialize(project_api_key="your_key")
```

### Viewing Traces

1. Go to your Laminar dashboard
2. Find the conversation ID (logged in output)
3. Explore the hierarchical trace
4. See sub-agent conversations as children

---

## 8. Running the Demo

### Prerequisites

- Docker (for clean environment)
- OpenAI API key (or Anthropic)

### Quick Start

```bash
# Clone the repo
git clone https://github.com/rajshah4/workflow-demos.git
cd workflow-demos

# Create .env with your API key
echo "OPENAI_API_KEY=sk-..." > .env

# Run in Docker (clean environment)
docker build -t workflow-demo .
docker run --rm workflow-demo "What is the AI coding assistant market size in 2024?"
```

### Local Development

```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ../sdk-pr3426/openhands-sdk
uv pip install -e ../sdk-pr3426/openhands-tools

# Clone SDK (if not present)
git clone --branch redo-dynamic-workflow-mvp \
    https://github.com/OpenHands/software-agent-sdk.git ../sdk-pr3426

# Run
python deep_research/deep_research.py "Your research question"
```

### Docker Troubleshooting

If you get file descriptor errors on macOS:
```
FD from fork parent still in poll list: fd(9, generation: 1)
```

**This is a macOS-specific issue.** The fix is to run in Docker where the environment is clean.

---

## Key Takeaways

1. **Agents can write their own orchestration** — This is the breakthrough. Not just "agents using agents," but "agents writing the code that orchestrates agents."

2. **Two lines vs. 30+ lines** — You write `send_message()` + `run()`. The agent writes the loop.

3. **Parallel by default** — `wf.map_agents()` runs tasks concurrently. No manual threading.

4. **Sub-agent isolation** — Each sub-agent runs in its own conversation. Failures are contained.

5. **Observability built-in** — Laminar traces show the full hierarchical execution.

6. **Cost is predictable** — $0.0186 for 11 sub-agents. Each call is logged.

---

## Further Reading

- [OpenHands SDK](https://github.com/OpenHands/software-agent-sdk)
- [WorkflowToolSet PR #3426](https://github.com/OpenHands/software-agent-sdk/pull/3426)
- [Laminar Observability](https://docs.lmnr.ai)

---

*Document version: 1.0*  
*Last updated: 2026-05-30*