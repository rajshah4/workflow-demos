FROM python:3.12-slim
WORKDIR /app

# Install git and dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Copy workflow-demos files
COPY deep_research/ /app/deep_research/
COPY multi_expert_review/ /app/multi_expert_review/
COPY .env /app/.env

ENV PYTHONPATH=/app/sdk/openhands-sdk:/app/sdk/openhands-tools

# Clone the SDK with workflow feature
RUN git clone --branch redo-dynamic-workflow-mvp --depth 1 https://github.com/OpenHands/software-agent-sdk.git /app/sdk

# Install uv and all dependencies from the SDK's pyproject.toml
RUN pip install uv && \
    cd /app/sdk && \
    uv pip install --system -e openhands-sdk/ && \
    uv pip install --system -e openhands-tools/ && \
    uv pip install --system python-dotenv

# Default: run the workflow version (NEW WAY)
CMD ["python3", "deep_research/deep_research_workflow.py"]