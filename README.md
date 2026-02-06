# Datagent (Avaloka AI)

Datagent is a production-grade, CLI-driven, multi-agent framework for data science, machine learning, and foundation model workflows.

## Features
- **CLI-First**: Manage sessions and workflows via terminal.
- **YAML Workflows**: Define agent interactions in declarative YAML.
- **Strict Typing**: Built on Pydantic and immutable dataclasses.
- **Distributed**: Native support for Ray and Kubernetes.
- **RAG Integration**: Built-in pipelines for code generation and knowledge retrieval.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run a Workflow
```bash
python -m datagent.cli run workflows/training_workflow.yaml
```

### Start Backend
```bash
uvicorn app.backend.main:app --reload
```

## Directory Structure
- `module/datagent/core`: Core engine (Graph Compiler, Executor).
- `module/datagent/agents`: Specialized agents (Planner, CodeGen, Validator).
- `module/datagent/rag`: Retrieval Augmented Generation components.
- `deployments/`: Kubernetes and Docker manifests.
