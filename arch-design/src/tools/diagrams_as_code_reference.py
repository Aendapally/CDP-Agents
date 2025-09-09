"""
Diagrams-as-Code Reference Examples

This module provides comprehensive examples of diagrams-as-code YAML structures
for the agent to reference when converting AWS architecture designs to YAML format.
"""

# Complete examples from the diagrams-as-code repository
DIAGRAMS_AS_CODE_EXAMPLES = {
    
    "simple_web_services": {
        "description": "Basic web services architecture with ELB, ECS, and RDS",
        "yaml": """diagram:
  name: Web Services Architecture on AWS
  open: true
  resources:
    - id: dns
      name: DNS
      type: aws.network.Route53
      relates:
        - to: elb
          direction: outgoing
    - id: elb
      name: ELB
      type: aws.network.ELB
      relates:
        - to: web-services.graphql-api
          direction: outgoing
    - id: web-services
      name: Web Services
      type: cluster
      of:
        - id: graphql-api
          name: GraphQL API
          type: group
          of:
            - id: first-api
              name: GraphQL API №1
              type: aws.compute.ECS
            - id: second-api
              name: GraphQL API №2
              type: aws.compute.ECS
            - id: third-api
              name: GraphQL API №3
              type: aws.compute.ECS
          relates:
            - to: databases.leader
              direction: outgoing
            - to: memcached
              direction: outgoing
    - id: databases
      name: Databases
      type: cluster
      of:
        - id: leader
          name: R/W Leader
          type: aws.database.RDS
          relates:
            - to: databases.followers
              direction: undirected
        - id: followers
          name: R/O Followers
          type: group
          of:
            - id: first-follower
              name: R/O Follower №1
              type: aws.database.RDS
            - id: second-follower
              name: R/O Follower №2
              type: aws.database.RDS
    - id: memcached
      name: Memcached
      type: aws.database.ElastiCache""",
        "patterns": [
            "Basic load balancer to application cluster",
            "Database cluster with leader/follower setup",
            "Caching layer with ElastiCache",
            "DNS routing with Route53"
        ]
    },
    
    "events_processing": {
        "description": "Event-driven architecture with SQS, Lambda, and storage",
        "yaml": """diagram:
  name: Events Processing Architecture on AWS
  open: true
  resources:
    - id: web-service
      name: Web Service (Source)
      type: aws.compute.EKS
      relates:
        - to: events-flow.workers.workers
          direction: outgoing
    - id: storage
      name: Events Storage
      type: aws.storage.S3
    - id: analytics
      name: Events Analytics
      type: aws.database.Redshift
    - id: events-flow
      name: Events Flow
      type: cluster
      of:
        - id: queue
          name: Events Queue
          type: aws.integration.SQS
          relates:
            - to: events-flow.processing.lambdas
              direction: outgoing
        - id: workers
          name: Workers
          type: cluster
          of:
            - id: workers
              name: Workers
              type: group
              of:
                - id: first-worker
                  name: Worker №1
                  type: aws.compute.ECS
                - id: second-worker
                  name: Worker №2
                  type: aws.compute.ECS
                - id: third-worker
                  name: Worker №3
                  type: aws.compute.ECS
              relates:
                - to: events-flow.queue
                  direction: outgoing
        - id: processing
          name: Processing
          type: cluster
          of:
            - id: lambdas
              name: Lambdas
              type: group
              of:
                - id: first-process
                  name: Lambda №1
                  type: aws.compute.Lambda
                - id: second-process
                  name: Lambda №2
                  type: aws.compute.Lambda
                - id: third-process
                  name: Lambda №3
                  type: aws.compute.Lambda
              relates:
                - to: storage
                  direction: outgoing
                - to: analytics
                  direction: outgoing""",
        "patterns": [
            "Event-driven processing with SQS",
            "Lambda function groups for processing",
            "S3 for storage and Redshift for analytics",
            "Nested clusters for complex workflows",
            "Worker pattern with ECS containers"
        ]
    },
    
    "complete_example": {
        "description": "Complete example showing all YAML features and styling",
        "yaml": """diagram:
  name: Web Services Architecture on AWS
  file_name: web-services-architecture-aws
  format: jpg
  direction: left-to-right
  style:
    graph:
      splines: ortho
    node:
      shape: circle
    edge:
      color: '#000000'
  label_resources: false
  open: true
  resources:
    - id: dns
      name: DNS
      type: aws.network.Route53
      relates:
        - to: elb
          direction: outgoing
          label: Makes Request
          color: brown
          style: dotted
    - id: elb
      name: ELB
      type: aws.network.ELB
      relates:
        - to: web-services.graphql-api
          direction: outgoing
          label: Proxy Request
          color: firebrick
          style: dashed
    - id: web-services
      name: Web Services
      type: cluster
      of:
        - id: graphql-api
          name: GraphQL API
          type: group
          of:
            - id: first-ecs
              name: GraphQL API №1
              type: aws.compute.ECS
            - id: second-ecs
              name: GraphQL API №2
              type: aws.compute.ECS
          relates:
            - to: databases.leader
              direction: outgoing
    - id: databases
      name: Databases
      type: cluster
      of:
        - id: leader
          name: R/W Leader
          type: aws.database.RDS
          relates:
            - to: databases.follower
              direction: undirected
        - id: follower
          name: R/O Follower
          type: aws.database.RDS""",
        "patterns": [
            "Custom styling with graph, node, and edge styles",
            "Relationship labels and colors",
            "Custom file naming and format",
            "Direction control (left-to-right)",
            "Style attributes (dotted, dashed lines)"
        ]
    },
    
    "simple_workers": {
        "description": "Simple workers architecture with load balancer and EC2 instances",
        "yaml": """diagram:
  name: Workers Architecture on AWS
  direction: top-to-bottom
  open: true
  resources:
    - id: elb
      name: ELB
      type: aws.network.ELB
      relates:
        - to: workers
          direction: outgoing
    - id: workers
      name: Workers
      type: group
      of:
        - id: first-worker
          name: Worker №1
          type: aws.compute.EC2
        - id: second-worker
          name: Worker №2
          type: aws.compute.EC2
        - id: third-worker
          name: Worker №3
          type: aws.compute.EC2
        - id: fourth-worker
          name: Worker №4
          type: aws.compute.EC2
        - id: fifth-worker
          name: Worker №5
          type: aws.compute.EC2
        - id: sixth-worker
          name: Worker №6
          type: aws.compute.EC2
      relates:
        - to: database
          direction: outgoing
    - id: database
      name: Events
      type: aws.database.RDS""",
        "patterns": [
            "Worker group pattern with multiple EC2 instances",
            "Top-to-bottom direction layout",
            "Simple load balancer to workers to database flow",
            "Group type for similar resources"
        ]
    }
}

