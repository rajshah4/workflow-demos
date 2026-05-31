# Dynamic Workflows: The Old Way vs. The New Way
## Video Script with Speaker Notes

*Estimated runtime: 18-20 minutes*  
*Target audience: Developers, AI engineers, tech leads*

---

## PART 1: THE HOOK
**Duration: 30 seconds**

**[On screen: Terminal showing code being deleted]**

> "Last week, I had 40 lines of orchestration code. Today, I have 2. The rest? My AI writes it."
>
> "And it's not just writing the code — it's writing the code that coordinates other AI agents. That's the breakthrough you've probably been hearing about, but nobody's shown you how it actually works."
>
> "In this video, I'm going to show you exactly how dynamic workflows work — the old way, the new way, and a live demo so you can see it in action."

**[Transition: clean background, presenter appears]**

---

## PART 2: THE PROBLEM (The Old Way)
**Duration: 4-5 minutes**

### 2.1 Show the Pain
**Duration: 2 minutes**

**[On screen: Multiple screens showing different orchestration patterns]**

> "Let me show you what building multi-agent systems looks like today. And I mean really building them — not the toy examples."
>
> "The problem isn't that agents can't use other agents. That's been possible for years. The problem is: **who writes the orchestration code?**"

**[Cut to: Code example - traditional multi-agent]**

```python
# This is what everyone writes today
from openhands.sdk import Agent, Conversation

prompts = {
    "market": "Research market trends...",
    "tech": "Research technology developments...",
    "legal": "Research legal considerations...",
    "competitors": "Research competitor strategies...",
}

# Create agents
agents = {name: Agent(llm, prompts[name]) for name in prompts}

# Create conversations
conversations = {name: Conversation(agent) for name, agent in agents.items()}

# Run SEQUENTIALLY (because you wrote the loop)
results = {}
for name, conv in conversations.items():
    conv.send_message(f"Research {name}")
    result = conv.run()
    results[name] = result

# Aggregate yourself
synth_conv = Conversation(synthesizer)
synth_conv.send_message(f"Combine all research: {results}")
final_report = synth_conv.run()
```

> "Look at this code. It's not bad code — it's actually well-structured. But notice who wrote it: **me**. I wrote the loop. I wrote the sequential execution. I wrote the aggregation."
>
> "And here's the thing — I have to write this same pattern for **every single project**. Market research? Write the loop. Code review? Write the loop. Data analysis? Write the loop."

### 2.2 The Problems with This Approach
**Duration: 2 minutes**

**[On screen: List of problems]**

> "Now, let's count the problems with this approach:"
>
> "**Problem 1: It's sequential by default.** I have to explicitly write code to run things in parallel. And parallel execution? That's hard. You need thread pools, async handlers, result aggregation..."
>
> "**Problem 2: You control the loop.** Not the agent. The agent is just a worker. It doesn't know it's part of a larger workflow."
>
> "**Problem 3: Every project repeats this.** The orchestration code looks the same across projects. The only thing that changes is the prompts and the sub-agent types."
>
> "**Problem 4: It's fragile.** Want to add a new research angle? You modify the loop. Want to change the aggregation? You modify the loop. The loop becomes this massive piece of code you have to maintain."
>
> "**Problem 5: The agent doesn't learn.** Each time you run this, the agent starts fresh. It doesn't learn from previous orchestrations because you're the one orchestrating, not the agent."

### 2.3 The Mental Model
**Duration: 1 minute**

**[On screen: Diagram of manual orchestration]**

```
┌─────────────────────────────────────────────┐
│             YOUR CODE                       │
│                                             │
│  for agent in agents:                       │
│      results.append(agent.run())            │
│                                             │
│  synthesizer.combine(results)              │
└─────────────────────────────────────────────┘
          │                         ▲
          │                         │
          ▼                         │
    ┌─────────────────────────────────┐
    │         AGENTS                  │
    │   [worker] [worker] [worker]    │
    └─────────────────────────────────┘
```

> "Think of it this way: you are the conductor. The agents are the musicians. You tell each musician when to play, what to play, and how long to play."
>
> "This works. But it's exhausting. And it doesn't scale."

---

## PART 3: THE SOLUTION (The New Way)
**Duration: 5-6 minutes**

### 3.1 The Key Insight
**Duration: 1 minute**

**[On screen: Simple animation of an agent writing code]**

> "Here's the key insight: what if instead of you writing the orchestration code, you gave the agent a **tool** that lets it write the orchestration code?"
>
> "Not a tool that runs a predefined workflow. Not a tool that picks from a menu. A tool that lets the agent write whatever orchestration logic it thinks is appropriate."
>
> "And then the agent writes the code. Just like it writes any other code."

### 3.2 Show the New Code
**Duration: 2 minutes**

**[On screen: The two-line version vs. the 40-line version]**

