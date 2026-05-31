#!/usr/bin/env python3
"""
Multi-Expert Code Review Demo - MANUAL VERSION (OLD WAY)

This is the OLD WAY to do multi-expert review.
Compare to multi_expert_review.py (NEW WAY with workflows).

Run:
    python multi_expert_review_manual.py [file_path]

Requirements:
    export OPENAI_API_KEY=sk-...
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

from openhands.sdk import LLM, Agent, AgentContext, Conversation
from openhands.sdk.tool.spec import Tool
from openhands.tools.terminal import TerminalTool
from openhands.tools.file_editor import FileEditorTool


def setup_llm():
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    if not api_key:
        print("No API key found!")
        sys.exit(1)
    
    return LLM(model=model, api_key=api_key, base_url=base_url)


def create_reviewer(llm: LLM, specialty: str, instructions: str) -> Agent:
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name), Tool(name=FileEditorTool.name)],
        agent_context=AgentContext(
            system_message=f"You are a {specialty} expert. {instructions}"
        )
    )


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not target:
        home_sdk = Path.home() / "Code" / "software-agent-sdk"
        if home_sdk.exists():
            target = str(home_sdk / "examples/01_standalone_sdk/02_custom_tools.py")
        else:
            print("Usage: python multi_expert_review_manual.py <file_path>")
            sys.exit(1)
    
    if not Path(target).exists():
        print(f"File not found: {target}")
        sys.exit(1)
    
    llm = setup_llm()
    
    print(f"\nMulti-Expert Code Review (MANUAL): {target}")
    print("=" * 60)
    print("OLD WAY: You write the orchestration loops")
    print("=" * 60 + "\n")
    
    # YOU define the reviewers
    reviewers = [
        ("security", "Check for security vulnerabilities (SQL injection, XSS, auth bypass)"),
        ("performance", "Check for performance issues (N+1 queries, memory leaks)"),
        ("style", "Check for style/maintainability issues"),
        ("tests", "Check for test coverage gaps"),
    ]
    
    # YOU create the results list
    all_results = []
    
    # YOU write the loop - Sequential!
    print("Running security review...")
    security_agent = create_reviewer(llm, "security", reviewers[0][1])
    security_conv = Conversation(agent=security_agent, workspace=Path.cwd())
    security_conv.send_message(f"Review {target} for security issues.")
    security_conv.run()
    security_result = security_conv.state.events[-1].content
    all_results.append(("Security", security_result))
    security_conv.close()
    
    print("Running performance review...")
    perf_agent = create_reviewer(llm, "performance", reviewers[1][1])
    perf_conv = Conversation(agent=perf_agent, workspace=Path.cwd())
    perf_conv.send_message(f"Review {target} for performance issues.")
    perf_conv.run()
    perf_result = perf_conv.state.events[-1].content
    all_results.append(("Performance", perf_result))
    perf_conv.close()
    
    print("Running style review...")
    style_agent = create_reviewer(llm, "style", reviewers[2][1])
    style_conv = Conversation(agent=style_agent, workspace=Path.cwd())
    style_conv.send_message(f"Review {target} for style issues.")
    style_conv.run()
    style_result = style_conv.state.events[-1].content
    all_results.append(("Style", style_result))
    style_conv.close()
    
    print("Running test review...")
    test_agent = create_reviewer(llm, "tests", reviewers[3][1])
    test_conv = Conversation(agent=test_agent, workspace=Path.cwd())
    test_conv.send_message(f"Review {target} for test coverage.")
    test_conv.run()
    test_result = test_conv.state.events[-1].content
    all_results.append(("Tests", test_result))
    test_conv.close()
    
    # YOU aggregate manually
    print("\nSynthesizing results...")
    synthesizer = Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name)],
        agent_context=AgentContext(
            system_message="You synthesize multiple review findings into a prioritized report."
        )
    )
    synth_conv = Conversation(agent=synthesizer, workspace=Path.cwd())
    synth_conv.send_message(f"""Combine these reviews into a prioritized report:

{chr(10).join(f'## {name} Findings:\\n{result}' for name, result in all_results)}

Format as:
## Code Review Report

### Critical Issues
### High Priority
### Medium/Low Priority
### Positive Findings
""")
    synth_conv.run()
    
    print(f"\n{'='*60}")
    print("Review Complete!")
    print(f"File: {target}")
    print("Note: This took 4 sequential runs (OLD WAY)")
    print("NEW WAY uses workflows: python multi_expert_review.py")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
