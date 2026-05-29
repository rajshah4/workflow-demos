#!/usr/bin/env python3
"""
Multi-Expert Code Review Demo

Parallel specialized reviewers with synthesis.
Demonstrates fan-out/fan-in pattern for code review.

Run:
    python multi_expert_review.py [file_path]

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

# Add SDK to path - try multiple locations
possible_paths = [
    Path(__file__).parent.parent / "sdk-demo",
    Path.home() / "Code" / "sdk-demo",
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
from openhands.tools.file_editor import FileEditorTool
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


def create_security_reviewer(llm: LLM) -> Agent:
    """Reviews code for security vulnerabilities."""
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name), Tool(name=FileEditorTool.name)],
        agent_context=AgentContext(
            skills=[
                Skill(
                    name="security_review",
                    content=(
                        "You are a security expert. Review code for: "
                        "SQL injection, XSS, auth bypass, secret leaks, "
                        "insecure dependencies, race conditions, input validation. "
                        "Check git diffs and file contents. "
                        "Report specific vulnerabilities with severity "
                        "(Critical/High/Medium/Low) and line references."
                    ),
                    trigger=None,
                )
            ],
            system_message_suffix="Focus on security. Do not modify code.",
        ),
    )


def create_performance_reviewer(llm: LLM) -> Agent:
    """Reviews code for performance issues."""
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name), Tool(name=FileEditorTool.name)],
        agent_context=AgentContext(
            skills=[
                Skill(
                    name="performance_review",
                    content=(
                        "You are a performance analyst. Review code for: "
                        "N+1 queries, memory leaks, O(n²) algorithms, "
                        "missing indexes, large data loading, blocking operations. "
                        "Check for inefficient patterns and suggest optimizations "
                        "with approximate speedup estimates."
                    ),
                    trigger=None,
                )
            ],
            system_message_suffix="Focus on performance. Do not modify code.",
        ),
    )


def create_style_reviewer(llm: LLM) -> Agent:
    """Reviews code for style and maintainability."""
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name), Tool(name=FileEditorTool.name)],
        agent_context=AgentContext(
            skills=[
                Skill(
                    name="style_review",
                    content=(
                        "You are a code style expert. Review for: "
                        "naming conventions, documentation gaps, error handling patterns, "
                        "type hints, consistent imports, code smells. "
                        "Check against common style guides. "
                        "Report issues with specific fixes."
                    ),
                    trigger=None,
                )
            ],
            system_message_suffix="Focus on quality. Do not modify code.",
        ),
    )


def create_test_reviewer(llm: LLM) -> Agent:
    """Reviews code for test coverage."""
    return Agent(
        llm=llm,
        tools=[Tool(name=TerminalTool.name), Tool(name=FileEditorTool.name)],
        agent_context=AgentContext(
            skills=[
                Skill(
                    name="test_review",
                    content=(
                        "You are a testing expert. Review for: "
                        "missing test cases, edge cases not covered, "
                        "integration vs unit test balance, mocking correctness, "
                        "testability of the code. "
                        "Check existing tests and suggest specific new tests."
                    ),
                    trigger=None,
                )
            ],
            system_message_suffix="Focus on testing. Do not modify code.",
        ),
    )


def main():
    # Default to SDK example file if no argument given
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        # Use an example from the SDK
        SDK_PATH = Path(__file__).parent.parent / "sdk-demo"
        if SDK_PATH.exists():
            target = str(SDK_PATH / "examples/01_standalone_sdk/02_custom_tools.py")
        else:
            print("Usage: python multi_expert_review.py <file_path>")
            print("No file specified and SDK not found.")
            sys.exit(1)

    if not Path(target).exists():
        print(f"❌ File not found: {target}")
        sys.exit(1)

    llm = setup_llm()

    # Register reviewer sub-agents
    register_agent_if_absent("security_reviewer", create_security_reviewer,
                            "Reviews code for security vulnerabilities")
    register_agent_if_absent("performance_reviewer", create_performance_reviewer,
                            "Reviews code for performance issues")
    register_agent_if_absent("style_reviewer", create_style_reviewer,
                            "Reviews code for style and maintainability")
    register_agent_if_absent("test_reviewer", create_test_reviewer,
                            "Reviews code for test coverage")

    # Create parent agent with workflow tool
    parent_agent = Agent(
        llm=llm,
        tools=[Tool(name=WorkflowToolSet.name)],
        agent_context=AgentContext(
            skills=[
                Skill(
                    name="review_orchestrator",
                    content=(
                        "When asked to review code, write a Python workflow that uses "
                        "wf.map_agents to fan out specialized reviewers in parallel. "
                        "Use wf.reduce_agent to synthesize findings into a prioritized report."
                    ),
                    trigger=None,
                )
            ]
        ),
    )

    conversation = Conversation(
        agent=parent_agent,
        workspace=Path.cwd(),
        visualizer=DelegationVisualizer(name="MultiExpertReview"),
        max_iteration_per_run=8,
    )

    print(f"\n👥 Multi-Expert Code Review: {target}")
    print("=" * 60)
    print("This will run 4 specialized reviewers in parallel:")
    print("  🔒 Security  |  ⚡ Performance  |  🎨 Style  |  🧪 Testing")
    print("=" * 60 + "\n")

    conversation.send_message(
        f"""Review the code at {target} using a multi-expert parallel review workflow.

Run these reviewers in parallel using wf.map_agents:
1. security_reviewer - Check for security vulnerabilities
2. performance_reviewer - Check for performance issues  
3. style_reviewer - Check for style/maintainability issues
4. test_reviewer - Check for test coverage gaps

Each reviewer should:
- Read the relevant code
- Report their specific findings
- Use maximum 3 tool calls (be efficient)

Then use wf.reduce_agent with security_reviewer to synthesize into a final report:

## Code Review Report

### 🔴 Critical Issues (fix immediately)
### 🟠 High Priority (fix soon)
### 🟡 Medium/Low Priority
### ✅ Positive Findings

For each issue include:
- What: brief description
- Where: file/line reference
- Why: why it matters
- Fix: suggested solution

Return the prioritized report."""
    )

    conversation.run()

    cost = conversation.conversation_stats.get_combined_metrics().accumulated_cost
    print(f"\n{'='*60}")
    print("✅ Review Complete!")
    print(f"{'='*60}")
    print(f"File: {target}")
    print(f"Cost: ${cost:.4f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()