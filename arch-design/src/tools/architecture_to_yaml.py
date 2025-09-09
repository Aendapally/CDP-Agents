from strands import tool
import yaml
import json
import re
import os
from datetime import datetime
from pathlib import Path
from .diagrams_as_code_reference import (
    DIAGRAMS_AS_CODE_EXAMPLES,
    AWS_SERVICE_TYPES,
    ARCHITECTURE_PATTERNS,
    YAML_STRUCTURE_GUIDE,
    get_examples_for_architecture_type,
    get_service_type_for_component
)


@tool
def convert_architecture_to_yaml(architecture_design: str, diagram_name: str = "AWS Architecture", output_folder: str = None, additional_categories: str = None) -> str:
    """
    Convert AWS architecture design text to diagrams-as-code YAML format and save to folder.
    
    This tool analyzes the architecture design text from aws_architecture_designer and converts it
    into a structured YAML file compatible with diagrams-as-code. It identifies AWS components,
    their relationships, and data flows to create a visual diagram specification.
    
    Args:
        architecture_design: The complete architecture design text output from aws_architecture_designer
        diagram_name: The name for the diagram (default: "AWS Architecture")
        output_folder: Optional folder name. If not provided, uses sanitized diagram name with timestamp
    
    Returns:
        Status message with file path and YAML content preview
    """
    
    # Create output folder name if not provided
    if not output_folder:
        # Sanitize diagram name for folder
        sanitized_name = re.sub(r'[^a-zA-Z0-9\s-]', '', diagram_name)
        sanitized_name = re.sub(r'\s+', '_', sanitized_name).lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = f"{sanitized_name}_{timestamp}"
    
    # Create the output directory
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)
    
    # Create the YAML structure with enhanced metadata
    yaml_structure = {
        "diagram": {
            "name": diagram_name,
            "direction": "left-to-right",
            "format": "png",
            "open": True,
            "style": {
                "graph": {
                    "splines": "ortho",
                    "nodesep": "0.6",
                    "ranksep": "1.2"
                },
                "node": {
                    "shape": "box",
                    "style": "rounded,filled",
                    "fillcolor": "lightblue"
                },
                "edge": {
                    "style": "solid",
                    "color": "darkblue",
                    "fontsize": "10"
                }
            },
            "resources": []
        }
    }
    
    # Parse architecture design and extract components
    components = []
    relationships = []
    
    # Group components by category for better organization
    service_categories = {
        "frontend": [],
        "network": [],
        "security": [],
        "compute": [],
        "database": [],
        "storage": [],
        "integration": [],
        "monitoring": [],
        "devops": [],
        "users": []
    }
    
    # Common AWS service patterns to look for - Updated to match schema
    service_patterns = {
        # Network Services
        r'cloudfront|cdn': {'type': 'aws.network.CloudFront', 'name': 'CloudFront', 'category': 'network', 'description': 'Content Delivery Network'},
        r'route\s*53|dns': {'type': 'aws.network.Route53', 'name': 'Route 53', 'category': 'network', 'description': 'DNS Management'},
        r'application\s*load\s*balancer|alb': {'type': 'aws.network.ElbApplicationLoadBalancer', 'name': 'Application Load Balancer', 'category': 'network', 'description': 'Load Balancing'},
        r'network\s*load\s*balancer|nlb': {'type': 'aws.network.ElbNetworkLoadBalancer', 'name': 'Network Load Balancer', 'category': 'network', 'description': 'Load Balancing'},
        r'classic\s*load\s*balancer|elb': {'type': 'aws.network.ELB', 'name': 'Classic Load Balancer', 'category': 'network', 'description': 'Load Balancing'},
        r'api\s*gateway': {'type': 'aws.network.APIGateway', 'name': 'API Gateway', 'category': 'network', 'description': 'API Management'},
        r'vpc': {'type': 'aws.network.VPC', 'name': 'VPC', 'category': 'network', 'description': 'Virtual Private Cloud'},
        r'nat\s*gateway': {'type': 'aws.network.NATGateway', 'name': 'NAT Gateway', 'category': 'network', 'description': 'Network Address Translation'},
        r'internet\s*gateway': {'type': 'aws.network.InternetGateway', 'name': 'Internet Gateway', 'category': 'network', 'description': 'Internet Access'},
        r'privatelink': {'type': 'aws.network.Privatelink', 'name': 'PrivateLink', 'category': 'network', 'description': 'Private Connectivity'},
        r'transit\s*gateway': {'type': 'aws.network.TransitGateway', 'name': 'Transit Gateway', 'category': 'network', 'description': 'Network Transit Hub'},
        r'direct\s*connect': {'type': 'aws.network.DirectConnect', 'name': 'Direct Connect', 'category': 'network', 'description': 'Dedicated Network Connection'},
        
        # Security Services
        r'waf': {'type': 'aws.security.WAF', 'name': 'AWS WAF', 'category': 'security', 'description': 'Web Application Firewall'},
        r'shield': {'type': 'aws.security.Shield', 'name': 'AWS Shield', 'category': 'security', 'description': 'DDoS Protection'},
        r'cognito': {'type': 'aws.security.Cognito', 'name': 'Amazon Cognito', 'category': 'security', 'description': 'User Authentication'},
        r'certificate\s*manager|acm': {'type': 'aws.security.CertificateManager', 'name': 'Certificate Manager', 'category': 'security', 'description': 'SSL/TLS Certificates'},
        r'kms': {'type': 'aws.security.KMS', 'name': 'AWS KMS', 'category': 'security', 'description': 'Key Management'},
        r'secrets\s*manager': {'type': 'aws.security.SecretsManager', 'name': 'Secrets Manager', 'category': 'security', 'description': 'Secrets Management'},
        r'iam': {'type': 'aws.security.IAM', 'name': 'AWS IAM', 'category': 'security', 'description': 'Identity and Access Management'},
        r'guardduty': {'type': 'aws.security.Guardduty', 'name': 'GuardDuty', 'category': 'security', 'description': 'Threat Detection'},
        
        # Compute Services
        r'ec2': {'type': 'aws.compute.EC2', 'name': 'EC2', 'category': 'compute', 'description': 'Virtual Servers'},
        r'ecs': {'type': 'aws.compute.ECS', 'name': 'ECS', 'category': 'compute', 'description': 'Container Orchestration'},
        r'fargate': {'type': 'aws.compute.Fargate', 'name': 'Fargate', 'category': 'compute', 'description': 'Serverless Containers'},
        r'lambda': {'type': 'aws.compute.Lambda', 'name': 'Lambda', 'category': 'compute', 'description': 'Serverless Functions'},
        r'eks': {'type': 'aws.compute.EKS', 'name': 'EKS', 'category': 'compute', 'description': 'Managed Kubernetes'},
        r'elastic\s*beanstalk': {'type': 'aws.compute.ElasticBeanstalk', 'name': 'Elastic Beanstalk', 'category': 'compute', 'description': 'Application Platform'},
        r'app\s*runner': {'type': 'aws.compute.AppRunner', 'name': 'App Runner', 'category': 'compute', 'description': 'Container-based Applications'},
        
        # Database Services
        r'dynamodb': {'type': 'aws.database.Dynamodb', 'name': 'DynamoDB', 'category': 'database', 'description': 'NoSQL Database'},
        r'rds': {'type': 'aws.database.RDS', 'name': 'RDS', 'category': 'database', 'description': 'Relational Database'},
        r'elasticache': {'type': 'aws.database.ElastiCache', 'name': 'ElastiCache', 'category': 'database', 'description': 'In-Memory Cache'},
        r'dax': {'type': 'aws.database.DAX', 'name': 'DAX', 'category': 'database', 'description': 'DynamoDB Accelerator'},
        r'redshift': {'type': 'aws.database.Redshift', 'name': 'Redshift', 'category': 'database', 'description': 'Data Warehouse'},
        r'aurora': {'type': 'aws.database.Aurora', 'name': 'Aurora', 'category': 'database', 'description': 'High-Performance Database'},
        r'documentdb': {'type': 'aws.database.DocumentDB', 'name': 'DocumentDB', 'category': 'database', 'description': 'MongoDB-compatible Database'},
        r'neptune': {'type': 'aws.database.Neptune', 'name': 'Neptune', 'category': 'database', 'description': 'Graph Database'},
        
        # Storage Services
        r's3': {'type': 'aws.storage.S3', 'name': 'S3', 'category': 'storage', 'description': 'Object Storage'},
        r'ebs': {'type': 'aws.storage.EBS', 'name': 'EBS', 'category': 'storage', 'description': 'Block Storage'},
        r'efs': {'type': 'aws.storage.EFS', 'name': 'EFS', 'category': 'storage', 'description': 'File Storage'},
        r'fsx': {'type': 'aws.storage.FSx', 'name': 'FSx', 'category': 'storage', 'description': 'High-Performance File Systems'},
        r'backup': {'type': 'aws.storage.Backup', 'name': 'AWS Backup', 'category': 'storage', 'description': 'Backup Service'},
        
        # Container Services
        r'ecr': {'type': 'aws.compute.ECR', 'name': 'ECR', 'category': 'devops', 'description': 'Container Registry'},
        
        # Integration Services
        r'sqs': {'type': 'aws.integration.SQS', 'name': 'SQS', 'category': 'integration', 'description': 'Message Queue'},
        r'sns': {'type': 'aws.integration.SNS', 'name': 'SNS', 'category': 'integration', 'description': 'Pub/Sub Messaging'},
        r'eventbridge': {'type': 'aws.integration.Eventbridge', 'name': 'EventBridge', 'category': 'integration', 'description': 'Event Bus'},
        r'step\s*functions': {'type': 'aws.integration.StepFunctions', 'name': 'Step Functions', 'category': 'integration', 'description': 'Workflow Orchestration'},
        r'mq': {'type': 'aws.integration.MQ', 'name': 'Amazon MQ', 'category': 'integration', 'description': 'Message Broker'},
        r'appsync': {'type': 'aws.integration.Appsync', 'name': 'AppSync', 'category': 'integration', 'description': 'GraphQL API'},
        
        # Analytics Services
        r'kinesis': {'type': 'aws.analytics.Kinesis', 'name': 'Kinesis', 'category': 'integration', 'description': 'Data Streaming'},
        r'kinesis\s*data\s*streams': {'type': 'aws.analytics.KinesisDataStreams', 'name': 'Kinesis Data Streams', 'category': 'integration', 'description': 'Real-time Data Streaming'},
        r'kinesis\s*data\s*firehose': {'type': 'aws.analytics.KinesisDataFirehose', 'name': 'Kinesis Data Firehose', 'category': 'integration', 'description': 'Data Delivery'},
        r'emr': {'type': 'aws.analytics.EMR', 'name': 'EMR', 'category': 'integration', 'description': 'Big Data Processing'},
        r'glue': {'type': 'aws.analytics.Glue', 'name': 'AWS Glue', 'category': 'integration', 'description': 'Data Integration'},
        r'athena': {'type': 'aws.analytics.Athena', 'name': 'Athena', 'category': 'integration', 'description': 'Query Service'},
        r'quicksight': {'type': 'aws.analytics.Quicksight', 'name': 'QuickSight', 'category': 'integration', 'description': 'Business Intelligence'},
        r'elasticsearch': {'type': 'aws.analytics.ElasticsearchService', 'name': 'Elasticsearch', 'category': 'integration', 'description': 'Search and Analytics'},
                
        # CI/CD Services (only if requested)
        'ci-cd': {
            r'codecommit': {'type': 'aws.devtools.Codecommit', 'name': 'CodeCommit', 'category': 'ci-cd', 'description': 'Source Control'},
            r'codebuild': {'type': 'aws.devtools.Codebuild', 'name': 'CodeBuild', 'category': 'ci-cd', 'description': 'Build Service'},
            r'codepipeline': {'type': 'aws.devtools.Codepipeline', 'name': 'CodePipeline', 'category': 'ci-cd', 'description': 'CI/CD Pipeline'},
            r'codedeploy': {'type': 'aws.devtools.Codedeploy', 'name': 'CodeDeploy', 'category': 'ci-cd', 'description': 'Deployment Service'},
            r'ecr': {'type': 'aws.compute.ECR', 'name': 'ECR', 'category': 'ci-cd', 'description': 'Container Registry'},
        },
        
        # Cost Management
        r'cost\s*explorer': {'type': 'aws.cost.CostExplorer', 'name': 'Cost Explorer', 'category': 'monitoring', 'description': 'Cost Analysis'},
        r'budgets': {'type': 'aws.cost.Budgets', 'name': 'Budgets', 'category': 'monitoring', 'description': 'Cost Management'},
        
        # Generic/Client Services
        r'internet': {'type': 'generic.network.Internet', 'name': 'Internet', 'category': 'users', 'description': 'Public Internet'},
        r'users?': {'type': 'aws.general.Users', 'name': 'Users', 'category': 'users', 'description': 'End Users'},
        r'clients?': {'type': 'aws.general.Client', 'name': 'Client', 'category': 'users', 'description': 'Client Applications'},
        r'mobile': {'type': 'aws.general.MobileClient', 'name': 'Mobile Client', 'category': 'users', 'description': 'Mobile Applications'},
    }
    
    # Extract services from architecture design with flexible approach
    architecture_lower = architecture_design.lower()
    found_services = set()
    
    # First, try to match known patterns
    for pattern, service_info in service_patterns.items():
        if re.search(pattern, architecture_lower):
            service_id = service_info['name'].lower().replace(' ', '_').replace('-', '_')
            if service_id not in found_services:
                component = {
                    "id": service_id,
                    "name": service_info['name'],
                    "type": service_info['type'],
                    "description": service_info['description']
                }
                components.append(component)
                service_categories[service_info['category']].append(component)
                found_services.add(service_id)
    
    # FLEXIBILITY: Extract any AWS service mentions that weren't caught by patterns
    # Look for common AWS service patterns in the text
    aws_service_mentions = re.findall(r'\b(aws\s+\w+|\w+\s+aws|\w+\s+service|\w+\s+database|\w+\s+storage|\w+\s+compute|\w+\s+network)', architecture_lower)
    
    # Look for capitalized service names that might be custom or new services
    potential_services = re.findall(r'\b[A-Z][a-z]+[A-Z]\w*\b', architecture_design)  # CamelCase
    potential_services.extend(re.findall(r'\b[A-Z]{2,}\b', architecture_design))  # UPPERCASE
    
    # Filter out common words that shouldn't be services
    common_words_to_ignore = {
        'aws', 'service', 'database', 'storage', 'compute', 'network', 'security',
        'management', 'integration', 'analytics', 'devtools', 'mobile', 'general',
        'following', 'relational', 'nosql', 'sql', 'rest', 'api', 'https', 'ssl',
        'tls', 'iam', 'kms', 'nat', 'sso', 'cpu', 'xss', 'alb', 'dns', 'cdn'
    }
    
    # Add flexible service detection for unknown services
    for mention in aws_service_mentions + potential_services:
        mention_clean = mention.strip().lower()
        # Skip if it's a common word or already processed
        if (mention_clean not in found_services and 
            len(mention_clean) > 2 and 
            mention_clean not in common_words_to_ignore and
            not any(word in mention_clean for word in ['following', 'relational', 'nosql', 'sql', 'rest', 'api', 'https', 'ssl', 'tls', 'iam', 'kms', 'nat', 'sso', 'cpu', 'xss', 'alb', 'dns', 'cdn'])):
            
            # Try to infer service type from context
            service_type = infer_service_type(mention_clean)
            service_id = mention_clean.replace(' ', '_').replace('-', '_')
            
            if service_id not in found_services:
                component = {
                    "id": service_id,
                    "name": mention.strip(),
                    "type": service_type,
                    "description": f"Custom or inferred service: {mention.strip()}"
                }
                components.append(component)
                # Put unknown services in appropriate category based on inferred type
                category = infer_category_from_type(service_type)
                service_categories[category].append(component)
                found_services.add(service_id)
    
    # Add generic components if none found
    if not components:
        default_components = [
            {"id": "internet", "name": "Internet", "type": "generic.network.Internet", "description": "Public Internet", "category": "users"},
            {"id": "users", "name": "Users", "type": "aws.general.Users", "description": "End Users", "category": "users"},
            {"id": "web_app", "name": "Web Application", "type": "aws.compute.EC2", "description": "Web Application Server", "category": "compute"},
            {"id": "database", "name": "Database", "type": "aws.database.RDS", "description": "Relational Database", "category": "database"},
            {"id": "storage", "name": "Storage", "type": "aws.storage.S3", "description": "Object Storage", "category": "storage"}
        ]
        components.extend(default_components)
        for component in default_components:
            service_categories[component['category']].append(component)
    
    # FLEXIBILITY: More adaptive relationship generation
    if len(components) > 1:
        # Use LLM-based intelligent relationship generation
        # Analyze the architecture text to determine logical connections
        architecture_analysis = f"""
        Architecture Description: {architecture_design}
        
        Detected Components:
        {chr(10).join([f"- {c['name']} ({c['type']}): {c['description']}" for c in components])}
        
        Based on this architecture description, determine the logical data flows and relationships between these components. 
        Consider typical AWS architecture patterns, data flow directions, and service dependencies.
        """
        
        # Create a more selective relationship approach
        # Only connect services that are logically adjacent or have direct dependencies
        
        # First, create a list of services in the order they appear in the text
        service_order = []
        arch_lower = architecture_design.lower()
        
        for component in components:
            service_name = component['name'].lower()
            pos = arch_lower.find(service_name)
            if pos != -1:
                service_order.append((pos, component))
        
        # Sort by position in text
        service_order.sort(key=lambda x: x[0])
        
        # Generate relationships only between adjacent services or logical pairs
        for i, (pos, component) in enumerate(service_order):
            component_relationships = []
            
            # Only create relationships to the next few services (not all subsequent ones)
            for j in range(i + 1, min(i + 3, len(service_order))):  # Only next 2 services
                target_pos, target_component = service_order[j]
                
                # Check if these services should be logically connected
                if should_connect_services(component, target_component, architecture_design):
                    relationship = create_logical_relationship(component, target_component)
                    if relationship:
                        component_relationships.append(relationship)
            
            # Add monitoring relationship to CloudWatch if it exists
            cloudwatch_component = next((c for c in components if 'cloudwatch' in c['name'].lower()), None)
            if cloudwatch_component and component['id'] != cloudwatch_component['id']:
                if any(aws_service in component['type'].lower() for aws_service in ['aws.']):
                    component_relationships.append({
                        "to": cloudwatch_component['id'],
                        "direction": "outgoing",
                        "label": "Monitoring"
                    })
            
            # Add relationships to component if any were found
            if component_relationships:
                component['relates'] = component_relationships
    
    # Build the final YAML structure
    yaml_structure["diagram"]["resources"] = components
    
    # Convert to YAML string
    yaml_output = yaml.dump(yaml_structure, default_flow_style=False, sort_keys=False)
    
    # Save YAML file to the output folder
    yaml_filename = f"{diagram_name.replace(' ', '_').lower()}.yaml"
    yaml_path = output_dir / yaml_filename
    
    with open(yaml_path, 'w') as f:
        f.write(yaml_output)
    
    # Store the folder path for the diagram generation tool
    folder_info_path = output_dir / ".folder_info"
    with open(folder_info_path, 'w') as f:
        f.write(f"diagram_name={diagram_name}\n")
        f.write(f"yaml_file={yaml_filename}\n")
        f.write(f"output_folder={output_folder}\n")
    
    return f"""✅ Architecture YAML Generated Successfully!

📁 **Output Folder**: {output_folder}/
📄 **YAML File**: {yaml_path}
📊 **Components**: {len(components)} AWS services detected
🔗 **Relationships**: {yaml_output.count('relates:')} connections generated

📋 **YAML Preview:**
{yaml_output[:500]}...

🎯 **Next Steps:**
1. Use generate_diagram_from_yaml to create the visual diagram
2. All files will be saved to: {output_folder}/
3. The folder contains: YAML file + metadata for diagram generation"""


