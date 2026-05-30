#!/usr/bin/env python3
"""
Deep Research Workflow Demo

Inspired by Claude Code's /deep-research workflow.
This demonstrates parallel agent orchestration with fan-out/fan-in pattern.

Run:
    python deep_research.py "your research question"

Requirements:
    export OPENAI_API_KEY=sk-...  (or set LLM_API_KEY)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present (look in parent directory)
dotenv_path = Path(__file__).parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Add local SDK to path - use sdk-pr3426 from sibling directory
possible_paths = [
    Path(__file__).parent.parent / "sdk-pr3426",
    Path.home() / "Code" / "sdk-pr3426",
]

for sdk_path in possible_paths:
    if sdk_path.exists():
        sys.path.insert(0, str(sdk_path / "openhands-sdk"))
        sys.path.insert(0, str(sdk_path / "openhands-tools"))
        break

from openhands.sdk import LLM, Agent, AgentContext, Conversation, Tool
from openhands.sdk.context import Skill
from openhands.sdk.subagent import register_agent_if_absent
from openhands.tools.delegate import DelegationVisualizer
from openhands.tools.terminal import TerminalTool
from openhands.tools.workflow import WorkflowToolSet


def setup_llm():
    """Auto-detect available API keys."""
    api_key = (
        os.getenv("OPENAI_API_KEY") or
        os.getenv("LLM_API_KEY") or
        os.getenv("ANTHROPIC_API_KEY")
    )
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    if not api_key:
        print("❌ No API key found!")
        print("\nPlease set one of:")
        print("  export OPENAI_API_KEY=sk-...")
        print("  export LLM_API_KEY=your_key")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)
    
    return LLM(model=model, api_key=api_key, base_url=base_url)


def create_web_searcher(llm: LLM) -> Agent:
    """Sub-agent that searches the web for information."""
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name)],
        agent_context=AgentContext(
            skills=[
                Skill(
                    name="web_researcher",
                    content=(
                        "You are a thorough web researcher. Search for information about "
                        "the given topic. Use curl or wget to fetch relevant pages. "
                        "Extract key facts, statistics, and claims with sources. "
                        "Return findings with citations and confidence levels."
                    ),
                    trigger=None,
                )
            ],
            system_message_suffix="You cite sources for every claim.",
        ),
    )


def create_fact_checker(llm: LLM) -> Agent:
    """Sub-agent that cross-checks claims."""
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name)],
        agent_context=AgentContext(
            skills=[
                Skill(
                    name="fact_checker",
                    content=(
                        "You verify research claims against multiple sources. "
                        "For each claim, assess: (1) Fully Supported, "
                        "(2) Partially Supported, (3) Contradicted, "
                        "(4) Unverified. Return confidence scores and sources."
                    ),
                    trigger=None,
                )
            ],
            system_message_suffix="You are skeptical of strong claims without strong evidence.",
        ),
    )


def create_synthesizer(llm: LLM) -> Agent:
    """Sub-agent that creates the final report."""
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name)],
        agent_context=AgentContext(
            skills=[
                Skill(
                    name="research_synthesizer",
                    content=(
                        "You synthesize verified research into clear, well-structured reports. "
                        "Organize by theme, cite sources inline [source], "
                        "highlight key insights, flag areas of uncertainty."
                    ),
                    trigger=None,
                )
            ],
            system_message_suffix="You write clear research reports with proper citations.",
        ),
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python deep_research.py <research_question>")
        print("\nExample:")
        print("  python deep_research.py 'What are the latest developments in AI coding assistants?'")
        print("\nTip: Set OPENAI_API_KEY environment variable first.")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    llm = setup_llm()
    
    # Register sub-agents
    register_agent_if_absent("web_searcher", create_web_searcher, 
                            "Searches the web for information")
    register_agent_if_absent("fact_checker", create_fact_checker, 
                            "Cross-checks claims against sources")
    register_agent_if_absent("synthesizer", create_synthesizer, 
                            "Synthesizes research into reports")

    # Create parent agent with workflow tool
    parent_agent = Agent(
        llm=llm,
        tools=[Tool(name=WorkflowToolSet.name)],
        agent_context=AgentContext(
            skills=[
                Skill(
                    name="research_orchestrator",
                    content=(
                        "When asked to research a topic deeply, write a Python workflow: "
                        "(1) fan out web_searcher agents across multiple angles, "
                        "(2) use fact_checker to cross-check claims, "
                        "(3) use reduce_agent with synthesizer for final report."
                    ),
                    trigger=None,
                )
            ]
        ),
    )

    conversation = Conversation(
        agent=parent_agent,
        workspace=Path.cwd(),
        visualizer=DelegationVisualizer(name="DeepResearch"),
        max_iteration_per_run=10,
    )

    print(f"\n🔍 Deep Research: {question}")
    print("=" * 60)
    print("This will fan out multiple research agents in parallel...")
    print("=" * 60 + "\n")

    conversation.send_message(
        f"""Conduct deep research on: {question}

Use a parallel research workflow:

1. FAN OUT: Use wf.map_agents to send web_searcher agents across multiple angles:
   - Market overview and major players
   - Technical developments and innovations
   - Expert opinions and analysis
   - Statistics and data points
   - Debates, concerns, or counterarguments

2. CROSS-CHECK: Use fact_checker to verify key claims from multiple angles

3. SYNTHESIZE: Use wf.reduce_agent with synthesizer to create a final report with:
   - Executive summary (2-3 sentences)
   - Key findings with confidence scores
   - Sources cited inline [source_url]
   - Areas of uncertainty or conflicting views
   - Recommended next steps or further research

Return the full cited report."""
    )

    conversation.run()

    cost = conversation.conversation_stats.get_combined_metrics().accumulated_cost
    print(f"\n{'='*60}")
    print("✅ Research Complete!")
    print(f"{'='*60}")
    print(f"Question: {question}")
    print(f"Cost: ${cost:.4f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()