# Complete AWS service type mappings based on diagrams-as-code schema
AWS_SERVICE_TYPES = {
    # Analytics Services
    "aws.analytics.Analytics": "AWS Analytics",
    "aws.analytics.Athena": "Amazon Athena",
    "aws.analytics.CloudsearchSearchDocuments": "CloudSearch Search Documents",
    "aws.analytics.Cloudsearch": "Amazon CloudSearch",
    "aws.analytics.DataLakeResource": "Data Lake Resource",
    "aws.analytics.DataPipeline": "AWS Data Pipeline",
    "aws.analytics.ElasticsearchService": "Amazon Elasticsearch Service",
    "aws.analytics.ES": "Amazon ES",
    "aws.analytics.EMRCluster": "Amazon EMR Cluster",
    "aws.analytics.EMREngineMaprM3": "EMR Engine MapR M3",
    "aws.analytics.EMREngineMaprM5": "EMR Engine MapR M5",
    "aws.analytics.EMREngineMaprM7": "EMR Engine MapR M7",
    "aws.analytics.EMREngine": "Amazon EMR Engine",
    "aws.analytics.EMRHdfsCluster": "EMR HDFS Cluster",
    "aws.analytics.EMR": "Amazon EMR",
    "aws.analytics.GlueCrawlers": "AWS Glue Crawlers",
    "aws.analytics.GlueDataCatalog": "AWS Glue Data Catalog",
    "aws.analytics.Glue": "AWS Glue",
    "aws.analytics.KinesisDataAnalytics": "Amazon Kinesis Data Analytics",
    "aws.analytics.KinesisDataFirehose": "Amazon Kinesis Data Firehose",
    "aws.analytics.KinesisDataStreams": "Amazon Kinesis Data Streams",
    "aws.analytics.KinesisVideoStreams": "Amazon Kinesis Video Streams",
    "aws.analytics.Kinesis": "Amazon Kinesis",
    "aws.analytics.LakeFormation": "AWS Lake Formation",
    "aws.analytics.ManagedStreamingForKafka": "Amazon MSK",
    "aws.analytics.Quicksight": "Amazon QuickSight",
    "aws.analytics.RedshiftDenseComputeNode": "Redshift Dense Compute Node",
    "aws.analytics.RedshiftDenseStorageNode": "Redshift Dense Storage Node",
    "aws.analytics.Redshift": "Amazon Redshift",

    # AR/VR Services
    "aws.ar.ArVr": "AWS AR/VR",
    "aws.ar.Sumerian": "Amazon Sumerian",

    # Blockchain Services
    "aws.blockchain.BlockchainResource": "Blockchain Resource",
    "aws.blockchain.Blockchain": "Amazon Blockchain",
    "aws.blockchain.ManagedBlockchain": "Amazon Managed Blockchain",
    "aws.blockchain.QuantumLedgerDatabaseQldb": "Amazon QLDB",
    "aws.blockchain.QLDB": "Amazon QLDB",

    # Business Applications
    "aws.business.AlexaForBusiness": "Alexa for Business",
    "aws.business.A4B": "Alexa for Business",
    "aws.business.BusinessApplications": "Business Applications",
    "aws.business.Chime": "Amazon Chime",
    "aws.business.Workmail": "Amazon WorkMail",

    # Compute Services
    "aws.compute.AppRunner": "AWS App Runner",
    "aws.compute.ApplicationAutoScaling": "Application Auto Scaling",
    "aws.compute.AutoScaling": "AWS Auto Scaling",
    "aws.compute.Batch": "AWS Batch",
    "aws.compute.ComputeOptimizer": "AWS Compute Optimizer",
    "aws.compute.Compute": "AWS Compute",
    "aws.compute.EC2Ami": "Amazon EC2 AMI",
    "aws.compute.AMI": "Amazon Machine Image",
    "aws.compute.EC2AutoScaling": "EC2 Auto Scaling",
    "aws.compute.EC2ContainerRegistryImage": "ECR Image",
    "aws.compute.EC2ContainerRegistryRegistry": "ECR Registry",
    "aws.compute.EC2ContainerRegistry": "Amazon ECR",
    "aws.compute.ECR": "Amazon ECR",
    "aws.compute.EC2ElasticIpAddress": "EC2 Elastic IP",
    "aws.compute.EC2ImageBuilder": "EC2 Image Builder",
    "aws.compute.EC2Instance": "EC2 Instance",
    "aws.compute.EC2Instances": "EC2 Instances",
    "aws.compute.EC2Rescue": "EC2 Rescue",
    "aws.compute.EC2SpotInstance": "EC2 Spot Instance",
    "aws.compute.EC2": "Amazon EC2",
    "aws.compute.ElasticBeanstalkApplication": "Elastic Beanstalk Application",
    "aws.compute.ElasticBeanstalkDeployment": "Elastic Beanstalk Deployment",
    "aws.compute.ElasticBeanstalk": "AWS Elastic Beanstalk",
    "aws.compute.EB": "AWS Elastic Beanstalk",
    "aws.compute.ElasticContainerServiceContainer": "ECS Container",
    "aws.compute.ElasticContainerServiceService": "ECS Service",
    "aws.compute.ElasticContainerService": "Amazon ECS",
    "aws.compute.ECS": "Amazon ECS",
    "aws.compute.ElasticKubernetesService": "Amazon EKS",
    "aws.compute.EKS": "Amazon EKS",
    "aws.compute.Fargate": "AWS Fargate",
    "aws.compute.LambdaFunction": "Lambda Function",
    "aws.compute.Lambda": "AWS Lambda",
    "aws.compute.Lightsail": "Amazon Lightsail",
    "aws.compute.LocalZones": "AWS Local Zones",
    "aws.compute.Outposts": "AWS Outposts",
    "aws.compute.ServerlessApplicationRepository": "Serverless Application Repository",
    "aws.compute.SAR": "Serverless Application Repository",
    "aws.compute.ThinkboxDeadline": "Thinkbox Deadline",
    "aws.compute.ThinkboxDraft": "Thinkbox Draft",
    "aws.compute.ThinkboxFrost": "Thinkbox Frost",
    "aws.compute.ThinkboxKrakatoa": "Thinkbox Krakatoa",
    "aws.compute.ThinkboxSequoia": "Thinkbox Sequoia",
    "aws.compute.ThinkboxStoke": "Thinkbox Stoke",
    "aws.compute.ThinkboxXmesh": "Thinkbox XMesh",
    "aws.compute.VmwareCloudOnAWS": "VMware Cloud on AWS",
    "aws.compute.Wavelength": "AWS Wavelength",

    # Cost Management
    "aws.cost.Budgets": "AWS Budgets",
    "aws.cost.CostAndUsageReport": "Cost and Usage Report",
    "aws.cost.CostExplorer": "AWS Cost Explorer",
    "aws.cost.CostManagement": "AWS Cost Management",
    "aws.cost.ReservedInstanceReporting": "Reserved Instance Reporting",
    "aws.cost.SavingsPlans": "AWS Savings Plans",

    # Database Services
    "aws.database.AuroraInstance": "Aurora Instance",
    "aws.database.Aurora": "Amazon Aurora",
    "aws.database.DatabaseMigrationServiceDatabaseMigrationWorkflow": "DMS Workflow",
    "aws.database.DatabaseMigrationService": "AWS Database Migration Service",
    "aws.database.DMS": "AWS DMS",
    "aws.database.Database": "Database",
    "aws.database.DB": "Database",
    "aws.database.DocumentdbMongodbCompatibility": "Amazon DocumentDB",
    "aws.database.DocumentDB": "Amazon DocumentDB",
    "aws.database.DynamodbAttribute": "DynamoDB Attribute",
    "aws.database.DynamodbAttributes": "DynamoDB Attributes",
    "aws.database.DynamodbDax": "DynamoDB DAX",
    "aws.database.DAX": "DynamoDB Accelerator",
    "aws.database.DynamodbGlobalSecondaryIndex": "DynamoDB GSI",
    "aws.database.DynamodbGSI": "DynamoDB GSI",
    "aws.database.DynamodbItem": "DynamoDB Item",
    "aws.database.DynamodbItems": "DynamoDB Items",
    "aws.database.DynamodbTable": "DynamoDB Table",
    "aws.database.Dynamodb": "Amazon DynamoDB",
    "aws.database.DDB": "Amazon DynamoDB",
    "aws.database.ElasticacheCacheNode": "ElastiCache Cache Node",
    "aws.database.ElasticacheForMemcached": "ElastiCache for Memcached",
    "aws.database.ElasticacheForRedis": "ElastiCache for Redis",
    "aws.database.Elasticache": "Amazon ElastiCache",
    "aws.database.ElastiCache": "Amazon ElastiCache",
    "aws.database.KeyspacesManagedApacheCassandraService": "Amazon Keyspaces",
    "aws.database.Neptune": "Amazon Neptune",
    "aws.database.QuantumLedgerDatabaseQldb": "Amazon QLDB",
    "aws.database.QLDB": "Amazon QLDB",
    "aws.database.RDSInstance": "RDS Instance",
    "aws.database.RDSMariadbInstance": "RDS MariaDB Instance",
    "aws.database.RDSMysqlInstance": "RDS MySQL Instance",
    "aws.database.RDSOnVmware": "RDS on VMware",
    "aws.database.RDSOracleInstance": "RDS Oracle Instance",
    "aws.database.RDSPostgresqlInstance": "RDS PostgreSQL Instance",
    "aws.database.RDSSqlServerInstance": "RDS SQL Server Instance",
    "aws.database.RDS": "Amazon RDS",
    "aws.database.RedshiftDenseComputeNode": "Redshift Dense Compute Node",
    "aws.database.RedshiftDenseStorageNode": "Redshift Dense Storage Node",
    "aws.database.Redshift": "Amazon Redshift",
    "aws.database.Timestream": "Amazon Timestream",

    # DevTools Services
    "aws.devtools.CloudDevelopmentKit": "AWS CDK",
    "aws.devtools.Cloud9Resource": "Cloud9 Resource",
    "aws.devtools.Cloud9": "AWS Cloud9",
    "aws.devtools.Codebuild": "AWS CodeBuild",
    "aws.devtools.Codecommit": "AWS CodeCommit",
    "aws.devtools.Codedeploy": "AWS CodeDeploy",
    "aws.devtools.Codepipeline": "AWS CodePipeline",
    "aws.devtools.Codestar": "AWS CodeStar",
    "aws.devtools.CommandLineInterface": "AWS CLI",
    "aws.devtools.CLI": "AWS CLI",
    "aws.devtools.DeveloperTools": "Developer Tools",
    "aws.devtools.DevTools": "Developer Tools",
    "aws.devtools.ToolsAndSdks": "Tools and SDKs",
    "aws.devtools.XRay": "AWS X-Ray",

    # General Services
    "aws.general.Client": "Client",
    "aws.general.Disk": "Disk",
    "aws.general.Forums": "Forums",
    "aws.general.General": "General",
    "aws.general.GenericDatabase": "Generic Database",
    "aws.general.GenericFirewall": "Generic Firewall",
    "aws.general.GenericOfficeBuilding": "Generic Office Building",
    "aws.general.OfficeBuilding": "Office Building",
    "aws.general.GenericSamlToken": "Generic SAML Token",
    "aws.general.GenericSDK": "Generic SDK",
    "aws.general.InternetAlt1": "Internet Alt 1",
    "aws.general.InternetAlt2": "Internet Alt 2",
    "aws.general.InternetGateway": "Internet Gateway",
    "aws.general.Marketplace": "AWS Marketplace",
    "aws.general.MobileClient": "Mobile Client",
    "aws.general.Multimedia": "Multimedia",
    "aws.general.SamlToken": "SAML Token",
    "aws.general.SDK": "SDK",
    "aws.general.SslPadlock": "SSL Padlock",
    "aws.general.TapeStorage": "Tape Storage",
    "aws.general.Toolkit": "Toolkit",
    "aws.general.TraditionalServer": "Traditional Server",
    "aws.general.User": "User",
    "aws.general.Users": "Users",

    # Integration Services
    "aws.integration.ApplicationIntegration": "Application Integration",
    "aws.integration.Appsync": "AWS AppSync",
    "aws.integration.ConsoleMobileApplication": "Console Mobile Application",
    "aws.integration.EventResource": "Event Resource",
    "aws.integration.EventbridgeCustomEventBusResource": "EventBridge Custom Event Bus",
    "aws.integration.EventbridgeDefaultEventBusResource": "EventBridge Default Event Bus",
    "aws.integration.EventbridgeSaasPartnerEventBusResource": "EventBridge SaaS Partner Event Bus",
    "aws.integration.Eventbridge": "Amazon EventBridge",
    "aws.integration.ExpressWorkflows": "Express Workflows",
    "aws.integration.MQ": "Amazon MQ",
    "aws.integration.SimpleNotificationServiceSnsEmailNotification": "SNS Email Notification",
    "aws.integration.SimpleNotificationServiceSnsHttpNotification": "SNS HTTP Notification",
    "aws.integration.SimpleNotificationServiceSnsTopic": "SNS Topic",
    "aws.integration.SimpleNotificationServiceSns": "Amazon SNS",
    "aws.integration.SNS": "Amazon SNS",
    "aws.integration.SimpleQueueServiceSqsMessage": "SQS Message",
    "aws.integration.SimpleQueueServiceSqsQueue": "SQS Queue",
    "aws.integration.SimpleQueueServiceSqs": "Amazon SQS",
    "aws.integration.SQS": "Amazon SQS",
    "aws.integration.StepFunctions": "AWS Step Functions",
    "aws.integration.SF": "AWS Step Functions",

    # Management Services
    "aws.management.AutoScaling": "AWS Auto Scaling",
    "aws.management.Chatbot": "AWS Chatbot",
    "aws.management.CloudformationChangeSet": "CloudFormation Change Set",
    "aws.management.CloudformationStack": "CloudFormation Stack",
    "aws.management.CloudformationTemplate": "CloudFormation Template",
    "aws.management.Cloudformation": "AWS CloudFormation",
    "aws.management.Cloudtrail": "AWS CloudTrail",
    "aws.management.CloudwatchAlarm": "CloudWatch Alarm",
    "aws.management.CloudwatchEventEventBased": "CloudWatch Event (Event-based)",
    "aws.management.CloudwatchEventTimeBased": "CloudWatch Event (Time-based)",
    "aws.management.CloudwatchRule": "CloudWatch Rule",
    "aws.management.Cloudwatch": "Amazon CloudWatch",
    "aws.management.Codeguru": "Amazon CodeGuru",
    "aws.management.CommandLineInterface": "AWS CLI",
    "aws.management.Config": "AWS Config",
    "aws.management.ControlTower": "AWS Control Tower",
    "aws.management.LicenseManager": "AWS License Manager",
    "aws.management.ManagedServices": "AWS Managed Services",
    "aws.management.ManagementAndGovernance": "Management and Governance",
    "aws.management.ManagementConsole": "AWS Management Console",
    "aws.management.OpsworksApps": "AWS OpsWorks Apps",
    "aws.management.OpsworksDeployments": "AWS OpsWorks Deployments",
    "aws.management.OpsworksInstances": "AWS OpsWorks Instances",
    "aws.management.OpsworksLayers": "AWS OpsWorks Layers",
    "aws.management.OpsworksMonitoring": "AWS OpsWorks Monitoring",
    "aws.management.OpsworksPermissions": "AWS OpsWorks Permissions",
    "aws.management.OpsworksResources": "AWS OpsWorks Resources",
    "aws.management.OpsworksStack": "AWS OpsWorks Stack",
    "aws.management.Opsworks": "AWS OpsWorks",
    "aws.management.OrganizationsAccount": "AWS Organizations Account",
    "aws.management.OrganizationsOrganizationalUnit": "AWS Organizations OU",
    "aws.management.Organizations": "AWS Organizations",
    "aws.management.PersonalHealthDashboard": "Personal Health Dashboard",
    "aws.management.ServiceCatalog": "AWS Service Catalog",
    "aws.management.SystemsManagerAutomation": "Systems Manager Automation",
    "aws.management.SystemsManagerDocuments": "Systems Manager Documents",
    "aws.management.SystemsManagerInventory": "Systems Manager Inventory",
    "aws.management.SystemsManagerMaintenanceWindows": "Systems Manager Maintenance Windows",
    "aws.management.SystemsManagerOpscenter": "Systems Manager OpsCenter",
    "aws.management.SystemsManagerParameterStore": "Systems Manager Parameter Store",
    "aws.management.ParameterStore": "Parameter Store",
    "aws.management.SystemsManagerPatchManager": "Systems Manager Patch Manager",
    "aws.management.SystemsManagerRunCommand": "Systems Manager Run Command",
    "aws.management.SystemsManagerStateManager": "Systems Manager State Manager",
    "aws.management.SystemsManager": "AWS Systems Manager",
    "aws.management.SSM": "AWS Systems Manager",
    "aws.management.TrustedAdvisorChecklistCost": "Trusted Advisor Cost Checklist",
    "aws.management.TrustedAdvisorChecklistFaultTolerant": "Trusted Advisor Fault Tolerant Checklist",
    "aws.management.TrustedAdvisorChecklistPerformance": "Trusted Advisor Performance Checklist",
    "aws.management.TrustedAdvisorChecklistSecurity": "Trusted Advisor Security Checklist",
    "aws.management.TrustedAdvisorChecklist": "Trusted Advisor Checklist",
    "aws.management.TrustedAdvisor": "AWS Trusted Advisor",
    "aws.management.WellArchitectedTool": "AWS Well-Architected Tool",

    # Mobile Services
    "aws.mobile.Amplify": "AWS Amplify",
    "aws.mobile.APIGatewayEndpoint": "API Gateway Endpoint",
    "aws.mobile.APIGateway": "Amazon API Gateway",
    "aws.mobile.Appsync": "AWS AppSync",
    "aws.mobile.DeviceFarm": "AWS Device Farm",
    "aws.mobile.Mobile": "AWS Mobile",
    "aws.mobile.Pinpoint": "Amazon Pinpoint",

    # Network Services
    "aws.network.APIGatewayEndpoint": "API Gateway Endpoint",
    "aws.network.APIGateway": "Amazon API Gateway",
    "aws.network.AppMesh": "AWS App Mesh",
    "aws.network.ClientVpn": "AWS Client VPN",
    "aws.network.CloudMap": "AWS Cloud Map",
    "aws.network.CloudFrontDownloadDistribution": "CloudFront Download Distribution",
    "aws.network.CloudFrontEdgeLocation": "CloudFront Edge Location",
    "aws.network.CloudFrontStreamingDistribution": "CloudFront Streaming Distribution",
    "aws.network.CloudFront": "Amazon CloudFront",
    "aws.network.CF": "Amazon CloudFront",
    "aws.network.DirectConnect": "AWS Direct Connect",
    "aws.network.ElasticLoadBalancing": "Elastic Load Balancing",
    "aws.network.ELB": "Classic Load Balancer",
    "aws.network.ElbApplicationLoadBalancer": "Application Load Balancer",
    "aws.network.ALB": "Application Load Balancer",
    "aws.network.ElbClassicLoadBalancer": "Classic Load Balancer",
    "aws.network.CLB": "Classic Load Balancer",
    "aws.network.ElbNetworkLoadBalancer": "Network Load Balancer",
    "aws.network.NLB": "Network Load Balancer",
    "aws.network.Endpoint": "VPC Endpoint",
    "aws.network.GlobalAccelerator": "AWS Global Accelerator",
    "aws.network.GAX": "AWS Global Accelerator",
    "aws.network.InternetGateway": "Internet Gateway",
    "aws.network.Nacl": "Network ACL",
    "aws.network.NATGateway": "NAT Gateway",
    "aws.network.NetworkingAndContentDelivery": "Networking and Content Delivery",
    "aws.network.PrivateSubnet": "Private Subnet",
    "aws.network.Privatelink": "AWS PrivateLink",
    "aws.network.PublicSubnet": "Public Subnet",
    "aws.network.Route53HostedZone": "Route 53 Hosted Zone",
    "aws.network.Route53": "Amazon Route 53",
    "aws.network.RouteTable": "Route Table",
    "aws.network.SiteToSiteVpn": "Site-to-Site VPN",
    "aws.network.TransitGateway": "AWS Transit Gateway",
    "aws.network.VPCCustomerGateway": "VPC Customer Gateway",
    "aws.network.VPCElasticNetworkAdapter": "VPC Elastic Network Adapter",
    "aws.network.VPCElasticNetworkInterface": "VPC Elastic Network Interface",
    "aws.network.VPCFlowLogs": "VPC Flow Logs",
    "aws.network.VPCPeering": "VPC Peering",
    "aws.network.VPCRouter": "VPC Router",
    "aws.network.VPCTrafficMirroring": "VPC Traffic Mirroring",
    "aws.network.VPC": "Amazon VPC",
    "aws.network.VpnConnection": "VPN Connection",
    "aws.network.VpnGateway": "VPN Gateway",

    # Security Services
    "aws.security.AdConnector": "AD Connector",
    "aws.security.Artifact": "AWS Artifact",
    "aws.security.CertificateAuthority": "AWS Certificate Authority",
    "aws.security.CertificateManager": "AWS Certificate Manager",
    "aws.security.ACM": "AWS Certificate Manager",
    "aws.security.CloudDirectory": "Amazon Cloud Directory",
    "aws.security.Cloudhsm": "AWS CloudHSM",
    "aws.security.CloudHSM": "AWS CloudHSM",
    "aws.security.Cognito": "Amazon Cognito",
    "aws.security.Detective": "Amazon Detective",
    "aws.security.DirectoryService": "AWS Directory Service",
    "aws.security.DS": "AWS Directory Service",
    "aws.security.FirewallManager": "AWS Firewall Manager",
    "aws.security.FMS": "AWS Firewall Manager",
    "aws.security.Guardduty": "Amazon GuardDuty",
    "aws.security.IdentityAndAccessManagementIamAccessAnalyzer": "IAM Access Analyzer",
    "aws.security.IAMAccessAnalyzer": "IAM Access Analyzer",
    "aws.security.IdentityAndAccessManagementIamAddOn": "IAM Add-On",
    "aws.security.IdentityAndAccessManagementIamAWSStsAlternate": "IAM AWS STS Alternate",
    "aws.security.IdentityAndAccessManagementIamAWSSts": "IAM AWS STS",
    "aws.security.IAMAWSSts": "IAM AWS STS",
    "aws.security.IdentityAndAccessManagementIamDataEncryptionKey": "IAM Data Encryption Key",
    "aws.security.IdentityAndAccessManagementIamEncryptedData": "IAM Encrypted Data",
    "aws.security.IdentityAndAccessManagementIamLongTermSecurityCredential": "IAM Long-term Security Credential",
    "aws.security.IdentityAndAccessManagementIamMfaToken": "IAM MFA Token",
    "aws.security.IdentityAndAccessManagementIamPermissions": "IAM Permissions",
    "aws.security.IAMPermissions": "IAM Permissions",
    "aws.security.IdentityAndAccessManagementIamRole": "IAM Role",
    "aws.security.IAMRole": "IAM Role",
    "aws.security.IdentityAndAccessManagementIamTemporarySecurityCredential": "IAM Temporary Security Credential",
    "aws.security.IdentityAndAccessManagementIam": "AWS IAM",
    "aws.security.IAM": "AWS IAM",
    "aws.security.InspectorAgent": "Amazon Inspector Agent",
    "aws.security.Inspector": "Amazon Inspector",
    "aws.security.KeyManagementService": "AWS Key Management Service",
    "aws.security.KMS": "AWS KMS",
    "aws.security.Macie": "Amazon Macie",
    "aws.security.ManagedMicrosoftAd": "AWS Managed Microsoft AD",
    "aws.security.ResourceAccessManager": "AWS Resource Access Manager",
    "aws.security.RAM": "AWS Resource Access Manager",
    "aws.security.SecretsManager": "AWS Secrets Manager",
    "aws.security.SecurityHubFinding": "Security Hub Finding",
    "aws.security.SecurityHub": "AWS Security Hub",
    "aws.security.SecurityIdentityAndCompliance": "Security, Identity, and Compliance",
    "aws.security.ShieldAdvanced": "AWS Shield Advanced",
    "aws.security.Shield": "AWS Shield",
    "aws.security.SimpleAd": "Simple AD",
    "aws.security.SingleSignOn": "AWS Single Sign-On",
    "aws.security.WAFFilteringRule": "WAF Filtering Rule",
    "aws.security.WAF": "AWS WAF",

    # Storage Services
    "aws.storage.Backup": "AWS Backup",
    "aws.storage.CloudendureDisasterRecovery": "CloudEndure Disaster Recovery",
    "aws.storage.CDR": "CloudEndure Disaster Recovery",
    "aws.storage.EFSInfrequentaccessPrimaryBg": "EFS Infrequent Access",
    "aws.storage.EFSStandardPrimaryBg": "EFS Standard",
    "aws.storage.ElasticBlockStoreEBSSnapshot": "EBS Snapshot",
    "aws.storage.ElasticBlockStoreEBSVolume": "EBS Volume",
    "aws.storage.ElasticBlockStoreEBS": "Amazon EBS",
    "aws.storage.EBS": "Amazon EBS",
    "aws.storage.ElasticFileSystemEFSFileSystem": "EFS File System",
    "aws.storage.ElasticFileSystemEFS": "Amazon EFS",
    "aws.storage.EFS": "Amazon EFS",
    "aws.storage.FsxForLustre": "FSx for Lustre",
    "aws.storage.FsxForWindowsFileServer": "FSx for Windows File Server",
    "aws.storage.Fsx": "Amazon FSx",
    "aws.storage.FSx": "Amazon FSx",
    "aws.storage.MultipleVolumesResource": "Multiple Volumes Resource",
    "aws.storage.S3GlacierArchive": "S3 Glacier Archive",
    "aws.storage.S3GlacierVault": "S3 Glacier Vault",
    "aws.storage.S3Glacier": "Amazon S3 Glacier",
    "aws.storage.SimpleStorageServiceS3BucketWithObjects": "S3 Bucket with Objects",
    "aws.storage.SimpleStorageServiceS3Bucket": "S3 Bucket",
    "aws.storage.SimpleStorageServiceS3Object": "S3 Object",
    "aws.storage.SimpleStorageServiceS3": "Amazon S3",
    "aws.storage.S3": "Amazon S3",
    "aws.storage.SnowFamilySnowballImportExport": "Snow Family Snowball Import/Export",
    "aws.storage.SnowballEdge": "AWS Snowball Edge",
    "aws.storage.Snowball": "AWS Snowball",
    "aws.storage.Snowmobile": "AWS Snowmobile",
    "aws.storage.StorageGatewayCachedVolume": "Storage Gateway Cached Volume",
    "aws.storage.StorageGatewayNonCachedVolume": "Storage Gateway Non-Cached Volume",
    "aws.storage.StorageGatewayVirtualTapeLibrary": "Storage Gateway Virtual Tape Library",
    "aws.storage.StorageGateway": "AWS Storage Gateway",
    "aws.storage.Storage": "Storage",

    # Generic Services
    "generic.blank.Blank": "Blank",
    "generic.compute.Rack": "Compute Rack",
    "generic.database.SQL": "SQL Database",
    "generic.device.Mobile": "Mobile Device",
    "generic.device.Tablet": "Tablet",
    "generic.network.Firewall": "Firewall",
    "generic.network.Router": "Router",
    "generic.network.Subnet": "Subnet",
    "generic.network.Switch": "Switch",
    "generic.network.VPN": "VPN",
    "generic.network.Internet": "Internet",
    "generic.os.Android": "Android",
    "generic.os.Centos": "CentOS",
    "generic.os.Debian": "Debian",
    "generic.os.IOS": "iOS",
    "generic.os.LinuxGeneral": "Linux",
    "generic.os.Raspbian": "Raspbian",
    "generic.os.RedHat": "Red Hat",
    "generic.os.Suse": "SUSE",
    "generic.os.Ubuntu": "Ubuntu",
    "generic.os.Windows": "Windows",
    "generic.place.Datacenter": "Datacenter",
    "generic.storage.Storage": "Storage",
    "generic.virtualization.Virtualbox": "VirtualBox",
    "generic.virtualization.Vmware": "VMware",
    "generic.virtualization.XEN": "XEN"
}