def infer_service_type(service_name: str) -> str:
    """Infer AWS service type from service name when not in known patterns"""
    service_lower = service_name.lower()
    
    # Database keywords
    if any(word in service_lower for word in ['db', 'database', 'dynamo', 'rds', 'sql', 'nosql', 'cache', 'redis', 'mongo']):
        return "aws.database.RDS"
    
    # Storage keywords
    elif any(word in service_lower for word in ['storage', 'bucket', 'file', 'object', 'blob', 's3', 'ebs', 'efs']):
        return "aws.storage.S3"
    
    # Compute keywords
    elif any(word in service_lower for word in ['compute', 'server', 'instance', 'container', 'lambda', 'function', 'ec2', 'ecs']):
        return "aws.compute.EC2"
    
    # Network keywords
    elif any(word in service_lower for word in ['network', 'load', 'balancer', 'cdn', 'gateway', 'dns', 'route', 'vpc']):
        return "aws.network.VPC"
    
    # Security keywords
    elif any(word in service_lower for word in ['security', 'auth', 'identity', 'firewall', 'waf', 'shield', 'cognito']):
        return "aws.security.IAM"
    
    # Integration keywords
    elif any(word in service_lower for word in ['queue', 'message', 'notification', 'event', 'stream', 'sqs', 'sns']):
        return "aws.integration.SQS"
    
    # Monitoring keywords
    elif any(word in service_lower for word in ['monitor', 'log', 'metric', 'watch', 'trace', 'alert']):
        return "aws.management.Cloudwatch"
    
    # Default to general
    else:
        return "aws.general.General"


