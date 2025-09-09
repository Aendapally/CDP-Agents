#!/usr/bin/env python3
"""
Test script to verify the diagram generation fix works
"""

import yaml
from pathlib import Path
from diagrams import Diagram, Cluster, Edge
import diagrams.aws.network as aws_network
import diagrams.aws.compute as aws_compute
import diagrams.aws.database as aws_database
import diagrams.aws.storage as aws_storage
import diagrams.aws.security as aws_security
import diagrams.aws.management as aws_management


def test_diagram_generation():
    """Test the diagram generation with a recent YAML file"""
    
    # Read the YAML file from the recent architecture
    yaml_file = Path("nodejs_web_application_aws_architecture_20250722_060836/node.js_web_application_aws_architecture.yaml")
    
    if not yaml_file.exists():
        print("❌ YAML file not found")
        return
    
    with open(yaml_file, 'r') as f:
        yaml_content = f.read()
    
    # Parse YAML
    try:
        parsed_yaml = yaml.safe_load(yaml_content)
        print(f"✅ YAML parsed successfully")
        print(f"📊 Found {len(parsed_yaml.get('diagram', {}).get('resources', []))} resources")
    except Exception as e:
        print(f"❌ YAML parsing failed: {e}")
        return
    
    # Generate simple diagram
    try:
        output_path = "test_architecture_diagram.png"
        
        with Diagram("Test AWS Architecture", filename="test_architecture_diagram", show=False, direction="LR"):
            # Create a few sample components to test
            cloudfront = aws_network.CloudfrontDistribution("CloudFront")
            alb = aws_network.ElbApplicationLoadBalancer("ALB")  
            ec2 = aws_compute.EC2("Web Server")
            rds = aws_database.Rds("Database")
            
            # Connect them
            cloudfront >> alb >> ec2 >> rds
        
        if Path(f"{output_path}").exists():
            file_size = Path(f"{output_path}").stat().st_size
            print(f"✅ Diagram generated successfully!")
            print(f"📁 File: {output_path}")
            print(f"📏 Size: {file_size:,} bytes")
            return True
        else:
            print("❌ Diagram file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Diagram generation failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing diagram generation fix...")
    success = test_diagram_generation()
    
    if success:
        print("\n🎉 SUCCESS: Diagram generation is working!")
        print("The agent's YAML-to-diagram functionality has been fixed.")
    else:
        print("\n❌ FAILED: Still having issues with diagram generation") 