# Structure patterns for common architectures
ARCHITECTURE_PATTERNS = {
    "web_application": {
        "description": "Standard web application pattern",
        "components": [
            "aws.network.Route53",
            "aws.network.CloudFront", 
            "aws.network.ElbApplicationLoadBalancer",
            "aws.compute.ECS",
            "aws.database.RDS",
            "aws.database.ElastiCache"
        ],
        "relationships": [
            "Route53 → CloudFront → ALB → ECS → RDS",
            "ECS → ElastiCache (caching)"
        ]
    },
    
    "microservices": {
        "description": "Microservices architecture pattern",
        "components": [
            "aws.network.APIGateway",
            "aws.compute.Lambda",
            "aws.compute.ECS",
            "aws.database.Dynamodb",
            "aws.integration.SQS",
            "aws.integration.SNS"
        ],
        "relationships": [
            "API Gateway → Lambda/ECS services",
            "Services → DynamoDB",
            "Services → SQS → SNS"
        ]
    },
    
    "event_driven": {
        "description": "Event-driven architecture pattern",
        "components": [
            "aws.integration.SQS",
            "aws.integration.SNS",
            "aws.compute.Lambda",
            "aws.analytics.Kinesis",
            "aws.storage.S3"
        ],
        "relationships": [
            "Source → SQS → Lambda → Target",
            "Events → Kinesis → S3 (storage)",
            "SNS for fanout patterns"
        ]
    },
    
    "data_processing": {
        "description": "Data processing and analytics pattern",
        "components": [
            "aws.analytics.Kinesis",
            "aws.compute.Lambda",
            "aws.analytics.EMR",
            "aws.storage.S3",
            "aws.database.Redshift"
        ],
        "relationships": [
            "Kinesis → Lambda → S3",
            "S3 → EMR → Redshift",
            "Real-time and batch processing"
        ]
    }
}

