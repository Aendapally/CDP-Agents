# CDP-Agents: Cloud Developer Platform Using AI Agents

A comprehensive toolkit for building AI agents specialized in Customer Developer Platform (CDP) architecture design and implementation, built on the Strands platform.

##  Overview

This project combines three powerful components:

- **Agent Development Toolkit (ADT)** - A CLI tool for building, testing, and iterating on AI agents
- **Architecture Design Agent** - A specialized AI agent for AWS architecture design with MCP integration
- **Diagrams-as-Code** - A declarative YAML-based system for generating cloud architecture diagrams

## 📁 Project Structure

```
CDP-Agents/
├── adt-readme.md                    # ADT documentation
├── arch-design/                     # Architecture Design Agent
│   ├── src/
│   │   ├── agent.py                # Main agent implementation
│   │   ├── tools/                  # Custom tools for architecture design
│   │   │   ├── architecture_orchestrator.py
│   │   │   ├── aws_architecture_designer.py
│   │   │   ├── architecture_to_yaml.py     # Text → YAML (LLM-driven relationships)
│   │   │   ├── yaml_to_diagram.py          # YAML → PNG rendering
│   │   │   ├── tfstate_to_diagram.py       # Terraform state → diagram
│   │   │   ├── diagrams_as_code_reference.py
│   │   │   └── ...
│   │   ├── mcp_client.py           # MCP integration
│   │   └── mcp_tools.py            # MCP tool loader
│   ├── test_data/                   # Sample tfstate files for testing
│   ├── .agent.yaml                 # Agent configuration
│   ├── requirements.txt            # Python dependencies
│   └── README.md                   # Agent-specific documentation
├── diagrams-as-code/               # Diagrams-as-Code library
│   ├── examples/                   # Example YAML configurations
│   ├── docs/                       # Documentation
│   └── ...
└── ref.yaml                        # Reference configuration
```

##  Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for UI assets)
- Graphviz (`brew install graphviz` on macOS)
- Docker (optional — required for container mode and Terraform MCP server)
- AWS credentials configured (for Bedrock LLM and optionally S3 tfstate access)

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/Aendapally/CDP-Agents
cd CDP-Agents

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install ADT
pip install git+https://github.com/awslabs/agent-dev-toolkit.git
```

### 2. Run the Architecture Design Agent

```bash
# Navigate to the agent directory
cd arch-design

# Install dependencies
pip install -r requirements.txt

# Set up AWS credentials (choose one method)
# Method 1: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2

# Method 2: AWS profile
# adt dev --aws-profile your-profile-name

# Method 3: Environment file
# Create .env file with your credentials
# adt dev --env-file .env

# Start the development server
adt dev --port 8083
```

Visit http://localhost:8083 to interact with the Architecture Design Agent.

##  Architecture Design Agent

The Architecture Design Agent is a specialized AI agent that helps design AWS architectures through a sophisticated workflow:

### Core Workflow

1. **Requirements Analysis** - Analyzes initial requirements and identifies AWS components
2. **AWS Component Analysis** - Queries AWS documentation for detailed service capabilities
3. **Progressive Questioning** - Generates targeted questions for both application and infrastructure needs
4. **Architecture Design** - Creates comprehensive AWS architectures following the Well-Architected Framework
5. **Diagram Generation** - Converts architectures to visual diagrams using YAML specifications

### Key Features

- **AWS Documentation Integration** - Real-time access to AWS service information via MCP
- **Progressive Refinement** - Starts broad, then drills down to specific configurations
- **Well-Architected Framework** - Ensures security, reliability, performance, cost optimization, and operational excellence
- **Diagrams-as-Code** - Generates visual architecture diagrams from YAML specifications
- **Implementation-Ready Designs** - Provides specific configurations, not just high-level concepts

### Available Tools

- `analyze_and_question` - Identifies AWS components and generates targeted questions
- `finalize_architecture` - Creates final design with detailed user answers
- `convert_architecture_to_yaml` - Converts architecture design to diagrams-as-code YAML (LLM-driven relationships by default)
- `generate_diagram_from_yaml` - Creates visual AWS diagrams from YAML specifications
- `validate_yaml_schema` - Validates YAML against diagrams-as-code schema
- `read_tfstate` - Reads a Terraform state file (local or S3) and returns a resource summary
- `tfstate_to_diagram` - Generates an architecture diagram (YAML + PNG) from a Terraform state file

## Terraform State to Diagram

Generate architecture diagrams directly from your Terraform `.tfstate` files — no manual drawing required.

### How It Works

```
.tfstate (JSON) → Parse Resources → Map to Diagram Types → Infer Relationships → YAML + PNG
```

1. **Parse** — Reads the `.tfstate` JSON and extracts managed resources, skipping infrastructure plumbing (subnets, security groups, IAM policies, etc.)
2. **Map** — Looks up each Terraform resource type against a 120+ entry mapping table to find the corresponding `diagrams` library icon (e.g. `aws_lambda_function` → `aws.compute.Lambda`)
3. **Infer Relationships** — Uses ARN-based lookups and architectural patterns to connect resources (e.g. API Gateway → Lambda, ALB → ECS, SNS → SQS)
4. **Generate** — Produces a diagrams-as-code YAML file and renders a PNG using Graphviz
```

