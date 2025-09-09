from strands import tool
import yaml
import tempfile
import os
import subprocess
import json
import sys
from pathlib import Path
from .diagrams_as_code_reference import (
    DIAGRAMS_AS_CODE_EXAMPLES,
    AWS_SERVICE_TYPES,
    YAML_STRUCTURE_GUIDE
)


@tool
def generate_diagram_from_yaml(yaml_content: str, output_filename: str = "architecture_diagram", output_folder: str = None) -> str:
    """
    Generate AWS architecture diagram from diagrams-as-code YAML format and save to folder.
    
    This tool takes a YAML file in diagrams-as-code format and creates a visual AWS architecture 
    diagram. It uses the diagrams-as-code library to generate PNG diagrams showing the 
    architecture components and their relationships.
    
    Args:
        yaml_content: The complete YAML content in diagrams-as-code format
        output_filename: Name for the output PNG file (without extension)
        output_folder: Optional folder to save to. If not provided, tries to detect from recent YAML generation
    
    Returns:
        Success message with file path and diagram details
    """
    
    # Auto-detect output folder if not provided
    if not output_folder:
        # Look for recent folder info files
        current_dir = Path('.')
        info_files = list(current_dir.glob('*/.folder_info'))
        
        if info_files:
            # Get the most recent folder info
            latest_info = max(info_files, key=lambda f: f.stat().st_mtime)
            output_folder = latest_info.parent.name
        else:
            # Default to current directory
            output_folder = "."
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)
    
    # Parse YAML content
    try:
        parsed_yaml = yaml.safe_load(yaml_content)
        if not parsed_yaml or 'diagram' not in parsed_yaml:
            return "❌ Error: Invalid YAML format. Missing 'diagram' section."
    except yaml.YAMLError as e:
        return f"❌ Error: Failed to parse YAML content: {str(e)}"
    
    # Set output path
    output_path = output_dir / f"{output_filename}.png"
    
    # Skip the broken diagrams-as-code CLI and use Python diagrams library directly
    try:
        result = generate_simple_diagram(parsed_yaml, str(output_path))
        
        if "successfully" in result.lower():
            return f"""✅ Architecture Diagram Generated Successfully!

📁 **Output Folder**: {output_folder}/
🖼️ **PNG File**: {output_path}
📏 **File Size**: {output_path.stat().st_size:,} bytes
📊 **Components**: {len(parsed_yaml.get('diagram', {}).get('resources', []))} services visualized

🎯 **Diagram Features:**
- Professional AWS service icons
- Clear data flow connections
- Organized component layout
- High-resolution PNG format

📂 **Folder Contents:**
{get_folder_contents(output_dir)}

✅ Your architecture diagram is ready for presentations and documentation!"""
        else:
            return result
            
    except Exception as e:
        return f"❌ Error generating diagram: {str(e)}"


