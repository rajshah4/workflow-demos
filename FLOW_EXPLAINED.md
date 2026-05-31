# How Dynamic Workflows Work: The Complete Flow

> **⚠️ IMPORTANT: This is the OpenHands implementation, not Anthropic's.**
> 
> We don't know exactly how Anthropic/Claude Code implements dynamic workflows.
> This is our best interpretation using the OpenHands SDK, which seems inspired by Anthropic's blog post.
> 
> For reference: [Anthropic's Dynamic Workflows blog](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)

## The Three Parts You Write (Ahead of Time)

### 1. SUB-AGENTS (like预定义的 "roles")

These are registered ONCE, like building a team:

```python
# You define what each role can do
def create_web_searcher(llm):
    return Agent(llm=llm, system_message="You search the web and cite sources...")

def create_fact_checker(llm):
    return Agent(llm=llm, system_message="You verify claims...")

def create_synthesizer(llm):
    return Agent(llm=llm, system_message="You create reports...")

# Register them - now they're available to any workflow
register_agent_if_absent("web_searcher", create_web_searcher, "Searches the web")
register_agent_if_absent("fact_checker", create_fact_checker, "Cross-checks claims")
register_agent_if_absent("synthesizer", create_synthesizer, "Creates reports")
```

**Think of this as:** Building a team before the project starts. You have:
- Web Searcher (employee)
- Fact Checker (employee)  
- Synthesizer (employee)

They're ready to work whenever you need them.

### 2. THE SKILL (your instructions to the agent)

This tells the agent WHEN and HOW to use the workflow:

```python
ORCHESTRATOR_SKILL = {
    "name": "orchestrator",
    "content": """
When asked to research deeply:
1. Identify 4-6 distinct research angles
2. Use wf.map_agents() to fan out research in parallel
3. Use wf.reduce_agent() to synthesize findings
4. Structure report with: Executive Summary, Key Findings, Sources, etc.
"""
}
```

**Think of this as:** The training manual for your team lead. It says:
- "When someone asks for deep research, here's what to do"

### 3. THE PARENT AGENT (puts it all together)

```python
parent_agent = Agent(
    llm=LLM(model="gpt-4o-mini"),
    tools=[Tool(name=WorkflowToolSet.name)],  # Gives access to workflow tool
    agent_context=AgentContext(skills=[ORCHESTRATOR_SKILL])
)
```

**Think of this as:** Hiring a team lead. They have:
- The team (sub-agents)
- The training manual (skill)
- The workflow tool (wf.map_agents, etc.)

---

## The Complete Flow (Step by Step)

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: YOU SET UP AHEAD OF TIME (do once)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Sub-agents registered     Skill written       Parent agent        │
│  ┌──────────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │ • web_searcher   │    │ "When deep   │    │ tools: [wf]     │   │
│  │ • fact_checker   │    │  research:   │    │ skills: [skill] │   │
│  │ • synthesizer    │    │  use map +   │    │                 │   │
│  │                  │    │  reduce"     │    │                 │   │
│  └──────────────────┘    └──────────────┘    └─────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: USER SENDS A TASK (runtime)                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  conversation.send_message(                                          │
│    "What is the AI coding assistant market size in 2024?"           │
│  )                                                                  │
│                              │                                      │
│                              ▼                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: PARENT AGENT RECEIVES TASK                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Parent Agent thinks:                                               │
│  "This is a deep research question. The skill tells me to          │
│   use the workflow tool and identify 4-6 angles."                   │
│                              │                                      │
│                              ▼                                      │
│  "Let me use the workflow tool..."                                  │
│                              │                                      │
│                              ▼                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: AGENT WRITES THE WORKFLOW (this happens inside the agent)  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  The agent writes this code (you don't see this, the agent does it)│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ async def main(wf):                                        │    │
│  │     angles = [                                            │    │
│  │         'Market overview and major players',              │    │
│  │         'Technical capabilities',                          │    │  ← Agent decided
│  │         'Expert opinions',                                 │    │    these angles
│  │         'Statistics and data',                             │    │    based on skill
│  │         'Concerns and debates'                             │    │    + question
│  │     ]                                                      │    │
│  │                                                           │    │
│  │     # Fan out to web_searcher agents (parallel)            │    │
│  │     market_data = await wf.map_agents(                    │    │
│  │         items=angles,                                      │    │
│  │         subagent_type='web_searcher'  ← uses registered   │    │
│  │     )                                                      │    │
│  │                                                           │    │
│  │     # Cross-check with fact_checker agents                │    │
│  │     verified = await wf.map_agents(                       │    │
│  │         items=market_data,                                │    │
│  │         subagent_type='fact_checker' ← uses registered   │    │
│  │     )                                                      │    │
│  │                                                           │    │
│  │     # Synthesize with synthesizer                         │    │
│  │     return await wf.reduce_agent(                        │    │
│  │         items=verified,                                   │    │
│  │         subagent_type='synthesizer'  ← uses registered   │    │
│  │     )                                                      │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: WORKFLOW EXECUTES (SDK handles this)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ WorkflowContext (wf)                                       │    │
│  │                                                             │    │
│  │ wf.map_agents(angles, 'web_searcher')                      │    │
│  │    │                                                        │    │
│  │    ├──→ Task 1: "Market overview..." (web_searcher)         │    │
│  │    ├──→ Task 2: "Technical..." (web_searcher)              │    │
│  │    ├──→ Task 3: "Expert opinions..." (web_searcher)        │    │
│  │    ├──→ Task 4: "Statistics..." (web_searcher)            │    │
│  │    └──→ Task 5: "Concerns..." (web_searcher)              │    │
│  │           (all run in parallel)                             │    │
│  │                                                             │    │
│  │ wf.map_agents(results, 'fact_checker')                     │    │
│  │    │                                                        │    │
│  │    ├──→ Task 1: Verify result 1 (fact_checker)            │    │
│  │    ├──→ Task 2: Verify result 2 (fact_checker)            │    │
│  │    └──→ ... (all run in parallel)                          │    │
│  │                                                             │    │
│  │ wf.reduce_agent(verified, 'synthesizer')                   │    │
│  │    │                                                        │    │
│  │    └──→ Final Report (synthesizer)                        │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: RESULTS RETURNED TO USER                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  final_report = "### Executive Summary\n..."                       │
│                              │                                      │
│                              ▼                                      │
│  conversation.run() returns the report                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary: What You Write vs What the Agent Writes

| What | When | Who |
|------|------|-----|
| Sub-agents (web_searcher, fact_checker, synthesizer) | Once, ahead of time | You |
| Skill (orchestrator instructions) | Once, ahead of time | You |
| Parent agent (with tools + skill) | Once, ahead of time | You |
| The workflow script (angles, which sub-agents, how to aggregate) | Runtime, per task | **Agent** |

---

## The Key Insight

**You build the team and write the training manual.**
**The agent decides how to deploy them for each specific task.**

```python
# YOU write (setup, once):
- Sub-agent factories
- The orchestrator skill  
- The parent agent

# AGENT writes (runtime, per task):
- Which angles to research (based on skill + question)
- Which sub-agents to use when
- How many parallel tasks
- How to aggregate the results
```

This is what makes it "dynamic" — the same infrastructure works for any question, and the agent figures out the specifics each time.