```python
# THE NEW WAY - What YOU write:
from openhands.sdk import Agent, Conversation
from openhands.tools.workflow import WorkflowToolSet

parent_agent = Agent(
    llm=llm,
    tools=[Tool(name=WorkflowToolSet.name)],  # ← THE TOOL
    agent_context=AgentContext(skills=[
        Skill(name="orchestrator", content=(
            "When asked to research deeply, write a workflow using "
            "wf.map_agents() for parallel research and "
            "wf.reduce_agent() for synthesis."
        ))
    ])
)

conversation = Conversation(agent=parent_agent)
conversation.send_message("Research the AI coding assistant market")
conversation.run()
```

> "This is it. This is the entire orchestration code. 12 lines."
>
> "The agent receives the task, decides it needs to research multiple angles in parallel, and writes the orchestration code to make that happen."
>
> "What does the agent write? Let me show you."

### 3.3 What the Agent Writes
**Duration: 2 minutes**

**[On screen: The code the agent wrote]**

```python
# What the agent wrote:
async def main(wf):
    # Fan out research to multiple angles
    angles = [
        'Market overview and major players',
        'Technical developments and innovations',
        'Expert opinions and analysis',
        'Statistics and data points',
        'Debates, concerns, or counterarguments'
    ]
    
    # Run web_searcher agents in parallel
    market_data = await wf.map_agents(
        items=angles,
        prompt='Research: {item}',
        subagent_type='web_searcher',
        max_concurrency=3
    )
    
    # Cross-check claims
    verified_data = await wf.map_agents(
        items=market_data,
        prompt='Verify this claim: {item}',
        subagent_type='fact_checker'
    )
    
    # Synthesize into final report
    final_report = await wf.reduce_agent(
        items=verified_data,
        prompt='Create report: {items}',
        subagent_type='synthesizer'
    )
    
    return final_report
```

> "The agent wrote this. It decided to: one, fan out research across five angles in parallel. Two, cross-check the findings with a fact-checker. Three, synthesize everything into a final report."
>
> "It wrote 25 lines of orchestration. I wrote 12."
>
> "And here's the beautiful part — **the agent can change this logic**. If I ask a different question, the agent might write a completely different workflow. Maybe it needs more steps. Maybe fewer. Maybe different sub-agents."
>
> "The agent is in control. Not me."

### 3.4 The New Mental Model
**Duration: 1 minute**

**[On screen: New diagram with agent writing orchestration]**

```
┌─────────────────────────────────────────────┐
│             YOUR CODE                       │
│                                             │
│  conversation.send_message(task)           │
│  conversation.run()                         │
│                                             │
│  That's it. That's all you write.           │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           PARENT AGENT                      │
│                                             │
│  thinking...                                │
│  "I should write a workflow"                │
│  writes async def main(wf): ...             │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│        WORKFLOW CONTEXT (wf)                │
│                                             │
│  wf.map_agents()  wf.reduce_agent()        │
└─────────────────────────────────────────────┘
                    │
                    ▼
    ┌─────────────────────────────────┐
    │         SUB-AGENTS              │
    │  [researcher] [checker] [synth]│
    │      (agent writes these too)   │
    └─────────────────────────────────┘
```

> "Now the agent is the conductor. You give it a task, it decides how to orchestrate."
>
> "This is the paradigm shift. It's not just 'agents using agents' — it's 'agents writing the orchestration logic for other agents.'"

---

## PART 4: THE LIVE DEMO
**Duration: 8-10 minutes**

### 4.1 Setup the Demo
**Duration: 1 minute**

**[On screen: Docker running]**

> "Let me show you this working. I'm running this in Docker because it gives us a clean environment."
>
> "The question we're going to ask: 'What is the AI coding assistant market size in 2024?'"
>
> "The agent will research this from multiple angles in parallel, cross-check the findings, and synthesize a report."

### 4.2 Run the Demo
**Duration: 5 minutes**

**[On screen: Terminal output scrolling]**

```bash
docker run --rm workflow-demo \
    python3 deep_research/deep_research.py \
    "What is the AI coding assistant market size in 2024?"
```

> "[Walk through the output as it runs]"
>
> "See how the agent is thinking? It's deciding to write a workflow."
>
> "Now watch — the workflow is executing. We have 5 web searcher agents running in parallel..."
>
> "Each sub-agent is doing its own research. They're all running simultaneously."
>
> "Now the fact-checkers are running. Each one is verifying claims from the research phase."
>
> "And finally, the synthesizer is creating the report..."

### 4.3 Show the Results
**Duration: 2 minutes**

**[On screen: Final report output]**

> "Look at this report. It has an executive summary, key findings, sources, areas of uncertainty, and next steps."
>
> "The agent decided to structure it this way. I didn't specify the format — the agent did."
>
> "And check this out — the total cost was 1.86 cents. For 11 sub-agents working in parallel."
>
> "Let me show you the trace."

### 4.4 Show the Trace
**Duration: 2 minutes**

**[On screen: Laminar trace visualization]**