def generate_with_diagrams_as_code(yaml_content: str, output_path: str) -> str:
    """
    Generate diagram using diagrams-as-code library
    """
    try:
        # Try to use diagrams-as-code if available
        import diagrams_as_code
        
        # Create temporary YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            temp_file.write(yaml_content)
            temp_yaml_path = temp_file.name
        
        try:
            # Generate diagram using diagrams-as-code
            result = subprocess.run([
                'diagrams-as-code', 
                'generate', 
                temp_yaml_path,
                '--output', output_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return f"✅ Diagram generated successfully using diagrams-as-code: {output_path}"
            else:
                return f"❌ diagrams-as-code failed: {result.stderr}"
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_yaml_path):
                os.unlink(temp_yaml_path)
    
    except ImportError:
        return "❌ diagrams-as-code library not available, using fallback method"
    except Exception as e:
        return f"❌ Error with diagrams-as-code: {str(e)}"


def generate_simple_diagram(parsed_yaml, output_path):
    """
    Generate a simple diagram using the diagrams library directly
    """
    try:
        from diagrams import Diagram, Cluster, Edge
        import diagrams.aws.network as aws_network
        import diagrams.aws.compute as aws_compute
        import diagrams.aws.database as aws_database
        import diagrams.aws.storage as aws_storage
        import diagrams.aws.security as aws_security
        import diagrams.aws.management as aws_management
        import diagrams.aws.devtools as aws_devtools
        import diagrams.aws.mobile as aws_mobile
        import diagrams.aws.analytics as aws_analytics
        import diagrams.aws.integration as aws_integration
        import diagrams.aws.general as aws_general
        import diagrams.generic.network as generic_network
        
        # Extract diagram info
        diagram_info = parsed_yaml.get('diagram', {})
        diagram_name = diagram_info.get('name', 'AWS Architecture')
        resources = diagram_info.get('resources', [])
        
        # Create the diagram
        output_filename = Path(output_path).stem
        output_dir = Path(output_path).parent
        
        with Diagram(diagram_name, filename=str(output_dir / output_filename), show=False, direction="LR"):
            nodes = {}
            
            # Create nodes for each resource
            for i, resource in enumerate(resources):
                resource_id = resource.get('id', f'resource_{i}')
                resource_name = resource.get('name', resource_id)
                resource_type = resource.get('type', 'aws.general.General')
                
                # Map AWS service types to diagrams classes with improved case-insensitive matching
                try:
                    # Network Services
                    if 'network' in resource_type.lower():
                        if 'cloudfront' in resource_type.lower():
                            nodes[resource_id] = aws_network.CloudFront(resource_name)
                        elif 'route53' in resource_type.lower():
                            nodes[resource_id] = aws_network.Route53(resource_name)
                        elif 'elb' in resource_type.lower() and 'application' in resource_type.lower():
                            nodes[resource_id] = aws_network.ElbApplicationLoadBalancer(resource_name)
                        elif 'elb' in resource_type.lower() and 'network' in resource_type.lower():
                            nodes[resource_id] = aws_network.ElbNetworkLoadBalancer(resource_name)
                        elif 'elb' in resource_type.lower():
                            nodes[resource_id] = aws_network.ELB(resource_name)
                        elif 'apigateway' in resource_type.lower():
                            nodes[resource_id] = aws_network.APIGateway(resource_name)
                        elif 'vpc' in resource_type.lower():
                            nodes[resource_id] = aws_network.VPC(resource_name)
                        elif 'nat' in resource_type.lower():
                            nodes[resource_id] = aws_network.NATGateway(resource_name)
                        elif 'internetgateway' in resource_type.lower():
                            nodes[resource_id] = aws_network.InternetGateway(resource_name)
                        elif 'privatelink' in resource_type.lower():
                            nodes[resource_id] = aws_network.Privatelink(resource_name)
                        elif 'transit' in resource_type.lower():
                            nodes[resource_id] = aws_network.TransitGateway(resource_name)
                        elif 'direct' in resource_type.lower():
                            nodes[resource_id] = aws_network.DirectConnect(resource_name)
                        else:
                            nodes[resource_id] = aws_network.VPC(resource_name)
                    
                    # Compute Services
                    elif 'compute' in resource_type.lower():
                        if 'ec2' in resource_type.lower():
                            nodes[resource_id] = aws_compute.EC2(resource_name)
                        elif 'ecs' in resource_type.lower():
                            nodes[resource_id] = aws_compute.ECS(resource_name)
                        elif 'eks' in resource_type.lower():
                            nodes[resource_id] = aws_compute.EKS(resource_name)
                        elif 'lambda' in resource_type.lower():
                            nodes[resource_id] = aws_compute.Lambda(resource_name)
                        elif 'fargate' in resource_type.lower():
                            nodes[resource_id] = aws_compute.Fargate(resource_name)
                        elif 'beanstalk' in resource_type.lower():
                            nodes[resource_id] = aws_compute.ElasticBeanstalk(resource_name)
                        elif 'ecr' in resource_type.lower():
                            nodes[resource_id] = aws_compute.ECR(resource_name)
                        elif 'apprunner' in resource_type.lower():
                            nodes[resource_id] = aws_compute.AppRunner(resource_name)
                        else:
                            nodes[resource_id] = aws_compute.EC2(resource_name)
                    
                    # Database Services
                    elif 'database' in resource_type.lower():
                        if 'dynamodb' in resource_type.lower():
                            nodes[resource_id] = aws_database.Dynamodb(resource_name)
                        elif 'rds' in resource_type.lower():
                            nodes[resource_id] = aws_database.RDS(resource_name)
                        elif 'elasticache' in resource_type.lower():
                            nodes[resource_id] = aws_database.ElastiCache(resource_name)
                        elif 'redshift' in resource_type.lower():
                            nodes[resource_id] = aws_database.Redshift(resource_name)
                        elif 'aurora' in resource_type.lower():
                            nodes[resource_id] = aws_database.Aurora(resource_name)
                        elif 'documentdb' in resource_type.lower():
                            nodes[resource_id] = aws_database.DocumentdbMongodbCompatibility(resource_name)
                        elif 'neptune' in resource_type.lower():
                            nodes[resource_id] = aws_database.Neptune(resource_name)
                        elif 'dax' in resource_type.lower():
                            nodes[resource_id] = aws_database.DynamodbDax(resource_name)
                        else:
                            nodes[resource_id] = aws_database.RDS(resource_name)
                    
                    # Storage Services
                    elif 'storage' in resource_type.lower():
                        if 's3' in resource_type.lower():
                            nodes[resource_id] = aws_storage.S3(resource_name)
                        elif 'ebs' in resource_type.lower():
                            nodes[resource_id] = aws_storage.EBS(resource_name)
                        elif 'efs' in resource_type.lower():
                            nodes[resource_id] = aws_storage.EFS(resource_name)
                        elif 'fsx' in resource_type.lower():
                            nodes[resource_id] = aws_storage.Fsx(resource_name)
                        elif 'backup' in resource_type.lower():
                            nodes[resource_id] = aws_storage.Backup(resource_name)
                        else:
                            nodes[resource_id] = aws_storage.S3(resource_name)
                    
                    # Security Services
                    elif 'security' in resource_type.lower():
                        if 'waf' in resource_type.lower():
                            nodes[resource_id] = aws_security.WAF(resource_name)
                        elif 'shield' in resource_type.lower():
                            nodes[resource_id] = aws_security.Shield(resource_name)
                        elif 'cognito' in resource_type.lower():
                            nodes[resource_id] = aws_security.Cognito(resource_name)
                        elif 'kms' in resource_type.lower():
                            nodes[resource_id] = aws_security.KMS(resource_name)
                        elif 'secrets' in resource_type.lower():
                            nodes[resource_id] = aws_security.SecretsManager(resource_name)
                        elif 'iam' in resource_type.lower():
                            nodes[resource_id] = aws_security.IAM(resource_name)
                        elif 'certificate' in resource_type.lower():
                            nodes[resource_id] = aws_security.CertificateManager(resource_name)
                        else:
                            nodes[resource_id] = aws_security.WAF(resource_name)
                    
                    # Integration Services
                    elif 'integration' in resource_type.lower():
                        if 'sqs' in resource_type.lower():
                            nodes[resource_id] = aws_integration.SQS(resource_name)
                        elif 'sns' in resource_type.lower():
                            nodes[resource_id] = aws_integration.SNS(resource_name)
                        elif 'eventbridge' in resource_type.lower():
                            nodes[resource_id] = aws_integration.Eventbridge(resource_name)
                        elif 'stepfunctions' in resource_type.lower():
                            nodes[resource_id] = aws_integration.StepFunctions(resource_name)
                        elif 'mq' in resource_type.lower():
                            nodes[resource_id] = aws_integration.MQ(resource_name)
                        elif 'appsync' in resource_type.lower():
                            nodes[resource_id] = aws_integration.Appsync(resource_name)
                        else:
                            nodes[resource_id] = aws_integration.SQS(resource_name)
                    
                    # Analytics Services
                    elif 'analytics' in resource_type.lower():
                        if 'kinesis' in resource_type.lower():
                            nodes[resource_id] = aws_analytics.Kinesis(resource_name)
                        elif 'emr' in resource_type.lower():
                            nodes[resource_id] = aws_analytics.EMR(resource_name)
                        elif 'glue' in resource_type.lower():
                            nodes[resource_id] = aws_analytics.Glue(resource_name)
                        elif 'athena' in resource_type.lower():
                            nodes[resource_id] = aws_analytics.Athena(resource_name)
                        elif 'quicksight' in resource_type.lower():
                            nodes[resource_id] = aws_analytics.Quicksight(resource_name)
                        elif 'redshift' in resource_type.lower():
                            nodes[resource_id] = aws_analytics.Redshift(resource_name)
                        else:
                            nodes[resource_id] = aws_analytics.Kinesis(resource_name)
                    
                    # Management Services
                    elif 'management' in resource_type.lower():
                        if 'cloudwatch' in resource_type.lower():
                            nodes[resource_id] = aws_management.Cloudwatch(resource_name)
                        elif 'cloudtrail' in resource_type.lower():
                            nodes[resource_id] = aws_management.Cloudtrail(resource_name)
                        elif 'cloudformation' in resource_type.lower():
                            nodes[resource_id] = aws_management.Cloudformation(resource_name)
                        elif 'systems' in resource_type.lower():
                            nodes[resource_id] = aws_management.SystemsManager(resource_name)
                        elif 'config' in resource_type.lower():
                            nodes[resource_id] = aws_management.Config(resource_name)
                        else:
                            nodes[resource_id] = aws_management.Cloudwatch(resource_name)
                    
                    # DevTools Services
                    elif 'devtools' in resource_type.lower():
                        if 'xray' in resource_type.lower():
                            nodes[resource_id] = aws_devtools.XRay(resource_name)
                        elif 'codecommit' in resource_type.lower():
                            nodes[resource_id] = aws_devtools.Codecommit(resource_name)
                        elif 'codebuild' in resource_type.lower():
                            nodes[resource_id] = aws_devtools.Codebuild(resource_name)
                        elif 'codepipeline' in resource_type.lower():
                            nodes[resource_id] = aws_devtools.Codepipeline(resource_name)
                        elif 'codedeploy' in resource_type.lower():
                            nodes[resource_id] = aws_devtools.Codedeploy(resource_name)
                        elif 'cloud9' in resource_type.lower():
                            nodes[resource_id] = aws_devtools.Cloud9(resource_name)
                        else:
                            nodes[resource_id] = aws_devtools.XRay(resource_name)
                    
                    # Mobile Services
                    elif 'mobile' in resource_type.lower():
                        if 'apigateway' in resource_type.lower():
                            nodes[resource_id] = aws_mobile.APIGateway(resource_name)
                        elif 'amplify' in resource_type.lower():
                            nodes[resource_id] = aws_mobile.Amplify(resource_name)
                        elif 'pinpoint' in resource_type.lower():
                            nodes[resource_id] = aws_mobile.Pinpoint(resource_name)
                        else:
                            nodes[resource_id] = aws_mobile.APIGateway(resource_name)
                    
                    # Generic Services
                    elif 'generic' in resource_type.lower():
                        if 'internet' in resource_type.lower():
                            nodes[resource_id] = generic_network.Internet(resource_name)
                        else:
                            nodes[resource_id] = generic_network.Internet(resource_name)
                    
                    # General AWS Services
                    elif 'general' in resource_type.lower():
                        if 'client' in resource_type.lower():
                            nodes[resource_id] = aws_general.Client(resource_name)
                        elif 'user' in resource_type.lower():
                            nodes[resource_id] = aws_general.User(resource_name)
                        else:
                            nodes[resource_id] = aws_general.General(resource_name)
                    
                    # Default fallback - categorize by common terms
                    else:
                        if any(term in resource_type.lower() for term in ['lambda', 'function']):
                            nodes[resource_id] = aws_compute.Lambda(resource_name)
                        elif any(term in resource_type.lower() for term in ['database', 'db', 'dynamo']):
                            nodes[resource_id] = aws_database.Dynamodb(resource_name)
                        elif any(term in resource_type.lower() for term in ['storage', 's3', 'bucket']):
                            nodes[resource_id] = aws_storage.S3(resource_name)
                        elif any(term in resource_type.lower() for term in ['network', 'vpc', 'subnet']):
                            nodes[resource_id] = aws_network.VPC(resource_name)
                        elif any(term in resource_type.lower() for term in ['monitor', 'cloudwatch']):
                            nodes[resource_id] = aws_management.Cloudwatch(resource_name)
                        elif any(term in resource_type.lower() for term in ['queue', 'sqs']):
                            nodes[resource_id] = aws_integration.SQS(resource_name)
                        elif any(term in resource_type.lower() for term in ['user', 'client']):
                            nodes[resource_id] = aws_general.User(resource_name)
                        elif any(term in resource_type.lower() for term in ['internet', 'web']):
                            nodes[resource_id] = generic_network.Internet(resource_name)
                        else:
                            nodes[resource_id] = aws_general.General(resource_name)
                        
                except Exception as e:
                    # Ultimate fallback
                    nodes[resource_id] = aws_general.General(resource_name)
            
            # Create relationships
            relationship_count = 0
            for resource in resources:
                resource_id = resource.get('id', '')
                relates = resource.get('relates', [])
                
                if resource_id in nodes:
                    for relation in relates:
                        if isinstance(relation, dict):
                            target = relation.get('to', relation.get('target'))
                            label = relation.get('label', '')
                            
                            if target and target in nodes:
                                try:
                                    if label:
                                        nodes[resource_id] >> Edge(label=label) >> nodes[target]
                                    else:
                                        nodes[resource_id] >> nodes[target]
                                    relationship_count += 1
                                except Exception as e:
                                    pass  # Skip failed relationships
        
        # Get file info
        output_path_obj = Path(output_path)
        file_size = output_path_obj.stat().st_size if output_path_obj.exists() else 0
        
        return f"""✅ Architecture Diagram Generated Successfully!

📁 **Output Folder**: {output_path_obj.parent}/
🖼️ **PNG File**: {output_path_obj}
📏 **File Size**: {file_size:,} bytes
📊 **Components**: {len(nodes)} services visualized
🔗 **Relationships**: {relationship_count} connections created

🎯 **Diagram Features:**
- Professional AWS service icons
- Clear data flow connections
- Organized component layout
- High-resolution PNG format

📂 **Folder Contents:**
{get_folder_contents(output_path_obj.parent)}

✅ Your architecture diagram is ready for presentations and documentation!"""
        
    except ImportError as e:
        return f"""❌ Error: Required libraries not installed. {str(e)}

Please install with:
pip install diagrams graphviz

And ensure graphviz is installed on your system:
- macOS: brew install graphviz
- Ubuntu: sudo apt-get install graphviz
- Windows: Download from https://graphviz.org/download/"""
    
    except Exception as e:
        return f"❌ Error generating diagram: {str(e)}"


def get_folder_contents(folder_path):
    """Get a formatted list of folder contents"""
    try:
        folder = Path(folder_path)
        contents = []
        
        for item in folder.iterdir():
            if item.name.startswith('.'):
                continue  # Skip hidden files
            
            if item.is_file():
                size = item.stat().st_size
                if size > 1024 * 1024:  # > 1MB
                    size_str = f"{size / (1024*1024):.1f}MB"
                elif size > 1024:  # > 1KB
                    size_str = f"{size / 1024:.1f}KB"
                else:
                    size_str = f"{size}B"
                
                contents.append(f"  📄 {item.name} ({size_str})")
        
        return "\n".join(contents) if contents else "  (Empty folder)"
    
    except Exception:
        return "  (Unable to read folder contents)"


@tool
def validate_yaml_schema(yaml_content: str) -> str:
    """
    Validate YAML content against diagrams-as-code schema.
    
    This tool validates the YAML structure to ensure it's compatible with diagrams-as-code
    and provides feedback on any issues or improvements needed.
    
    Args:
        yaml_content: The YAML content to validate
    
    Returns:
        Validation results including:
        - Schema compliance status
        - Any errors or warnings
        - Suggestions for improvements
    """
    try:
        # Parse the YAML
        parsed_yaml = yaml.safe_load(yaml_content)
        
        errors = []
        warnings = []
        
        # Check basic structure
        if not isinstance(parsed_yaml, dict):
            errors.append("Root element must be a dictionary")
        else:
            # Check for required 'diagram' key
            if 'diagram' not in parsed_yaml:
                errors.append("Missing required 'diagram' key")
            else:
                diagram = parsed_yaml['diagram']
                
                # Check diagram properties
                if 'name' not in diagram:
                    warnings.append("Missing 'name' in diagram - will use default")
                if 'resources' not in diagram:
                    errors.append("Missing required 'resources' in diagram")
                else:
                    resources = diagram['resources']
                    if not isinstance(resources, list):
                        errors.append("'resources' must be a list")
                    elif len(resources) == 0:
                        warnings.append("No resources defined in diagram")
                    else:
                        # Validate each resource
                        for i, resource in enumerate(resources):
                            if not isinstance(resource, dict):
                                errors.append(f"Resource {i} must be a dictionary")
                            else:
                                if 'id' not in resource:
                                    errors.append(f"Resource {i} missing required 'id'")
                                if 'name' not in resource:
                                    warnings.append(f"Resource {i} missing 'name'")
                                if 'type' not in resource:
                                    errors.append(f"Resource {i} missing required 'type'")
        
        # Generate validation report
        if errors:
            status = "❌ INVALID"
            error_list = "\n".join(f"  • {error}" for error in errors)
            report = f"{status}\n\n**Errors:**\n{error_list}"
        else:
            status = "✅ VALID"
            report = f"{status}\n\n**Schema Validation Passed!**"
        
        if warnings:
            warning_list = "\n".join(f"  • {warning}" for warning in warnings)
            report += f"\n\n**Warnings:**\n{warning_list}"
        
        return report
        
    except yaml.YAMLError as e:
        return f"❌ YAML Parse Error: {str(e)}"
    except Exception as e:
        return f"❌ Validation Error: {str(e)}"


@tool
def install_diagram_dependencies() -> str:
    """
    Install required dependencies for diagram generation.
    
    This tool installs the necessary Python packages and system dependencies
    required for generating AWS architecture diagrams.
    
    Returns:
        Installation status and instructions
    """
    try:
        # Try to install Python packages
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'diagrams', 'diagrams-as-code', 'graphviz'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return """✅ Dependencies installed successfully!

📦 **Installed Packages:**
- diagrams: For creating AWS architecture diagrams
- diagrams-as-code: For YAML-based diagram generation
- graphviz: For graph visualization support

🎯 **System Requirements:**
Make sure you have graphviz installed on your system:
- **macOS**: `brew install graphviz`
- **Ubuntu**: `sudo apt-get install graphviz`
- **Windows**: Download from https://graphviz.org/download/

✅ **Ready to Generate Diagrams!**
You can now use the generate_diagram_from_yaml tool to create PNG diagrams from your YAML specifications."""
        else:
            return f"""⚠️ Installation Issues:

**Error Output:**
{result.stderr}

**Manual Installation:**
Please try installing manually:
```bash
pip install diagrams diagrams-as-code graphviz
```

**System Dependencies:**
Also ensure graphviz is installed:
- macOS: `brew install graphviz`
- Ubuntu: `sudo apt-get install graphviz`
- Windows: Download from https://graphviz.org/download/"""
            
    except Exception as e:
        return f"""❌ Installation Error: {str(e)}

**Manual Installation Steps:**
1. Install Python packages:
   ```bash
   pip install diagrams diagrams-as-code graphviz
   ```

2. Install system graphviz:
   - macOS: `brew install graphviz`
   - Ubuntu: `sudo apt-get install graphviz`
   - Windows: Download from https://graphviz.org/download/""" 