def infer_category_from_type(service_type: str) -> str:
    """Infer category from service type"""
    if 'database' in service_type:
        return 'database'
    elif 'storage' in service_type:
        return 'storage'
    elif 'compute' in service_type:
        return 'compute'
    elif 'network' in service_type:
        return 'network'
    elif 'security' in service_type:
        return 'security'
    elif 'integration' in service_type:
        return 'integration'
    elif 'management' in service_type:
        return 'monitoring'
    elif 'devtools' in service_type:
        return 'devops'
    else:
        return 'compute'  # Default category


def determine_relationship(source_component: dict, target_component: dict, architecture_text: str) -> dict:
    """Determine relationship between two components with flexible logic"""
    source_type = source_component["type"]
    target_type = target_component["type"]
    source_name = source_component["name"].lower()
    target_name = target_component["name"].lower()
    
    # Check if there's explicit mention of relationship in the architecture text
    text_lower = architecture_text.lower()
    
    # Look for explicit connections mentioned in text
    connection_patterns = [
        fr'{source_name}.*(?:connects?|uses?|accesses?|sends?|routes?).*{target_name}',
        fr'{source_name}.*(?:→|->|flows? to|points? to).*{target_name}',
        fr'{target_name}.*(?:receives?|gets?|from).*{source_name}'
    ]
    
    for pattern in connection_patterns:
        if re.search(pattern, text_lower):
            return {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Explicit Connection"
            }
    
    # Apply flexible pattern matching (original logic but as fallback)
    relationship_info = None
    
    # User/Internet -> CDN/DNS patterns
    if ("general.User" in source_type or "network.Internet" in source_type):
        if ("network.CloudFront" in target_type or "network.Route53" in target_type):
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Web Request"
            }
    
    # DNS -> CDN patterns
    elif "network.Route53" in source_type:
        if "network.CloudFront" in target_type:
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "DNS Resolution"
            }
    
    # CDN -> Load Balancer patterns
    elif "network.CloudFront" in source_type:
        if ("network.Elb" in target_type or "network.APIGateway" in target_type):
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Origin Request"
            }
    
    # Load Balancer -> Compute patterns
    elif ("network.Elb" in source_type or "network.APIGateway" in source_type):
        if ("compute.ECS" in target_type or "compute.Lambda" in target_type or 
            "compute.EC2" in target_type or "compute.Fargate" in target_type):
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Route Request"
            }
    
    # Compute -> Database patterns
    elif ("compute.ECS" in source_type or "compute.Lambda" in source_type or 
          "compute.EC2" in source_type or "compute.Fargate" in source_type):
        if ("database.Dynamodb" in target_type or "database.RDS" in target_type or
            "database.ElastiCache" in target_type):
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Database Query"
            }
    
    # Compute -> Storage patterns
    elif ("compute.ECS" in source_type or "compute.Lambda" in source_type or
          "compute.EC2" in source_type or "compute.Fargate" in source_type):
        if "storage.S3" in target_type:
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "File Storage"
            }
    
    # Compute -> Integration patterns
    elif ("compute.ECS" in source_type or "compute.Lambda" in source_type or
          "compute.EC2" in source_type or "compute.Fargate" in source_type):
        if ("integration.SQS" in target_type or "integration.SNS" in target_type or
            "integration.Eventbridge" in target_type):
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Message Queue"
            }
    
    # Security patterns
    elif "security.WAF" in source_type:
        if ("network.Elb" in target_type or "network.CloudFront" in target_type):
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Security Filter"
            }
    
    # Monitoring patterns
    elif ("compute.ECS" in source_type or "compute.Lambda" in source_type or
          "compute.EC2" in source_type or "database.RDS" in source_type):
        if ("management.Cloudwatch" in target_type or "devtools.XRay" in target_type):
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Monitoring"
            }
    
    # FLEXIBILITY: If no specific pattern matches, check for general compatibility
    elif not relationship_info:
        # General database -> compute relationship
        if "database" in source_type and "compute" in target_type:
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Data Processing"
            }
        # General storage -> compute relationship
        elif "storage" in source_type and "compute" in target_type:
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Data Access"
            }
        # Any service -> monitoring relationship
        elif "management" in target_type or "devtools" in target_type:
            relationship_info = {
                "to": target_component["id"],
                "direction": "outgoing",
                "label": "Monitoring"
            }
    
    return relationship_info


