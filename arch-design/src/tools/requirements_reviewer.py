from strands import tool


@tool
def review_requirements(initial_requirements: str, identified_aws_components: str = "") -> str:
    """
    Generate application and infrastructure-centric questions based on identified AWS components.
    
    This tool takes user requirements and a list of identified AWS components, then generates
    specific questions about application architecture, infrastructure configuration, and 
    implementation details for each AWS service.
    
    Args:
        initial_requirements: The user's initial description of their system requirements
        identified_aws_components: List of AWS services/components identified for the architecture
    
    Returns:
        Structured questions organized by:
        - Application architecture questions
        - Infrastructure configuration questions  
        - AWS service-specific implementation questions
        - Integration and operational questions
    """
    
    return f"""
# Application & Infrastructure Requirements Analysis

Based on your requirements and the identified AWS components, I'll ask specific questions about your application and infrastructure needs.

**Your Requirements:**
{initial_requirements}

**Identified AWS Components:**
{identified_aws_components}

## Application-Centric Questions
[Questions about application architecture, frameworks, dependencies, scaling patterns]

## Infrastructure-Centric Questions  
[Questions about networking, security, compliance, operational requirements]

## AWS Service-Specific Questions
[Detailed configuration questions for each identified AWS service]

## Integration & Operational Questions
[Questions about CI/CD, monitoring, backup, disaster recovery]
"""


@tool  
def clarify_requirements(aws_service_answers: str, original_requirements: str = "") -> str:
    """
    Process AWS service-specific answers and create a comprehensive architecture specification.
    
    This tool takes the user's answers to AWS service-specific questions and combines them with
    the original requirements to create a detailed, AWS-native requirements specification
    that includes specific service configurations, integrations, and implementation details.
    
    Args:
        aws_service_answers: User's responses to AWS service-specific questions from review_requirements
        original_requirements: The original user requirements (optional, for context)
    
    Returns:
        A complete, AWS-focused requirements specification including:
        - Consolidated requirements summary
        - AWS service specifications and configurations
        - Service integration requirements
        - Security and compliance configurations
        - Performance and scalability settings
        - Cost optimization considerations
        - Implementation roadmap with AWS services
        - Ready-for-design AWS architecture specification
    """
    
    # This tool consolidates AWS service answers into a comprehensive specification
    # that maps user needs directly to AWS service configurations and capabilities
    
    return f"""
# AWS-Native Requirements Specification

Based on your original requirements and AWS service-specific answers, I'll create a comprehensive 
specification that maps your needs directly to AWS services and configurations.

**Original Requirements:**
{original_requirements}

**AWS Service Specifications:**
{aws_service_answers}

## AWS Service Configuration Specification
[The LLM will create detailed AWS service configurations based on the answers]

## Service Integration Architecture
[How the identified AWS services will work together]

## Implementation Recommendations
[Specific AWS service configurations, instance types, networking, etc.]

## Ready for AWS Architecture Design
Your requirements are now mapped to specific AWS services and configurations.
You can now use the `design_aws_architecture` tool with this AWS-native specification 
for a highly tailored and implementation-ready design.
""" 