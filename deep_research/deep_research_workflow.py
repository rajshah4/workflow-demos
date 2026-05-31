"""
Deep Research: Agent-Written Orchestration (THE NEW WAY)
=======================================================

This is what building multi-agent systems looks like WITH workflows.
The AGENT writes the orchestration loop. You just give it the objective.

Notice: YOU only write the setup. The agent writes the orchestration.
"""

import os
import sys
from pathlib import Path

# Add SDK to path
SDK_PATH = Path(__file__).parent.parent / "sdk-pr3426"
sys.path.insert(0, str(SDK_PATH / "openhands-sdk"))
sys.path.insert(0, str(SDK_PATH / "openhands-tools"))

from dotenv import load_dotenv
from openhands.sdk import LLM, Agent, AgentContext, Conversation
from openhands.sdk.subagent import register_agent_if_absent
from openhands.tools.workflow import WorkflowToolSet, Tool

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")

# ============================================================
# STEP 1: Define your sub-agents (ONLY once)
# ============================================================

def create_web_searcher(llm: LLM) -> Agent:
    """Factory for web search agents."""
    return Agent(
        llm=llm,
        agent_context=AgentContext(
            system_message="You are a thorough web researcher. Search for information and cite sources for every claim."
        )
    )

def create_fact_checker(llm: LLM) -> Agent:
    """Factory for fact-checking agents."""
    return Agent(
        llm=llm,
        agent_context=AgentContext(
            system_message="You verify claims by cross-referencing sources. Be skeptical and flag uncertain claims."
        )
    )

def create_synthesizer(llm: LLM) -> Agent:
    """Factory for synthesis agents."""
    return Agent(
        llm=llm,
        agent_context=AgentContext(
            system_message="You synthesize research into clear, well-structured reports with proper citations."
        )
    )

# Register the sub-agent types (ONLY once, not in the workflow)
register_agent_if_absent("web_searcher", create_web_searcher, "Searches the web")
register_agent_if_absent("fact_checker", create_fact_checker, "Cross-checks claims")
register_agent_if_absent("synthesizer", create_synthesizer, "Creates reports")


# ============================================================
# STEP 2: Create the parent agent with the workflow tool
# ============================================================

parent_agent = Agent(
    llm=LLM(model="gpt-4o-mini"),
    tools=[Tool(name=WorkflowToolSet.name)],  # <-- THE MAGIC
    agent_context=AgentContext(
        system_message="You are OpenHands, a helpful AI assistant.",
        skills=[]  # We let the agent figure out when to use the workflow
    )
)


# ============================================================
# THE CONTRAST
# ============================================================
"""
Compare this to deep_research_manual.py:

OLD WAY (manual orchestration):
    - You create conversations
    - You write the loops
    - You manage state
    - You aggregate results
    - 100+ lines of orchestration code

NEW WAY (agent-written orchestration):
    - You create the parent agent with the workflow tool
    - You send the task
    - The agent decides to write a workflow
    - The agent calls wf.map_agents(), wf.reduce_agent()
    - 12 lines of setup code
"""

def run_with_workflow(question: str):
    """
    Run research using agent-written workflows.
    
    YOU only write:
        - The setup (parent agent + workflow tool)
        - The initial message
    
    THE AGENT writes:
        - The orchestration loop
        - Which sub-agents to use
        - How to aggregate results
    """
    
    print(f"\n🔍 WORKFLOW ORCHESTRATION: {question}")
    print("=" * 60)
    print("The agent is the orchestrator. YOU just give the objective.")
    print()
    
    # ---- THIS IS ALL YOU WRITE ----
    
    conversation = Conversation(agent=parent_agent)
    conversation.send_message(
        f"Research '{question}' deeply from multiple angles.\n\n"
        f"Use the workflow tool to:\n"
        f"1. Fan out research to multiple web searcher agents in parallel\n"
        f"2. Cross-check findings with fact-checker agents\n"
        f"3. Synthesize everything into a final report\n\n"
        f"Make sure to include: Executive Summary, Key Findings, Sources, "
        f"Areas of Uncertainty, and Next Steps."
    )
    
    # The agent will:
    # 1. Decide to use the workflow tool
    # 2. Write an async workflow script
    # 3. Execute it (creating sub-agents, running them, aggregating)
    
    result = conversation.run()
    
    print()
    print("=" * 60)
    print("✅ WORKFLOW ORCHESTRATION COMPLETE")
    print("=" * 60)
    print()
    print("The agent wrote the orchestration code!")
    print("It decided how many research angles, which sub-agents to use,")
    print("and how to structure the final report.")
    
    return result


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What is the AI coding assistant market size in 2024?"
    
    result = run_with_workflow(question)
    print()
    print("=" * 60)
    print("📊 FINAL REPORT (Generated via agent-written orchestration)")
    print("=" * 60)
    print()
    print(result)