def determine_intelligent_relationship(source_name, source_type, target_name, target_type, architecture_text):
    """
    Intelligently determine relationships between components based on their types and architecture context.
    This function uses flexible pattern recognition without hard-coded flow patterns.
    """
    
    # Convert to lowercase for easier matching
    source_lower = source_name.lower()
    target_lower = target_name.lower()
    source_type_lower = source_type.lower()
    target_type_lower = target_type.lower()
    arch_lower = architecture_text.lower()
    
    # Only create relationships for actual AWS services (not generic ones)
    if not any(aws_service in source_type_lower for aws_service in ['aws.']):
        return None
    
    # Skip self-relationships
    if source_name.lower() == target_name.lower():
        return None
    
    # Check if both services are mentioned in the architecture text
    if source_name.lower() in arch_lower and target_name.lower() in arch_lower:
        # Find the order they appear in the text to determine flow direction
        source_pos = arch_lower.find(source_name.lower())
        target_pos = arch_lower.find(target_name.lower())
        
        # Only create relationship if source appears before target (logical flow)
        if source_pos < target_pos:
            # Be more selective about relationships - only create logical ones
            
            # Skip relationships between services that are too far apart in the text
            # (indicates they're not directly related)
            if target_pos - source_pos > 500:  # Skip if more than 500 chars apart
                return None
            
            # Skip relationships between services of the same category unless they're adjacent
            source_category = get_service_category(source_type_lower)
            target_category = get_service_category(target_type_lower)
            
            if source_category == target_category and target_pos - source_pos > 100:
                return None
            
            # Create relationship with appropriate label based on service types
            label = get_relationship_label(source_type_lower, target_type_lower)
            return {"to": target_name.lower().replace(' ', '_'), "direction": "outgoing", "label": label}
    
    # Optional: Add monitoring relationships for AWS services to CloudWatch
    if 'cloudwatch' in target_lower and source_type_lower != target_type_lower:
        if any(aws_service in source_type_lower for aws_service in ['aws.']):
            return {"to": target_name.lower().replace(' ', '_'), "direction": "outgoing", "label": "Monitoring"}
    
    return None


