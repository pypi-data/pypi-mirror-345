# Fabric MCP Server

**Connect the power of the Fabric AI framework to any Model Context Protocol (MCP) compatible application.**

This project implements a standalone server that bridges the gap between [Daniel Miessler's Fabric framework][fabricGithubLink] and the [Model Context Protocol (MCP)][MCP]. It allows you to use Fabric's patterns, models, and configurations directly within MCP-enabled environments like IDE extensions or chat interfaces.

Imagine seamlessly using Fabric's specialized prompts for code explanation, refactoring, or creative writing right inside your favorite tools!

## Table of Contents

- [Fabric MCP Server](#fabric-mcp-server)
  - [Table of Contents](#table-of-contents)
  - [What is this?](#what-is-this)
  - [Key Goals \& Features (Based on Design)](#key-goals--features-based-on-design)
  - [How it Works](#how-it-works)
  - [Project Status](#project-status)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
      - [From Source (for Development)](#from-source-for-development)
      - [From PyPI (for Users)](#from-pypi-for-users)
  - [Contributing](#contributing)
  - [License](#license)


## What is this?

- **Fabric:** An open-source framework for augmenting human capabilities using AI, focusing on prompt engineering and modular AI workflows.
- **MCP:** An open standard protocol enabling AI applications (like IDEs) to securely interact with external tools and data sources (like this server).
- **Fabric MCP Server:** This project acts as an MCP server, translating MCP requests into calls to a running Fabric instance's REST API (`fabric --serve`).

## Key Goals & Features (Based on Design)

- **Seamless Integration:** Use Fabric patterns and capabilities directly within MCP clients without switching context.
- **Enhanced Workflows:** Empower LLMs within IDEs or other tools to leverage Fabric's specialized prompts and user configurations.
- **Standardization:** Adhere to the open MCP standard for AI tool integration.
- **Leverage Fabric Core:** Build upon the existing Fabric CLI and REST API without modifying the core Fabric codebase.
- **Expose Fabric Functionality:** Provide MCP tools to list patterns, get pattern details, run patterns, list models/strategies, and retrieve configuration.

## How it Works

1. An **MCP Host** (e.g., an IDE extension) connects to this **Fabric MCP Server**.
2. The Host discovers available tools (like `fabric_run_pattern`) via MCP's `list_tools()` mechanism.
3. When the user invokes a tool (e.g., asking the IDE's AI assistant to refactor code using a Fabric pattern), the Host sends an MCP request to this server.
4. The **Fabric MCP Server** translates the MCP request into a corresponding REST API call to a running `fabric --serve` instance.
5. The `fabric --serve` instance processes the request (e.g., executes the pattern).
6. The **Fabric MCP Server** receives the response (potentially streaming) from Fabric and translates it back into an MCP response for the Host.

## Project Status

This project is currently in the **design phase**. The core architecture and proposed tools are outlined in the [High-Level Design Document](./docs/design.md).

**Next Steps:**

- Select implementation language (Go/Python) and MCP library.
- Implement the standalone MCP server.
- Define detailed handling for streaming, variables, attachments, and errors.
- Gather community feedback.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) (Python package and environment manager)

### Installation

#### From Source (for Development)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ksylvan/fabric-mcp.git
   cd fabric-mcp
   ```

2. **Install dependencies using uv sync:**

   ```bash
   uv sync --dev
   ```

   This command ensures your virtual environment matches the dependencies in `pyproject.toml` and `uv.lock`, creating the environment on the first run if necessary.

3. **Activate the virtual environment (uv will create it if needed):**

   - On macOS/Linux:

     ```bash
     source .venv/bin/activate
     ```

   - On Windows:

     ```bash
     .venv\Scripts\activate
     ```

Now you have the development environment set up!

#### From PyPI (for Users)

If you just want to use the `fabric-mcp` server without developing it, you can install it directly from PyPI:

```bash
# Using pip
pip install fabric-mcp

# Or using uv
uv pip install fabric-mcp
```

This will install the package and its dependencies. You can then run the server using the `fabric-mcp` command.

## Contributing

Feedback on the [design document](./docs/design.md) is highly welcome! Please open an issue to share your thoughts or suggestions.

Read the [contribution document here](./docs/contributing.md) and please follow the guidelines for this repository.

## License

Copyright (c) 2025, [Kayvan Sylvan](kayvan@sylvan.com) Licensed under the [MIT License](./LICENSE).

[fabricGithubLink]: https://github.com/danielmiessler/fabric
[MCP]: https://modelcontextprotocol.io/
