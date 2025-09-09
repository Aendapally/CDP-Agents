from strands import tool


@tool
def analyze_and_question(user_requirements: str) -> str:
    """
    Orchestrates the architecture design workflow by first identifying AWS components, 
    then generating application and infrastructure questions.
    
    This tool follows the complete workflow:
    1. Analyzes user requirements to identify relevant AWS components
    2. Queries AWS documentation for component details
    3. Generates specific application and infrastructure questions based on those components
    4. Returns structured questions for detailed architecture design
    
    Args:
        user_requirements: Initial natural language description of system requirements
    
    Returns:
        Structured analysis including:
        - Identified AWS components with rationale
        - Application-centric questions
        - Infrastructure-centric questions
        - AWS service-specific configuration questions
        - Integration and operational questions
    """
    
    return f"""
# AWS Architecture Analysis & Requirements Refinement

I'll analyze your requirements, identify the most suitable AWS components using AWS documentation, 
and then ask specific application and infrastructure questions to design a tailored architecture.

**Your Requirements:**
{user_requirements}

## Step 1: AWS Component Identification
I'll first identify the most relevant AWS services for your requirements by consulting AWS documentation.

## Step 2: Component Analysis
For each identified component, I'll analyze its capabilities and configuration options.

## Step 3: Detailed Questioning
Based on the identified components, I'll ask specific questions about:
- Application architecture and implementation details
- Infrastructure configuration and requirements
- AWS service-specific settings and integrations
- Operational and maintenance considerations

Let me begin the analysis...
"""


@tool
def finalize_architecture(user_requirements: str, question_answers: str) -> str:
    """
    Creates the final comprehensive AWS architecture design based on initial requirements
    and detailed answers to application/infrastructure questions.
    
    This tool takes the user's answers to specific AWS component questions and creates
    a complete, implementation-ready architecture design with detailed specifications.
    
    Args:
        user_requirements: Original user requirements
        question_answers: User's detailed answers to application and infrastructure questions
    
    Returns:
        Complete AWS architecture design including:
        - Executive summary and architecture overview
        - Detailed AWS service configurations
        - Application and infrastructure implementation details
        - Data flow and integration patterns
        - Security, networking, and operational considerations
        - Best practices implementation
        - Deployment roadmap and next steps
    """
    
    return f"""
# Final AWS Architecture Design

Based on your requirements and detailed responses, I'll create a comprehensive, 
implementation-ready AWS architecture design.

**Original Requirements:**
{user_requirements}

**Detailed Specifications:**
{question_answers}

## Complete Architecture Design
I'll now design a tailored AWS architecture that specifically addresses your application 
and infrastructure needs with precise service configurations and implementation details.
""" 