def get_service_category(service_type):
    """Get the category of an AWS service type."""
    if 'network' in service_type:
        return 'network'
    elif 'compute' in service_type:
        return 'compute'
    elif 'database' in service_type:
        return 'database'
    elif 'storage' in service_type:
        return 'storage'
    elif 'security' in service_type:
        return 'security'
    elif 'management' in service_type:
        return 'management'
    elif 'integration' in service_type:
        return 'integration'
    elif 'analytics' in service_type:
        return 'analytics'
    elif 'devtools' in service_type:
        return 'devtools'
    elif 'mobile' in service_type:
        return 'mobile'
    elif 'general' in service_type:
        return 'general'
    else:
        return 'other'


def get_relationship_label(source_type, target_type):
    """Get an appropriate label for the relationship between two service types."""
    source_cat = get_service_category(source_type)
    target_cat = get_service_category(target_type)
    
    # Network flows
    if source_cat == 'network' and target_cat == 'network':
        return 'Network Flow'
    elif source_cat == 'network' and target_cat == 'compute':
        return 'Route Request'
    
    # Compute flows
    elif source_cat == 'compute' and target_cat == 'database':
        return 'Database Query'
    elif source_cat == 'compute' and target_cat == 'storage':
        return 'Data Access'
    elif source_cat == 'compute' and target_cat == 'integration':
        return 'Message Processing'
    
    # Integration flows
    elif source_cat == 'integration' and target_cat == 'compute':
        return 'Event Trigger'
    
    # Security flows
    elif source_cat == 'security' and target_cat == 'network':
        return 'Security Filter'
    
    # Monitoring flows
    elif target_cat == 'management':
        return 'Monitoring'
    
    # Default
    else:
        return 'Data Flow'