### LLM-Enhanced Mode

When `enhance_with_llm='true'`, the tool runs the deterministic pass first, then sends the resource list and auto-inferred relationships to the LLM (via Bedrock) for review. The LLM can add missing connections, remove incorrect ones, and improve labels. Requires AWS Bedrock credentials.

```python
result = tfstate_to_diagram(
    source='path/to/terraform.tfstate',
    diagram_name='My Infrastructure',
    output_folder='output',
    enhance_with_llm='true'
)
```

### Filtering Resources

Include or exclude specific Terraform resource types:

```python
result = tfstate_to_diagram(
    source='terraform.tfstate',
    diagram_name='Compute Only',
    include_types='aws_lambda_function,aws_ecs_cluster,aws_ecs_service',
)

result = tfstate_to_diagram(
    source='terraform.tfstate',
    diagram_name='No Monitoring',
    exclude_types='aws_cloudwatch_log_group,aws_cloudwatch_metric_alarm',
)
```

##  Diagrams-as-Code

The project includes a comprehensive diagrams-as-code library for generating cloud architecture diagrams:

### Features

- **Declarative YAML Configuration** - Define architectures using simple YAML syntax
- **Multi-Cloud Support** - AWS, Azure, GCP, IBM, Alibaba, Oracle, and more
- **Version Control Friendly** - Track architecture changes with Git
- **Collaborative** - Update architectures through pull requests
- **Consistent** - Maintains consistency across documentation

### Example Usage

```yaml
diagram:
  name: Web Services Architecture on AWS
  file_name: web-services-architecture-aws
  format: png
  direction: left-to-right
  resources:
    - id: elb
      name: ELB
      type: aws.network.ELB
      relates:
        - to: web-services
          direction: outgoing
    - id: web-services
      name: Web Services
      type: cluster
      of:
        - id: api
          name: API Gateway
          type: aws.network.APIGateway
```

##  Configuration

### Agent Configuration (`.agent.yaml`)

The agent is configured through a single YAML file:

```yaml
name: arch_design-agent
system_prompt: |
  You are an AWS Architecture Design Specialist Agent...

provider:
  class: "strands.models.BedrockModel"
  kwargs:
    model_id: "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    region_name: "us-west-2"
    temperature: 0.3

mcp_servers:
  - name: aws_documentation
    transport: stdio
    command: ["uvx", "awslabs.aws-documentation-mcp-server@latest"]
```

### Environment Variables

Create a `.env` file with your credentials:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
```

##  Development

### Adding Custom Tools

```bash
# Generate a new tool template
adt add tool my_tool_name

# This creates src/tools/my_tool_name.py with a template
```

### Running in Container Mode

```bash
# Run backend in Docker container
adt dev --container --port 9000

# Force rebuild after dependency changes
adt dev --container --rebuild --port 9000
```

### MCP Integration

The agent supports Model Context Protocol (MCP) for extending capabilities:

```bash
# Install MCP dependencies
pip install mcp uv
```

##  Documentation

- [ADT Documentation](adt-readme.md) - Complete Agent Development Toolkit guide
- [Architecture Agent README](arch-design/README.md) - Agent-specific documentation
- [Diagrams-as-Code README](diagrams-as-code/README.md) - Diagrams library documentation

##  Contributing - Need to make this public once approved

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/CDP-Agents/issues)
- **Documentation**: [Strands Documentation](https://strandsagents.com/latest/)
- **MCP Protocol**: [Model Context Protocol](https://github.com/modelcontextprotocol)

## Acknowledgments

- Built on the [Strands platform](https://strandsagents.com/)
- Uses [diagrams-as-code](https://github.com/dmytrostriletskyi/diagrams-as-code) for diagram generation
- Uses [diagrams](https://github.com/mingrammer/diagrams) (Graphviz) for PNG rendering
- Integrates with [AWS Documentation MCP Server](https://github.com/awslabs/aws-documentation-mcp-server)
- Integrates with [Terraform MCP Server](https://github.com/hashicorp/terraform-mcp-server)

---

**Made for the CDP and AI agent ecosystem**