# YAML structure guidelines
YAML_STRUCTURE_GUIDE = {
    "basic_structure": """diagram:
  name: "Your Architecture Name"
  direction: left-to-right | right-to-left | top-to-bottom | bottom-to-top
  format: png | jpg | svg | pdf
  open: true | false
  resources:
    - id: unique-identifier
      name: Display Name
      type: aws.category.service
      relates:
        - to: target-resource-id
          direction: outgoing | incoming | bidirectional | undirected
          label: "Optional Label"
          color: "#hexcolor"
          style: dotted | dashed | solid""",
    
    "cluster_pattern": """- id: cluster-name
  name: Cluster Display Name
  type: cluster
  of:
    - id: resource-in-cluster
      name: Resource Name
      type: aws.service.type""",
    
    "group_pattern": """- id: group-name
  name: Group Display Name
  type: group
  of:
    - id: first-resource
      name: Resource 1
      type: aws.service.type
    - id: second-resource
      name: Resource 2
      type: aws.service.type""",
    
    "relationship_patterns": [
        "Simple: resource1 → resource2",
        "Bidirectional: resource1 ↔ resource2", 
        "Undirected: resource1 — resource2",
        "Nested: cluster.subcluster.resource",
        "Group: group-id references all resources in group"
    ],
    
    "valid_directions": ["outgoing", "incoming", "bidirectional", "undirected"],
    "valid_formats": ["png", "jpg", "svg", "pdf", "dot"],
    "valid_diagram_directions": ["left-to-right", "right-to-left", "top-to-bottom", "bottom-to-top"]
}