@tool
def extract_data_flows(architecture_design: str) -> str:
    """
    Extract and structure data flows from architecture design for YAML conversion.
    
    This tool specifically focuses on identifying data flow patterns, request/response paths,
    and integration points from the architecture design text to create accurate relationship
    mappings in the YAML output.
    
    Args:
        architecture_design: The complete architecture design text output from aws_architecture_designer
    
    Returns:
        Structured analysis of data flows including:
        - Request/response flow patterns
        - Service integration points
        - Data transformation paths
        - Authentication flows
        - Error handling paths
        - Caching patterns
    """
    
    # Parse the architecture design to extract data flows
    flows = []
    
    # Look for common flow patterns
    flow_patterns = [
        r'users?\s*->\s*(\w+)',
        r'internet\s*->\s*(\w+)',
        r'(\w+)\s*->\s*(\w+)',
        r'(\w+)\s*connects?\s*to\s*(\w+)',
        r'(\w+)\s*communicates?\s*with\s*(\w+)',
        r'(\w+)\s*accesses?\s*(\w+)',
        r'(\w+)\s*sends?\s*to\s*(\w+)',
        r'(\w+)\s*receives?\s*from\s*(\w+)'
    ]
    
    architecture_lower = architecture_design.lower()
    
    for pattern in flow_patterns:
        matches = re.findall(pattern, architecture_lower)
        for match in matches:
            if isinstance(match, tuple) and len(match) == 2:
                flows.append({
                    "source": match[0].strip(),
                    "target": match[1].strip(),
                    "type": "data_flow"
                })
            elif isinstance(match, str):
                flows.append({
                    "source": "user",
                    "target": match.strip(),
                    "type": "user_flow"
                })
    
    return json.dumps(flows, indent=2) 


