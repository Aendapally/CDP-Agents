#!/usr/bin/env python3
"""
AWS Architecture Design Agent Workflow Diagram Generator
This script creates a visual flow diagram showing how the agent works.
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.generic import Node

def create_agent_workflow_diagram():
    """Create the AWS Architecture Design Agent workflow diagram."""
    
    with Diagram("AWS Architecture Design Agent Workflow", 
                 filename="agent_workflow_diagram", 
                 show=False, 
                 direction="TB",
                 curvestyle="ortho"):
        
        # User Input Section
        with Cluster("User Input"):
            user = Node("User")
            requirements = Node("Requirements\nText")
            user >> requirements
        
        # Agent Core Section
        with Cluster("Agent Core"):
            agent = Node("Architecture\nDesign Agent")
            bedrock = Node("AWS Bedrock\n(Claude 3.5 Sonnet)")
            agent >> bedrock
            bedrock >> agent
        
        # Analysis Phase
        with Cluster("Phase 1: Requirements Analysis"):
            analyze = Node("analyze_and_question")
            aws_docs = Node("AWS Documentation\nMCP Server")
            questions = Node("Generated\nQuestions")
            
            requirements >> analyze
            analyze >> aws_docs
            aws_docs >> analyze
            analyze >> questions
        
        # Design Phase
        with Cluster("Phase 2: Architecture Design"):
            design = Node("finalize_architecture")
            architecture = Node("Architecture\nDesign")
            
            questions >> design
            design >> architecture
        
        # YAML Generation Phase
        with Cluster("Phase 3: YAML Generation"):
            yaml_gen = Node("convert_architecture_to_yaml")
            yaml_file = Node("diagrams-as-code\nYAML")
            
            architecture >> yaml_gen
            yaml_gen >> yaml_file
        
        # Diagram Generation Phase
        with Cluster("Phase 4: Visual Diagram"):
            diagram_gen = Node("generate_diagram_from_yaml")
            png_diagram = Node("AWS Architecture\nDiagram (PNG)")
            
            yaml_file >> diagram_gen
            diagram_gen >> png_diagram
        
        # Output Section
        with Cluster("Output & Organization"):
            folder = Node("Project Folder\n(Organized Output)")
            metadata = Node("Metadata\n(.folder_info)")
            
            png_diagram >> folder
            yaml_file >> folder
            folder >> metadata
        
        # User Review Section
        with Cluster("User Review"):
            review = Node("User Review")
            feedback = Node("User Feedback")
            
            folder >> review
            review >> feedback
            feedback >> user
        
        # Add flow connections between phases
        analyze >> design
        design >> yaml_gen
        yaml_gen >> diagram_gen
        diagram_gen >> folder

if __name__ == "__main__":
    print("Generating AWS Architecture Design Agent Workflow Diagram...")
    create_agent_workflow_diagram()
    print("✅ Workflow diagram generated successfully!")
    print("📁 File: agent_workflow_diagram.png") 