def get_examples_for_architecture_type(architecture_type: str) -> str:
    """Get relevant examples based on architecture type"""
    if "web" in architecture_type.lower():
        return DIAGRAMS_AS_CODE_EXAMPLES["simple_web_services"]["yaml"]
    elif "event" in architecture_type.lower() or "processing" in architecture_type.lower():
        return DIAGRAMS_AS_CODE_EXAMPLES["events_processing"]["yaml"]
    elif "worker" in architecture_type.lower():
        return DIAGRAMS_AS_CODE_EXAMPLES["simple_workers"]["yaml"]
    else:
        return DIAGRAMS_AS_CODE_EXAMPLES["complete_example"]["yaml"]

def get_service_type_for_component(component_name: str) -> str:
    """Map component names to AWS service types with flexible fallback"""
    component_lower = component_name.lower()
    
    # Direct mappings for common service names
    service_mappings = {
        "route53": "aws.network.Route53",
        "route 53": "aws.network.Route53",
        "dns": "aws.network.Route53",
        "cloudfront": "aws.network.CloudFront",
        "cdn": "aws.network.CloudFront",
        "alb": "aws.network.ElbApplicationLoadBalancer",
        "application load balancer": "aws.network.ElbApplicationLoadBalancer",
        "nlb": "aws.network.ElbNetworkLoadBalancer",
        "network load balancer": "aws.network.ElbNetworkLoadBalancer",
        "elb": "aws.network.ELB",
        "classic load balancer": "aws.network.ELB",
        "api gateway": "aws.network.APIGateway",
        "apigateway": "aws.network.APIGateway",
        "vpc": "aws.network.VPC",
        "privatelink": "aws.network.Privatelink",
        "private link": "aws.network.Privatelink",
        "transit gateway": "aws.network.TransitGateway",
        "internet gateway": "aws.network.InternetGateway",
        "nat gateway": "aws.network.NATGateway",
        "ec2": "aws.compute.EC2",
        "ecs": "aws.compute.ECS",
        "eks": "aws.compute.EKS",
        "lambda": "aws.compute.Lambda",
        "fargate": "aws.compute.Fargate",
        "elastic beanstalk": "aws.compute.ElasticBeanstalk",
        "beanstalk": "aws.compute.ElasticBeanstalk",
        "rds": "aws.database.RDS",
        "dynamodb": "aws.database.Dynamodb",
        "dynamo db": "aws.database.Dynamodb",
        "dynamo": "aws.database.Dynamodb",
        "elasticache": "aws.database.ElastiCache",
        "redis": "aws.database.ElastiCache",
        "memcached": "aws.database.ElastiCache",
        "dax": "aws.database.DAX",
        "redshift": "aws.database.Redshift",
        "s3": "aws.storage.S3",
        "simple storage service": "aws.storage.S3",
        "ebs": "aws.storage.EBS",
        "efs": "aws.storage.EFS",
        "sqs": "aws.integration.SQS",
        "simple queue service": "aws.integration.SQS",
        "sns": "aws.integration.SNS",
        "simple notification service": "aws.integration.SNS",
        "eventbridge": "aws.integration.Eventbridge",
        "event bridge": "aws.integration.Eventbridge",
        "step functions": "aws.integration.StepFunctions",
        "kinesis": "aws.analytics.Kinesis",
        "emr": "aws.analytics.EMR",
        "glue": "aws.analytics.Glue",
        "athena": "aws.analytics.Athena",
        "quicksight": "aws.analytics.Quicksight",
        "cognito": "aws.security.Cognito",
        "waf": "aws.security.WAF",
        "shield": "aws.security.Shield",
        "kms": "aws.security.KMS",
        "key management service": "aws.security.KMS",
        "secrets manager": "aws.security.SecretsManager",
        "certificate manager": "aws.security.CertificateManager",
        "acm": "aws.security.CertificateManager",
        "iam": "aws.security.IAM",
        "cloudwatch": "aws.management.Cloudwatch",
        "cloud watch": "aws.management.Cloudwatch",
        "cloudtrail": "aws.management.Cloudtrail",
        "cloud trail": "aws.management.Cloudtrail",
        "x-ray": "aws.devtools.XRay",
        "xray": "aws.devtools.XRay",
        "x ray": "aws.devtools.XRay",
        "codecommit": "aws.devtools.Codecommit",
        "code commit": "aws.devtools.Codecommit",
        "codebuild": "aws.devtools.Codebuild",
        "code build": "aws.devtools.Codebuild",
        "codepipeline": "aws.devtools.Codepipeline",
        "code pipeline": "aws.devtools.Codepipeline",
        "codedeploy": "aws.devtools.Codedeploy",
        "code deploy": "aws.devtools.Codedeploy",
        "ecr": "aws.compute.ECR",
        "elastic container registry": "aws.compute.ECR",
        "internet": "generic.network.Internet",
        "client": "aws.general.Client",
        "user": "aws.general.User",
        "users": "aws.general.Users"
    }
    
    # First, try direct mappings
    if component_lower in service_mappings:
        return service_mappings[component_lower]
    
    # FLEXIBILITY: Try partial matching for variations
    for service_key, service_type in service_mappings.items():
        if service_key in component_lower or component_lower in service_key:
            return service_type
    
    # FLEXIBILITY: Infer from keywords if not found in mappings
    return infer_service_type_from_name(component_name)