> "This is the trace from Laminar. You can see the hierarchical structure."
>
> "At the top: the parent agent. 81 seconds total."
>
> "Underneath: the WorkflowAction. 74 seconds. This is where the agent wrote the orchestration code."
>
> "Then you see the child spans — each sub-agent running in parallel."
>
> "And each sub-agent has its own trace. You can expand any of these to see exactly what it did."
>
> "This is powerful for debugging. If something goes wrong, you can see exactly which sub-agent failed and why."

---

## PART 5: THE DEEP DIVE
**Duration: 4-5 minutes**

### 5.1 How Sub-Agents Work
**Duration: 2 minutes**

**[On screen: Sub-agent architecture]**

> "Let me explain how sub-agents work under the hood."
>
> "First, you register them. This is the only manual work you do — defining what types of sub-agents exist."

```python
from openhands.sdk.subagent import register_agent_if_absent

register_agent_if_absent(
    "web_searcher",
    create_web_searcher,
    "Searches the web for information"
)

def create_web_searcher(llm: LLM) -> Agent:
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name)],
        agent_context=AgentContext(
            skills=[Skill(name="web_researcher", content=(
                "You are a thorough web researcher. Search for information..."
            ))]
        )
    )
```

> "The factory pattern means each sub-agent gets the same LLM but with a different system prompt. This is efficient — no redundant model loading."
>
> "Each sub-agent runs in its own LocalConversation. They're isolated. If one fails, it doesn't crash the others."

### 5.2 The WorkflowToolSet API
**Duration: 1.5 minutes**

**[On screen: API documentation]**

> "The WorkflowToolSet exposes three main methods:"
>
> "`map_agents()` — Runs multiple sub-agents in parallel. Think of it like `Promise.all()`."
>
> "`reduce_agent()` — Runs a single sub-agent to aggregate results. Think of it like `reduce()`."
>
> "`run_agent()` — Runs a single sub-agent. For simple delegation."
>
> "That's it. Simple API, powerful semantics."

### 5.3 When to Use This (and When Not To)
**Duration: 1.5 minutes**

**[On screen: Decision matrix]**

> "Dynamic workflows are great for:"
>
> "- Research tasks that need multiple angles"
> "- Code review with multiple expert perspectives"
> "- Data aggregation from many sources"
> "- Any task where parallel execution beats sequential"
>
> "But they're not right for everything:"
>
> "- Simple single-agent tasks — overkill"
> "- Real-time critical systems — latency matters"
> "- When you need deterministic control — agents are non-deterministic"
> "- Low-budget projects — each workflow run costs tokens"

---

## PART 6: COMPARE TO ALTERNATIVES
**Duration: 2 minutes**

**[On screen: Comparison table]**

| Approach | Who writes loop | Parallel by default | Agent learns |
|----------|----------------|--------------------|--------------|
| Manual (today) | You | No | No |
| LangChain | You | Optional | No |
| LangGraph | You | Optional | No |
| CrewAI | You | Optional | No |
| **Dynamic Workflows** | **Agent** | **Yes** | **Yes** |

> "The key difference: everyone else has you writing the loop. Dynamic workflows have the agent writing the loop."
>
> "This isn't better or worse — it's a different paradigm. If you want full control, use LangGraph. If you want the agent to figure it out, use dynamic workflows."

---

## PART 7: WRAP UP
**Duration: 1 minute**

**[On screen: Code comparison again]**

> "Let me leave you with the code comparison."
>
> "Old way: 40 lines. You write the loop."
>
> "New way: 12 lines. The agent writes the loop."
>
> "The breakthrough isn't that agents can use other agents. It's that agents can now write the orchestration code that coordinates those agents."
>
> "Try it yourself. The code is on my GitHub. Link in the description."
>
> "If this was helpful, smash that subscribe button. I'll see you in the next one."

---

## APPENDIX: Timestamps

```
00:00 - HOOK: "I deleted 40 lines of orchestration code"
00:30 - THE PROBLEM: What building multi-agent systems looks like today
04:30 - THE SOLUTION: What if the agent writes the orchestration?
09:30 - LIVE DEMO: Running the workflow
16:30 - DEEP DIVE: How sub-agents work
18:00 - COMPARE: How is this different from LangChain?
20:00 - WRAP UP: The key insight
```

---

## APPENDIX: Required Visuals

1. **Hook animation**: Terminal with code being deleted
2. **Problem code**: 40-line manual orchestration
3. **Old mental model diagram**: You → loop → agents
4. **New code**: 12-line version
5. **Agent's code**: What the agent wrote
6. **New mental model diagram**: You → agent → wf → agents
7. **Demo terminal**: Docker running, output scrolling
8. **Final report**: The output showing executive summary
9. **Laminar trace**: Hierarchical trace visualization
10. **Sub-agent architecture**: Factory pattern diagram
11. **API docs**: map_agents, reduce_agent, run_agent
12. **Comparison table**: Old vs. new vs. alternatives
13. **Final code comparison**: 40 lines vs 12 lines

---

*Script version: 1.0*  
*Last updated: 2026-05-30*