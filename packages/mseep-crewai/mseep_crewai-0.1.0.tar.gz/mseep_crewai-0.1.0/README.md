# Crewai Crew

Welcome to the Crewai Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/crewai/config/agents.yaml` to define your agents
- Modify `src/crewai/config/tasks.yaml` to define your tasks
- Modify `src/crewai/crew.py` to add your own logic, tools and specific args
- Modify `src/crewai/main.py` to add custom inputs for your agents and tasks

## Running the Project

### Sequential Crew

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the crewai Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

### Hierarchical Crew

This project also includes a hierarchical implementation where each agent is specialized in using a specific tool. To run the hierarchical crew:

```bash
$ hierarchical
```

or:

```bash
$ run_hierarchical
```

This will create a `hierarchical_result.md` file with the output from the hierarchical process.

Learn more about the hierarchical implementation in the [Hierarchical README](src/crewai/hierarchical/README.md).

## Model Control Protocol (MCP) Integration

This project includes an MCP server that exposes CrewAI tools through a REST API. This allows Claude and other LLMs to access and utilize CrewAI tools.

### Starting the MCP Server

```bash
$ start_mcp
```

Or you can run it directly:

```bash
$ python -m mcp.run_server
```

By default, the server runs on `0.0.0.0:8000`. You can customize this:

```bash
$ start_mcp --host 127.0.0.1 --port 9000
```

### Available MCP Tools

The MCP server provides access to the following tools:
- Custom CrewAI tools
- Web search functionality
- Data analysis capabilities

For more information, see the [MCP README](mcp/README.md).

## Understanding Your Crew

The crewai Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the Crewai Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.