def should_connect_services(source_component, target_component, architecture_text):
    """Determine if two services should be logically connected based on their types and context."""
    
    source_type = source_component['type'].lower()
    target_type = target_component['type'].lower()
    source_name = source_component['name'].lower()
    target_name = target_component['name'].lower()
    
    # Network to compute connections
    if 'network' in source_type and 'compute' in target_type:
        return True
    
    # Compute to database connections
    if 'compute' in source_type and 'database' in target_type:
        return True
    
    # Compute to storage connections
    if 'compute' in source_type and 'storage' in target_type:
        return True
    
    # Compute to integration connections
    if 'compute' in source_type and 'integration' in target_type:
        return True
    
    # Integration to compute connections (event-driven)
    if 'integration' in source_type and 'compute' in target_type:
        return True
    
    # Security to network connections
    if 'security' in source_type and 'network' in target_type:
        return True
    
    # User to network connections
    if 'user' in source_name and 'network' in target_type:
        return True
    
    # Internet to network connections
    if 'internet' in source_name and 'network' in target_type:
        return True
    
    # Skip connections between services of the same category (unless they're adjacent)
    source_cat = get_service_category(source_type)
    target_cat = get_service_category(target_type)
    
    if source_cat == target_cat:
        return False
    
    return False


def create_logical_relationship(source_component, target_component):
    """Create a logical relationship between two components."""
    
    source_type = source_component['type'].lower()
    target_type = target_component['type'].lower()
    
    # Get appropriate label based on service types
    label = get_relationship_label(source_type, target_type)
    
    return {
        "to": target_component['id'],
        "direction": "outgoing",
        "label": label
    } 