def infer_service_type_from_name(service_name: str) -> str:
    """Infer AWS service type from service name using flexible keyword matching"""
    service_lower = service_name.lower()
    
    # Database keywords
    if any(word in service_lower for word in ['db', 'database', 'dynamo', 'rds', 'sql', 'nosql', 'cache', 'redis', 'mongo', 'postgresql', 'mysql', 'oracle', 'cassandra', 'elasticsearch']):
        if any(word in service_lower for word in ['cache', 'redis', 'memcached']):
            return "aws.database.ElastiCache"
        elif any(word in service_lower for word in ['dynamo', 'nosql', 'document']):
            return "aws.database.Dynamodb"
        elif any(word in service_lower for word in ['redshift', 'warehouse', 'analytics']):
            return "aws.database.Redshift"
        elif any(word in service_lower for word in ['aurora']):
            return "aws.database.Aurora"
        elif any(word in service_lower for word in ['mongo', 'document']):
            return "aws.database.DocumentDB"
        elif any(word in service_lower for word in ['graph', 'neptune']):
            return "aws.database.Neptune"
        else:
            return "aws.database.RDS"
    
    # Storage keywords
    elif any(word in service_lower for word in ['storage', 'bucket', 'file', 'object', 'blob', 's3', 'ebs', 'efs', 'fsx', 'glacier', 'backup']):
        if any(word in service_lower for word in ['block', 'ebs', 'volume']):
            return "aws.storage.EBS"
        elif any(word in service_lower for word in ['file', 'efs', 'nfs']):
            return "aws.storage.EFS"
        elif any(word in service_lower for word in ['fsx', 'lustre', 'windows']):
            return "aws.storage.FSx"
        elif any(word in service_lower for word in ['backup', 'archive']):
            return "aws.storage.Backup"
        else:
            return "aws.storage.S3"
    
    # Compute keywords
    elif any(word in service_lower for word in ['compute', 'server', 'instance', 'container', 'lambda', 'function', 'ec2', 'ecs', 'eks', 'fargate', 'batch', 'beanstalk']):
        if any(word in service_lower for word in ['container', 'ecs', 'docker']):
            return "aws.compute.ECS"
        elif any(word in service_lower for word in ['kubernetes', 'eks', 'k8s']):
            return "aws.compute.EKS"
        elif any(word in service_lower for word in ['lambda', 'function', 'serverless']):
            return "aws.compute.Lambda"
        elif any(word in service_lower for word in ['fargate']):
            return "aws.compute.Fargate"
        elif any(word in service_lower for word in ['batch', 'job']):
            return "aws.compute.Batch"
        elif any(word in service_lower for word in ['beanstalk', 'platform']):
            return "aws.compute.ElasticBeanstalk"
        else:
            return "aws.compute.EC2"
    
    # Network keywords
    elif any(word in service_lower for word in ['network', 'load', 'balancer', 'cdn', 'gateway', 'dns', 'route', 'vpc', 'cloudfront', 'alb', 'nlb', 'elb']):
        if any(word in service_lower for word in ['cdn', 'cloudfront', 'distribution']):
            return "aws.network.CloudFront"
        elif any(word in service_lower for word in ['dns', 'route53', 'domain']):
            return "aws.network.Route53"
        elif any(word in service_lower for word in ['application', 'alb', 'layer 7']):
            return "aws.network.ElbApplicationLoadBalancer"
        elif any(word in service_lower for word in ['network', 'nlb', 'layer 4']):
            return "aws.network.ElbNetworkLoadBalancer"
        elif any(word in service_lower for word in ['classic', 'elb']):
            return "aws.network.ELB"
        elif any(word in service_lower for word in ['api', 'gateway', 'rest']):
            return "aws.network.APIGateway"
        elif any(word in service_lower for word in ['vpc', 'virtual', 'private', 'cloud']):
            return "aws.network.VPC"
        elif any(word in service_lower for word in ['nat', 'gateway']):
            return "aws.network.NATGateway"
        elif any(word in service_lower for word in ['internet', 'gateway']):
            return "aws.network.InternetGateway"
        elif any(word in service_lower for word in ['private', 'link']):
            return "aws.network.Privatelink"
        elif any(word in service_lower for word in ['transit', 'gateway']):
            return "aws.network.TransitGateway"
        else:
            return "aws.network.VPC"
    
    # Security keywords
    elif any(word in service_lower for word in ['security', 'auth', 'identity', 'firewall', 'waf', 'shield', 'cognito', 'iam', 'kms', 'secrets']):
        if any(word in service_lower for word in ['firewall', 'waf', 'web']):
            return "aws.security.WAF"
        elif any(word in service_lower for word in ['ddos', 'shield', 'protection']):
            return "aws.security.Shield"
        elif any(word in service_lower for word in ['auth', 'cognito', 'identity', 'login']):
            return "aws.security.Cognito"
        elif any(word in service_lower for word in ['key', 'kms', 'encryption']):
            return "aws.security.KMS"
        elif any(word in service_lower for word in ['secret', 'password', 'credential']):
            return "aws.security.SecretsManager"
        elif any(word in service_lower for word in ['certificate', 'ssl', 'tls', 'acm']):
            return "aws.security.CertificateManager"
        else:
            return "aws.security.IAM"
    
    # Integration keywords
    elif any(word in service_lower for word in ['queue', 'message', 'notification', 'event', 'stream', 'sqs', 'sns', 'eventbridge', 'kinesis', 'mq']):
        if any(word in service_lower for word in ['queue', 'sqs', 'fifo']):
            return "aws.integration.SQS"
        elif any(word in service_lower for word in ['notification', 'sns', 'topic', 'publish']):
            return "aws.integration.SNS"
        elif any(word in service_lower for word in ['event', 'bridge', 'bus']):
            return "aws.integration.Eventbridge"
        elif any(word in service_lower for word in ['step', 'function', 'workflow', 'state']):
            return "aws.integration.StepFunctions"
        elif any(word in service_lower for word in ['stream', 'kinesis', 'data']):
            return "aws.analytics.Kinesis"
        elif any(word in service_lower for word in ['mq', 'broker', 'rabbit', 'active']):
            return "aws.integration.MQ"
        else:
            return "aws.integration.SQS"
    
    # Analytics keywords
    elif any(word in service_lower for word in ['analytics', 'data', 'lake', 'warehouse', 'etl', 'glue', 'athena', 'emr', 'quicksight', 'redshift']):
        if any(word in service_lower for word in ['glue', 'etl', 'transform']):
            return "aws.analytics.Glue"
        elif any(word in service_lower for word in ['athena', 'query', 'sql']):
            return "aws.analytics.Athena"
        elif any(word in service_lower for word in ['emr', 'hadoop', 'spark']):
            return "aws.analytics.EMR"
        elif any(word in service_lower for word in ['quicksight', 'dashboard', 'bi']):
            return "aws.analytics.Quicksight"
        elif any(word in service_lower for word in ['redshift', 'warehouse']):
            return "aws.analytics.Redshift"
        else:
            return "aws.analytics.Kinesis"
    
    # Monitoring keywords
    elif any(word in service_lower for word in ['monitor', 'log', 'metric', 'watch', 'trace', 'alert', 'cloudwatch', 'xray', 'cloudtrail']):
        if any(word in service_lower for word in ['trace', 'xray', 'distributed']):
            return "aws.devtools.XRay"
        elif any(word in service_lower for word in ['trail', 'audit', 'api']):
            return "aws.management.Cloudtrail"
        else:
            return "aws.management.Cloudwatch"
    
    # DevOps keywords
    elif any(word in service_lower for word in ['code', 'build', 'deploy', 'pipeline', 'git', 'ci', 'cd', 'codecommit', 'codebuild', 'codepipeline', 'codedeploy']):
        if any(word in service_lower for word in ['commit', 'git', 'repository']):
            return "aws.devtools.Codecommit"
        elif any(word in service_lower for word in ['build', 'compile']):
            return "aws.devtools.Codebuild"
        elif any(word in service_lower for word in ['pipeline', 'ci', 'cd']):
            return "aws.devtools.Codepipeline"
        elif any(word in service_lower for word in ['deploy', 'deployment']):
            return "aws.devtools.Codedeploy"
        else:
            return "aws.devtools.Codecommit"
    
    # Mobile/Frontend keywords
    elif any(word in service_lower for word in ['mobile', 'app', 'amplify', 'frontend', 'react', 'vue', 'angular']):
        return "aws.mobile.Amplify"
    
    # Generic/User keywords
    elif any(word in service_lower for word in ['user', 'client', 'browser', 'mobile', 'internet', 'external']):
        if any(word in service_lower for word in ['internet', 'external', 'public']):
            return "generic.network.Internet"
        elif any(word in service_lower for word in ['mobile', 'app']):
            return "aws.general.MobileClient"
        elif any(word in service_lower for word in ['user', 'customer']):
            return "aws.general.Users"
        else:
            return "aws.general.Client"
    
    # If nothing matches, return a general type
    else:
        return "aws.general.General" 