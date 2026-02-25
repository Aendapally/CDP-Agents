from strands import tool


@tool
def analyze_and_question(user_requirements: str) -> str:
    """
    Orchestrates the requirements gathering phase by analyzing user requirements and generating
    application and infrastructure questions WITHOUT querying AWS documentation.
    
    This tool focuses on requirements gathering FIRST:
    1. Analyzes user requirements to understand business and technical needs
    2. Generates application-centric questions (what the app does, users, data, features)
    3. Generates infrastructure-centric questions (scaling, availability, security, performance)
    4. Does NOT query AWS documentation in this phase - that happens after requirements are complete
    
    IMPORTANT: Do NOT use AWS MCP tools (search_documentation, read_documentation) in this phase.
    Focus purely on understanding the application and infrastructure requirements.
    
    Args:
        user_requirements: Initial natural language description of system requirements
    
    Returns:
        Structured analysis including:
        - Requirements analysis and understanding
        - Application-centric questions (frameworks, features, users, data)
        - Infrastructure-centric questions (scaling, availability, security, compliance)
        - Performance and operational requirements questions
        - NO AWS service recommendations at this stage
    """
    
    return f"""
# Requirements Analysis & Gathering

I'll analyze your requirements and ask comprehensive questions to understand your application 
and infrastructure needs. I will NOT query AWS documentation at this stage - that will happen 
after we gather all requirements.

**Your Requirements:**
{user_requirements}

## Step 1: Requirements Understanding
I'll analyze your requirements to understand:
- Business objectives and use cases
- Application functionality and features
- User base and access patterns
- Data types and volumes
- Performance and availability needs

## Step 2: Application-Focused Questions
I'll ask questions about:
- Application architecture and technology stack
- User experience and access patterns
- Data handling and storage needs
- Integration requirements
- Feature-specific needs

## Step 3: Infrastructure-Focused Questions
I'll ask questions about:
- Scaling and performance requirements
- Availability and disaster recovery needs
- Security and compliance requirements
- Network and connectivity needs
- Operational and monitoring requirements

Let me begin the requirements analysis...
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