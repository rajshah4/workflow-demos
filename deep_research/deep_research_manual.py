"""
Deep Research: Manual Orchestration (THE OLD WAY)
=================================================

This is what building multi-agent systems looks like TODAY.
You write the loop. You control the orchestration.

Notice how much code YOU have to write just to coordinate agents.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add SDK to path
SDK_PATH = Path(__file__).parent.parent / "sdk-pr3426"
sys.path.insert(0, str(SDK_PATH / "openhands-sdk"))
sys.path.insert(0, str(SDK_PATH / "openhands-tools"))

from dotenv import load_dotenv
from openhands.sdk import LLM, Agent, AgentContext, Conversation
from openhands.sdk.conversation.impl.local_conversation import LocalConversation
from openhands.sdk.subagent import register_agent_if_absent

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")

# Initialize LLM
llm = LLM(model="gpt-4o-mini")

# ============================================================
# STEP 1: Define your sub-agents (YOU write these)
# ============================================================

def create_research_agent(llm: LLM) -> Agent:
    """Factory for research agents."""
    return Agent(
        llm=llm,
        agent_context=AgentContext(
            system_message="You are a web researcher. Search for information and cite sources."
        )
    )

def create_fact_checker(llm: LLM) -> Agent:
    """Factory for fact-checking agents."""
    return Agent(
        llm=llm,
        agent_context=AgentContext(
            system_message="You verify claims by cross-referencing sources. Be skeptical."
        )
    )

def create_synthesizer(llm: LLM) -> Agent:
    """Factory for synthesis agents."""
    return Agent(
        llm=llm,
        agent_context=AgentContext(
            system_message="You synthesize research into clear reports with citations."
        )
    )

# Register the sub-agent types
register_agent_if_absent("researcher", create_research_agent, "Web research agent")
register_agent_if_absent("fact_checker", create_fact_checker, "Fact checking agent")
register_agent_if_absent("synthesizer", create_synthesizer, "Synthesis agent")


# ============================================================
# STEP 2: Define your research angles (YOU decide these)
# ============================================================

RESEARCH_ANGLES = [
    "Market overview and major players (GitHub Copilot, Tabnine, etc.)",
    "Technical developments and AI capabilities",
    "Expert opinions and industry analysis",
    "Statistics and market size data",
    "Concerns, debates, or counterarguments"
]

VERIFICATION_PROMPTS = [
    "Verify this market data: {result}",
    "Check these statistics: {result}",
    "Validate this expert opinion: {result}"
]


# ============================================================
# STEP 3: YOU write the orchestration logic
# ============================================================
# This is the part that's always the same across projects.
# The only thing that changes is the prompts and the agents.
# YOU are the orchestrator here.

def run_research_sync(question: str) -> dict:
    """
    Manual orchestration of the research workflow.
    
    Notice all the code YOU have to write:
    - Creating conversations
    - Managing state
    - Running things in sequence or manually in parallel
    - Aggregating results
    
    This is 40+ lines of boilerplate that you repeat for every project.
    """
    
    print(f"\n🔍 MANUAL ORCHESTRATION: {question}")
    print("=" * 60)
    print("You are the orchestrator. The agent is just a worker.")
    print()
    
    # Track timing
    import time
    start_time = time.time()
    
    # ---- PHASE 1: Parallel Research ----
    # YOU have to manage the parallel execution
    print("📡 Phase 1: Running research agents in parallel...")
    print("   (YOU have to write the loop)")
    
    research_results = []
    
    # This is the loop YOU write
    for i, angle in enumerate(RESEARCH_ANGLES):
        print(f"   Starting researcher {i+1}/{len(RESEARCH_ANGLES)}: {angle[:50]}...")
        
        # YOU create the conversation
        research_agent = create_research_agent(llm)
        conv = LocalConversation(
            agent=research_agent,
            workspace="/tmp/research-workspace"
        )
        
        # YOU send the message
        conv.send_message(
            f"For the question: '{question}', research this angle: {angle}\n"
            f"Provide detailed findings with sources."
        )
        
        # YOU run it
        conv.run()
        
        # YOU extract the result
        result = conv.state.events[-1].content if conv.state.events else "No result"
        research_results.append(result)
        conv.close()
        
        print(f"   ✓ Researcher {i+1} complete")
    
    print(f"   All {len(RESEARCH_ANGLES)} research agents done")
    print()
    
    # ---- PHASE 2: Verification ----
    # YOU manage another parallel phase
    print("✓ Phase 2: Running fact-checkers...")
    print("   (YOU have to write another loop)")
    
    verified_results = []
    
    # Another loop YOU write
    for i, (angle, result) in enumerate(zip(RESEARCH_ANGLES, research_results)):
        print(f"   Checking angle {i+1}/{len(RESEARCH_ANGLES)}...")
        
        checker_agent = create_fact_checker(llm)
        conv = LocalConversation(
            agent=checker_agent,
            workspace="/tmp/research-workspace"
        )
        
        conv.send_message(
            f"Verify and cross-check this research:\n\nAngle: {angle}\n\nFindings: {result[:500]}...\n\n"
            f"Is this accurate? Mark any claims that need verification."
        )
        
        conv.run()
        verified = conv.state.events[-1].content if conv.state.events else "Verification failed"
        verified_results.append(f"[From {angle}]: {verified}")
        conv.close()
    
    print(f"   All {len(RESEARCH_ANGLES)} fact-checkers done")
    print()
    
    # ---- PHASE 3: Synthesis ----
    # YOU aggregate everything manually
    print("📝 Phase 3: Synthesizing final report...")
    print("   (YOU have to combine the results)")
    
    synth_agent = create_synthesizer(llm)
    synth_conv = LocalConversation(
        agent=synth_agent,
        workspace="/tmp/research-workspace"
    )
    
    # YOU format the prompt
    combined_results = "\n\n".join([
        f"## {angle}\n{result[:300]}..."
        for angle, result in zip(RESEARCH_ANGLES, verified_results)
    ])
    
    # YOU send the message
    synth_conv.send_message(
        f"Create a comprehensive report answering: '{question}'\n\n"
        f"Use the following verified research:\n\n{combined_results}\n\n"
        f"Format with: Executive Summary, Key Findings, Sources, Areas of Uncertainty, Next Steps."
    )
    
    # YOU run it
    synth_conv.run()
    
    # YOU extract the final result
    final_report = synth_conv.state.events[-1].content if synth_conv.state.events else "Synthesis failed"
    synth_conv.close()
    
    total_time = time.time() - start_time
    
    print()
    print("=" * 60)
    print("✅ MANUAL ORCHESTRATION COMPLETE")
    print("=" * 60)
    print(f"Time: {total_time:.2f}s")
    print()
    
    return {
        "question": question,
        "angles": RESEARCH_ANGLES,
        "research_results": research_results,
        "verified_results": verified_results,
        "final_report": final_report,
        "total_time": total_time
    }


def print_report(report: dict):
    """Pretty print the final report."""
    print("\n" + "=" * 60)
    print("📊 FINAL REPORT (Generated via manual orchestration)")
    print("=" * 60)
    print()
    print(report["final_report"])
    print()
    print(f"Generated in {report['total_time']:.2f}s with {len(report['angles'])} research angles.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What is the AI coding assistant market size in 2024?"
    
    report = run_research_sync(question)
    print_report(report)