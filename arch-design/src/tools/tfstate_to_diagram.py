from strands import tool
import json
import yaml
import re
import os
import logging
import boto3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Terraform resource type → diagrams-as-code type mapping
# ---------------------------------------------------------------------------
TERRAFORM_TO_DIAGRAM_TYPE: Dict[str, Dict[str, str]] = {
    # Compute
    "aws_instance": {"type": "aws.compute.EC2", "category": "compute", "label": "EC2 Instance"},
    "aws_launch_template": {"type": "aws.compute.EC2", "category": "compute", "label": "Launch Template"},
    "aws_autoscaling_group": {"type": "aws.compute.EC2", "category": "compute", "label": "Auto Scaling Group"},
    "aws_ecs_cluster": {"type": "aws.compute.ECS", "category": "compute", "label": "ECS Cluster"},
    "aws_ecs_service": {"type": "aws.compute.ECS", "category": "compute", "label": "ECS Service"},
    "aws_ecs_task_definition": {"type": "aws.compute.ECS", "category": "compute", "label": "ECS Task Definition"},
    "aws_lambda_function": {"type": "aws.compute.Lambda", "category": "compute", "label": "Lambda Function"},
    "aws_lambda_layer_version": {"type": "aws.compute.Lambda", "category": "compute", "label": "Lambda Layer"},
    "aws_eks_cluster": {"type": "aws.compute.EKS", "category": "compute", "label": "EKS Cluster"},
    "aws_eks_node_group": {"type": "aws.compute.EKS", "category": "compute", "label": "EKS Node Group"},
    "aws_elastic_beanstalk_environment": {"type": "aws.compute.ElasticBeanstalk", "category": "compute", "label": "Beanstalk"},
    "aws_ecr_repository": {"type": "aws.compute.ECR", "category": "compute", "label": "ECR Repository"},
    "aws_apprunner_service": {"type": "aws.compute.AppRunner", "category": "compute", "label": "App Runner"},
    "aws_batch_job_definition": {"type": "aws.compute.Batch", "category": "compute", "label": "Batch Job"},
    "aws_lightsail_instance": {"type": "aws.compute.Lightsail", "category": "compute", "label": "Lightsail"},

    # Network
    "aws_lb": {"type": "aws.network.ElbApplicationLoadBalancer", "category": "network", "label": "Load Balancer"},
    "aws_alb": {"type": "aws.network.ElbApplicationLoadBalancer", "category": "network", "label": "ALB"},
    # aws_lb_target_group intentionally excluded — ALB already represents the load balancer
    "aws_api_gateway_rest_api": {"type": "aws.network.APIGateway", "category": "network", "label": "API Gateway"},
    "aws_apigatewayv2_api": {"type": "aws.network.APIGateway", "category": "network", "label": "API Gateway v2"},
    "aws_cloudfront_distribution": {"type": "aws.network.CloudFront", "category": "network", "label": "CloudFront"},
    "aws_route53_zone": {"type": "aws.network.Route53", "category": "network", "label": "Route 53 Zone"},
    "aws_route53_record": {"type": "aws.network.Route53", "category": "network", "label": "Route 53 Record"},
    "aws_vpc": {"type": "aws.network.VPC", "category": "network", "label": "VPC"},
    "aws_nat_gateway": {"type": "aws.network.NATGateway", "category": "network", "label": "NAT Gateway"},
    "aws_internet_gateway": {"type": "aws.network.InternetGateway", "category": "network", "label": "Internet Gateway"},
    "aws_vpc_endpoint": {"type": "aws.network.Endpoint", "category": "network", "label": "VPC Endpoint"},
    "aws_ec2_transit_gateway": {"type": "aws.network.TransitGateway", "category": "network", "label": "Transit Gateway"},
    "aws_dx_connection": {"type": "aws.network.DirectConnect", "category": "network", "label": "Direct Connect"},
    "aws_vpn_gateway": {"type": "aws.network.VPNGateway", "category": "network", "label": "VPN Gateway"},
    "aws_global_accelerator_accelerator": {"type": "aws.network.GlobalAccelerator", "category": "network", "label": "Global Accelerator"},
    "aws_cloud_map_service": {"type": "aws.network.CloudMap", "category": "network", "label": "Cloud Map"},

    # Database
    "aws_db_instance": {"type": "aws.database.RDS", "category": "database", "label": "RDS Instance"},
    "aws_rds_cluster": {"type": "aws.database.Aurora", "category": "database", "label": "Aurora Cluster"},
    "aws_rds_cluster_instance": {"type": "aws.database.Aurora", "category": "database", "label": "Aurora Instance"},
    "aws_dynamodb_table": {"type": "aws.database.Dynamodb", "category": "database", "label": "DynamoDB Table"},
    "aws_elasticache_cluster": {"type": "aws.database.ElastiCache", "category": "database", "label": "ElastiCache"},
    "aws_elasticache_replication_group": {"type": "aws.database.ElastiCache", "category": "database", "label": "ElastiCache Replication"},
    "aws_redshift_cluster": {"type": "aws.database.Redshift", "category": "database", "label": "Redshift Cluster"},
    "aws_neptune_cluster": {"type": "aws.database.Neptune", "category": "database", "label": "Neptune Cluster"},
    "aws_docdb_cluster": {"type": "aws.database.DocumentDB", "category": "database", "label": "DocumentDB"},
    "aws_dax_cluster": {"type": "aws.database.DynamodbDax", "category": "database", "label": "DAX Cluster"},
    "aws_timestream_database": {"type": "aws.database.Timestream", "category": "database", "label": "Timestream"},
    "aws_keyspaces_table": {"type": "aws.database.KeyspacesManagedApacheCassandraService", "category": "database", "label": "Keyspaces"},

    # Storage
    "aws_s3_bucket": {"type": "aws.storage.S3", "category": "storage", "label": "S3 Bucket"},
    "aws_efs_file_system": {"type": "aws.storage.EFS", "category": "storage", "label": "EFS"},
    "aws_ebs_volume": {"type": "aws.storage.EBS", "category": "storage", "label": "EBS Volume"},
    "aws_fsx_lustre_file_system": {"type": "aws.storage.Fsx", "category": "storage", "label": "FSx Lustre"},
    "aws_fsx_windows_file_system": {"type": "aws.storage.Fsx", "category": "storage", "label": "FSx Windows"},
    "aws_backup_vault": {"type": "aws.storage.Backup", "category": "storage", "label": "Backup Vault"},
    "aws_glacier_vault": {"type": "aws.storage.S3Glacier", "category": "storage", "label": "Glacier Vault"},

    # Security
    "aws_cognito_user_pool": {"type": "aws.security.Cognito", "category": "security", "label": "Cognito User Pool"},
    "aws_cognito_identity_pool": {"type": "aws.security.Cognito", "category": "security", "label": "Cognito Identity Pool"},
    "aws_wafv2_web_acl": {"type": "aws.security.WAF", "category": "security", "label": "WAF ACL"},
    "aws_waf_web_acl": {"type": "aws.security.WAF", "category": "security", "label": "WAF ACL"},
    "aws_shield_protection": {"type": "aws.security.Shield", "category": "security", "label": "Shield Protection"},
    "aws_acm_certificate": {"type": "aws.security.CertificateManager", "category": "security", "label": "ACM Certificate"},
    "aws_kms_key": {"type": "aws.security.KMS", "category": "security", "label": "KMS Key"},
    "aws_secretsmanager_secret": {"type": "aws.security.SecretsManager", "category": "security", "label": "Secrets Manager"},
    "aws_iam_role": {"type": "aws.security.IAM", "category": "security", "label": "IAM Role"},
    "aws_guardduty_detector": {"type": "aws.security.Guardduty", "category": "security", "label": "GuardDuty"},
    "aws_inspector_assessment_target": {"type": "aws.security.Inspector", "category": "security", "label": "Inspector"},
    "aws_macie2_account": {"type": "aws.security.Macie", "category": "security", "label": "Macie"},

    # Integration / Messaging
    "aws_sqs_queue": {"type": "aws.integration.SQS", "category": "integration", "label": "SQS Queue"},
    "aws_sns_topic": {"type": "aws.integration.SNS", "category": "integration", "label": "SNS Topic"},
    "aws_cloudwatch_event_rule": {"type": "aws.integration.Eventbridge", "category": "integration", "label": "EventBridge Rule"},
    "aws_cloudwatch_event_bus": {"type": "aws.integration.Eventbridge", "category": "integration", "label": "EventBridge Bus"},
    "aws_sfn_state_machine": {"type": "aws.integration.StepFunctions", "category": "integration", "label": "Step Functions"},
    "aws_mq_broker": {"type": "aws.integration.MQ", "category": "integration", "label": "Amazon MQ"},
    "aws_appsync_graphql_api": {"type": "aws.integration.Appsync", "category": "integration", "label": "AppSync"},

    # Analytics
    "aws_kinesis_stream": {"type": "aws.analytics.KinesisDataStreams", "category": "analytics", "label": "Kinesis Stream"},
    "aws_kinesis_firehose_delivery_stream": {"type": "aws.analytics.KinesisDataFirehose", "category": "analytics", "label": "Kinesis Firehose"},
    "aws_glue_job": {"type": "aws.analytics.Glue", "category": "analytics", "label": "Glue Job"},
    "aws_glue_catalog_database": {"type": "aws.analytics.Glue", "category": "analytics", "label": "Glue Catalog"},
    "aws_athena_workgroup": {"type": "aws.analytics.Athena", "category": "analytics", "label": "Athena"},
    "aws_elasticsearch_domain": {"type": "aws.analytics.ElasticsearchService", "category": "analytics", "label": "Elasticsearch"},
    "aws_opensearch_domain": {"type": "aws.analytics.ElasticsearchService", "category": "analytics", "label": "OpenSearch"},
    "aws_emr_cluster": {"type": "aws.analytics.EMR", "category": "analytics", "label": "EMR Cluster"},
    "aws_quicksight_data_source": {"type": "aws.analytics.Quicksight", "category": "analytics", "label": "QuickSight"},
    "aws_msk_cluster": {"type": "aws.analytics.ManagedStreamingForKafka", "category": "analytics", "label": "MSK Cluster"},

    # Management / Monitoring
    "aws_cloudwatch_log_group": {"type": "aws.management.Cloudwatch", "category": "monitoring", "label": "CloudWatch Logs"},
    "aws_cloudwatch_metric_alarm": {"type": "aws.management.Cloudwatch", "category": "monitoring", "label": "CloudWatch Alarm"},
    "aws_cloudwatch_dashboard": {"type": "aws.management.Cloudwatch", "category": "monitoring", "label": "CloudWatch Dashboard"},
    "aws_cloudtrail": {"type": "aws.management.Cloudtrail", "category": "monitoring", "label": "CloudTrail"},
    "aws_cloudformation_stack": {"type": "aws.management.Cloudformation", "category": "monitoring", "label": "CloudFormation Stack"},
    "aws_ssm_parameter": {"type": "aws.management.SystemsManager", "category": "monitoring", "label": "SSM Parameter"},
    "aws_config_configuration_recorder": {"type": "aws.management.Config", "category": "monitoring", "label": "AWS Config"},

    # DevTools / CI-CD
    "aws_codebuild_project": {"type": "aws.devtools.Codebuild", "category": "devops", "label": "CodeBuild"},
    "aws_codepipeline": {"type": "aws.devtools.Codepipeline", "category": "devops", "label": "CodePipeline"},
    "aws_codecommit_repository": {"type": "aws.devtools.Codecommit", "category": "devops", "label": "CodeCommit"},
    "aws_codedeploy_app": {"type": "aws.devtools.Codedeploy", "category": "devops", "label": "CodeDeploy"},
}

# Terraform resource types to skip (infrastructure plumbing, not diagram-worthy)
SKIP_RESOURCE_TYPES = {
    "aws_subnet", "aws_route_table", "aws_route_table_association",
    "aws_security_group", "aws_security_group_rule", "aws_vpc_security_group_ingress_rule",
    "aws_vpc_security_group_egress_rule",
    "aws_iam_role", "aws_iam_policy", "aws_iam_policy_document", "aws_iam_role_policy",
    "aws_iam_role_policy_attachment", "aws_iam_instance_profile",
    "aws_iam_policy_attachment", "aws_iam_group", "aws_iam_group_policy",
    "aws_iam_user", "aws_iam_user_policy",
    "aws_ecs_task_definition", "aws_lb_target_group",
    "aws_lb_listener", "aws_lb_listener_rule", "aws_alb_listener",
    "aws_route53_resolver_endpoint", "aws_route53_resolver_rule",
    "aws_eip", "aws_network_interface",
    "aws_cloudwatch_log_stream",
    "aws_lambda_permission", "aws_lambda_event_source_mapping",
    "aws_s3_bucket_policy", "aws_s3_bucket_versioning",
    "aws_s3_bucket_server_side_encryption_configuration",
    "aws_s3_bucket_public_access_block", "aws_s3_bucket_lifecycle_configuration",
    "aws_s3_bucket_notification", "aws_s3_object",
    "aws_kms_alias", "aws_secretsmanager_secret_version",
    "aws_acm_certificate_validation",
    "aws_db_subnet_group", "aws_elasticache_subnet_group",
    "aws_api_gateway_deployment", "aws_api_gateway_stage",
    "aws_api_gateway_resource", "aws_api_gateway_method",
    "aws_api_gateway_integration",
}


# ---------------------------------------------------------------------------
# State file reading
# ---------------------------------------------------------------------------

def _read_local_tfstate(path: str) -> dict:
    """Read a terraform.tfstate file from a local path."""
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix == ".tfstate" and "tfstate" not in file_path.name:
        raise ValueError(f"File does not appear to be a tfstate file: {file_path}")
    with open(file_path, "r") as f:
        return json.load(f)


def _read_s3_tfstate(s3_uri: str) -> dict:
    """Read a terraform.tfstate file from an S3 bucket."""
    match = re.match(r"s3://([^/]+)/(.+)", s3_uri)
    if not match:
        raise ValueError(f"Invalid S3 URI: {s3_uri}. Expected format: s3://bucket/key")
    bucket, key = match.group(1), match.group(2)

    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    return json.loads(content)


def _read_tfstate(source: str) -> dict:
    """Read tfstate from either local file or S3."""
    if source.startswith("s3://"):
        return _read_s3_tfstate(source)
    return _read_local_tfstate(source)


# ---------------------------------------------------------------------------
# State parsing
# ---------------------------------------------------------------------------

def _parse_resources(state: dict) -> List[Dict[str, Any]]:
    """Extract managed resources from the tfstate JSON."""
    version = state.get("version", 0)
    if version < 3:
        raise ValueError(f"Unsupported tfstate version {version}. Requires version 3 or 4.")

    raw_resources = state.get("resources", [])
    parsed = []

    for res in raw_resources:
        if res.get("mode") != "managed":
            continue

        tf_type = res.get("type", "")
        if tf_type in SKIP_RESOURCE_TYPES:
            continue

        mapping = TERRAFORM_TO_DIAGRAM_TYPE.get(tf_type)
        if not mapping:
            continue

        module = res.get("module", "")
        name = res.get("name", tf_type)

        attrs = {}
        instances = res.get("instances", [])
        if instances:
            attrs = instances[0].get("attributes", {})

        resource_name = attrs.get("tags", {}).get("Name", name) if isinstance(attrs.get("tags"), dict) else name

        # Determine specific subtype for load balancers
        diagram_type = mapping["type"]
        if tf_type == "aws_lb":
            lb_type = attrs.get("load_balancer_type", "application")
            if lb_type == "network":
                diagram_type = "aws.network.ElbNetworkLoadBalancer"

        parsed.append({
            "tf_type": tf_type,
            "tf_name": name,
            "resource_name": resource_name,
            "diagram_type": diagram_type,
            "category": mapping["category"],
            "label": mapping["label"],
            "module": module,
            "attrs": attrs,
        })

    return parsed


# ---------------------------------------------------------------------------
# Relationship inference
# ---------------------------------------------------------------------------

def _infer_relationships(resources: List[Dict[str, Any]]) -> List[Tuple[str, str, str]]:
    """Infer relationships between resources from their attributes.

    Uses ARN-based lookups for precise connections and falls back to
    architectural patterns only for 1:1 or 1:few connections — never
    connects every compute to every database.

    Returns list of (source_id, target_id, label) tuples.
    """
    relationships: List[Tuple[str, str, str]] = []
    id_by_arn: Dict[str, str] = {}
    res_by_type: Dict[str, List[Dict]] = {}

    for res in resources:
        rid = _resource_id(res)
        arn = res["attrs"].get("arn", "")
        if arn:
            id_by_arn[arn] = rid
        res_by_type.setdefault(res["tf_type"], []).append(res)

    seen = set()

    def _first_id(tf_type: str) -> Optional[str]:
        items = res_by_type.get(tf_type, [])
        return _resource_id(items[0]) if items else None

    for res in resources:
        rid = _resource_id(res)
        attrs = res["attrs"]
        tf_type = res["tf_type"]

        # --- Precise ARN-based connections ---

        # ECS service → target group (via load_balancer config)
        if tf_type == "aws_ecs_service":
            for lb_conf in attrs.get("load_balancer", []):
                tg_arn = lb_conf.get("target_group_arn", "")
                if tg_arn and tg_arn in id_by_arn:
                    _add_rel(relationships, seen, id_by_arn[tg_arn], rid, "Routes To")

        # ECS service → its cluster
        if tf_type == "aws_ecs_service":
            cluster_arn = attrs.get("cluster", "")
            if cluster_arn and cluster_arn in id_by_arn:
                _add_rel(relationships, seen, id_by_arn[cluster_arn], rid, "Runs")

        # --- Architectural flow (selective, not N×M) ---

        # Route53 → CloudFront (1:1)
        if tf_type == "aws_route53_zone":
            tgt = _first_id("aws_cloudfront_distribution")
            if tgt:
                _add_rel(relationships, seen, rid, tgt, "DNS")
            else:
                tgt = _first_id("aws_lb")
                if tgt:
                    _add_rel(relationships, seen, rid, tgt, "DNS")

        # CloudFront → ALB + S3
        if tf_type == "aws_cloudfront_distribution":
            tgt = _first_id("aws_lb")
            if tgt:
                _add_rel(relationships, seen, rid, tgt, "Origin")
            for s3 in res_by_type.get("aws_s3_bucket", []):
                _add_rel(relationships, seen, rid, _resource_id(s3), "Static Assets")

        # WAF → ALB or CloudFront (1:1)
        if tf_type in ("aws_wafv2_web_acl", "aws_waf_web_acl"):
            tgt = _first_id("aws_lb") or _first_id("aws_cloudfront_distribution")
            if tgt:
                _add_rel(relationships, seen, rid, tgt, "Protects")

        # ALB → ECS services only (not all compute)
        if tf_type in ("aws_lb", "aws_alb"):
            for svc in res_by_type.get("aws_ecs_service", []):
                _add_rel(relationships, seen, rid, _resource_id(svc), "Routes To")
            # If no ECS, try EC2 or EKS
            if not res_by_type.get("aws_ecs_service"):
                for inst in res_by_type.get("aws_instance", []):
                    _add_rel(relationships, seen, rid, _resource_id(inst), "Routes To")
                for eks in res_by_type.get("aws_eks_cluster", []):
                    _add_rel(relationships, seen, rid, _resource_id(eks), "Routes To")

        # API Gateway → Lambda
        if tf_type in ("aws_api_gateway_rest_api", "aws_apigatewayv2_api"):
            for lam in res_by_type.get("aws_lambda_function", []):
                _add_rel(relationships, seen, rid, _resource_id(lam), "Invokes")

        # ECS services → RDS / DynamoDB / ElastiCache (services only, not clusters/tasks/ECR)
        if tf_type == "aws_ecs_service":
            for db in res_by_type.get("aws_db_instance", []):
                _add_rel(relationships, seen, rid, _resource_id(db), "Reads/Writes")
            for db in res_by_type.get("aws_rds_cluster", []):
                _add_rel(relationships, seen, rid, _resource_id(db), "Reads/Writes")
            for ddb in res_by_type.get("aws_dynamodb_table", []):
                _add_rel(relationships, seen, rid, _resource_id(ddb), "Reads/Writes")
            for cache in res_by_type.get("aws_elasticache_cluster", []) + res_by_type.get("aws_elasticache_replication_group", []):
                _add_rel(relationships, seen, rid, _resource_id(cache), "Cache")

        # Lambda → SQS (consumer), SNS (publisher)
        if tf_type == "aws_lambda_function":
            for q in res_by_type.get("aws_sqs_queue", []):
                _add_rel(relationships, seen, _resource_id(q), rid, "Triggers")
            for s3 in res_by_type.get("aws_s3_bucket", []):
                _add_rel(relationships, seen, rid, _resource_id(s3), "Reads/Writes")

        # SNS → SQS fanout, SNS → Lambda
        if tf_type == "aws_sns_topic":
            for q in res_by_type.get("aws_sqs_queue", []):
                _add_rel(relationships, seen, rid, _resource_id(q), "Fanout")
            for lam in res_by_type.get("aws_lambda_function", []):
                _add_rel(relationships, seen, rid, _resource_id(lam), "Notifies")

        # Kinesis → Lambda / Firehose
        if tf_type == "aws_kinesis_stream":
            for lam in res_by_type.get("aws_lambda_function", []):
                _add_rel(relationships, seen, rid, _resource_id(lam), "Streams To")
            for fh in res_by_type.get("aws_kinesis_firehose_delivery_stream", []):
                _add_rel(relationships, seen, rid, _resource_id(fh), "Delivers To")

        # Step Functions → Lambda
        if tf_type == "aws_sfn_state_machine":
            for lam in res_by_type.get("aws_lambda_function", []):
                _add_rel(relationships, seen, rid, _resource_id(lam), "Orchestrates")

        # CodePipeline → CodeBuild
        if tf_type == "aws_codepipeline":
            for cb in res_by_type.get("aws_codebuild_project", []):
                _add_rel(relationships, seen, rid, _resource_id(cb), "Builds")
            tgt = _first_id("aws_ecs_service") or _first_id("aws_lambda_function")
            if tgt:
                _add_rel(relationships, seen, rid, tgt, "Deploys")

        # CodeBuild → ECR
        if tf_type == "aws_codebuild_project":
            for ecr in res_by_type.get("aws_ecr_repository", []):
                _add_rel(relationships, seen, rid, _resource_id(ecr), "Pushes Image")

        # Cognito → ALB / API Gateway (auth provider)
        if tf_type == "aws_cognito_user_pool":
            tgt = _first_id("aws_lb") or _first_id("aws_api_gateway_rest_api")
            if tgt:
                _add_rel(relationships, seen, rid, tgt, "Authenticates")

    return relationships


def _resource_id(res: Dict[str, Any]) -> str:
    """Generate a stable, unique diagram resource ID from tf_type + tf_name."""
    module = res["module"].replace("module.", "").replace(".", "_") if res["module"] else ""
    # Use short type prefix + name to guarantee uniqueness across different resource types
    tf_short = res["tf_type"].replace("aws_", "").replace("v2_", "")
    base = re.sub(r"[^a-zA-Z0-9]", "_", f"{tf_short}_{res['tf_name']}").lower()
    # Collapse repeated underscores
    base = re.sub(r"_+", "_", base).strip("_")
    return f"{module}_{base}" if module else base


def _add_rel(rels: list, seen: set, src: str, tgt: str, label: str):
    """Add a relationship if not already present."""
    if src == tgt:
        return
    key = (src, tgt)
    if key not in seen:
        seen.add(key)
        rels.append((src, tgt, label))


# ---------------------------------------------------------------------------
# LLM-enhanced relationship inference
# ---------------------------------------------------------------------------

def _load_bedrock_config() -> dict:
    """Load Bedrock model config from .agent.yaml so we reuse the same model."""
    defaults = {
        "model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "region_name": "us-west-2",
    }
    try:
        cfg_path = Path(__file__).parent.parent.parent / ".agent.yaml"
        if cfg_path.exists():
            cfg = yaml.safe_load(cfg_path.read_text())
            kwargs = cfg.get("provider", {}).get("kwargs", {})
            return {
                "model_id": kwargs.get("model_id", defaults["model_id"]),
                "region_name": kwargs.get("region_name", defaults["region_name"]),
            }
    except Exception:
        pass
    return defaults


def _call_bedrock(prompt: str, max_tokens: int = 4096) -> str:
    """Make a direct boto3 call to Bedrock for structured inference."""
    cfg = _load_bedrock_config()
    client = boto3.client("bedrock-runtime", region_name=cfg["region_name"])

    response = client.invoke_model(
        modelId=cfg["model_id"],
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }),
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


def _parse_json_from_llm(text: str):
    """Extract a JSON array from LLM output, handling markdown fences."""
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            if cleaned.startswith("["):
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    continue
    if text.startswith("["):
        return json.loads(text)
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        return json.loads(text[start : end + 1])
    raise ValueError("No JSON array found in LLM response")


def _llm_enhance_relationships(
    resources: List[Dict[str, Any]],
    deterministic_rels: List[Tuple[str, str, str]],
) -> List[Tuple[str, str, str]]:
    """Ask the LLM to review and enhance the deterministic relationships.

    The LLM receives the full resource list and the relationships already
    inferred, and can add missing ones, remove incorrect ones, or improve
    labels.  Returns the enhanced list, or the original if the call fails.
    """
    resource_desc = "\n".join(
        f"  - id: {_resource_id(r)},  terraform_type: {r['tf_type']},  "
        f"name: {r['resource_name']},  category: {r['category']}"
        for r in resources
    )
    existing_desc = "\n".join(
        f"  - {src} → {tgt}  label: \"{lbl}\"" for src, tgt, lbl in deterministic_rels
    )

    prompt = f"""You are a Senior AWS Solutions Architect reviewing an infrastructure architecture derived from a Terraform state file.

## Resources (from Terraform state)
{resource_desc}

## Existing Relationships (auto-inferred)
{existing_desc}

## Task
Review the resources and existing relationships. Return an **improved** set of relationships that:
1. Keeps correct existing relationships (you may improve labels).
2. Adds any missing relationships that are strongly implied by the resource types and names.
3. Removes any relationships that don't make architectural sense.
4. Does NOT create N×M connections — be selective and precise.
5. Uses descriptive labels (e.g. "HTTPS", "Read/Write", "Triggers", "Publishes", "Cache Lookup", "DNS").
6. Every from_id and to_id MUST be one of the resource ids listed above.

## Output
Return ONLY a JSON array — no markdown, no explanation. Each element:
{{"from_id": "<source id>", "to_id": "<target id>", "label": "<short label>"}}

JSON array:"""

    try:
        raw = _call_bedrock(prompt)
        parsed = _parse_json_from_llm(raw)

        valid_ids = {_resource_id(r) for r in resources}
        enhanced: List[Tuple[str, str, str]] = []
        seen: set = set()
        for rel in parsed:
            src = rel.get("from_id", "")
            tgt = rel.get("to_id", "")
            lbl = rel.get("label", "")
            if src in valid_ids and tgt in valid_ids and src != tgt:
                key = (src, tgt)
                if key not in seen:
                    seen.add(key)
                    enhanced.append((src, tgt, lbl))

        logger.info(
            f"LLM enhanced relationships: {len(deterministic_rels)} deterministic → "
            f"{len(enhanced)} LLM-derived"
        )
        return enhanced if enhanced else deterministic_rels
    except Exception as e:
        logger.warning(f"LLM enhancement failed, keeping deterministic relationships: {e}")
        return deterministic_rels


# ---------------------------------------------------------------------------
# YAML generation
# ---------------------------------------------------------------------------

def _build_diagram_yaml(
    resources: List[Dict[str, Any]],
    relationships: List[Tuple[str, str, str]],
    diagram_name: str,
) -> dict:
    """Build a diagrams-as-code YAML structure."""

    # Group resources by module for clustering
    modules: Dict[str, List[Dict]] = {}
    for res in resources:
        module_key = res["module"] or "root"
        modules.setdefault(module_key, []).append(res)

    # Build relationship lookup: source_id → list of {to, label}
    rel_map: Dict[str, List[dict]] = {}
    for src, tgt, label in relationships:
        rel_map.setdefault(src, []).append({"to": tgt, "direction": "outgoing", "label": label})

    # Build resources list
    yaml_resources = []
    for res in resources:
        rid = _resource_id(res)
        entry: Dict[str, Any] = {
            "id": rid,
            "name": res["resource_name"],
            "type": res["diagram_type"],
        }
        if rid in rel_map:
            entry["relates"] = rel_map[rid]
        yaml_resources.append(entry)

    # Build clusters from modules (skip if only root)
    yaml_clusters = []
    if len(modules) > 1 or "root" not in modules:
        for module_key, mod_resources in modules.items():
            if module_key == "root":
                continue
            cluster_name = module_key.replace("module.", "").replace("_", " ").title()
            yaml_clusters.append({
                "id": re.sub(r"[^a-zA-Z0-9]", "_", module_key).lower(),
                "name": cluster_name,
                "resources": [_resource_id(r) for r in mod_resources],
            })

    # Group by category for additional clustering
    categories: Dict[str, List[str]] = {}
    for res in resources:
        if res["module"]:
            continue
        categories.setdefault(res["category"], []).append(_resource_id(res))

    category_labels = {
        "compute": "Compute",
        "network": "Networking",
        "database": "Databases",
        "storage": "Storage",
        "security": "Security",
        "integration": "Integration & Messaging",
        "analytics": "Analytics",
        "monitoring": "Management & Monitoring",
        "devops": "CI/CD & DevTools",
    }

    for cat, rids in categories.items():
        if len(rids) >= 2:
            yaml_clusters.append({
                "id": cat,
                "name": category_labels.get(cat, cat.title()),
                "resources": rids,
            })

    diagram = {
        "diagram": {
            "name": diagram_name,
            "direction": "top-to-bottom",
            "format": "png",
            "open": True,
            "resources": yaml_resources,
        }
    }

    if yaml_clusters:
        diagram["diagram"]["clusters"] = yaml_clusters

    return diagram


# ---------------------------------------------------------------------------
# Strands tools
# ---------------------------------------------------------------------------

@tool
def read_tfstate(source: str) -> str:
    """
    Read and summarise a Terraform state file from a local path or S3 URI.

    Args:
        source: Path to the tfstate file. Either a local path
                (e.g. /path/to/terraform.tfstate) or an S3 URI
                (e.g. s3://my-bucket/env/terraform.tfstate).

    Returns:
        JSON summary of managed AWS resources found in the state file including
        resource types, names, and counts by category.
    """
    try:
        state = _read_tfstate(source)
    except FileNotFoundError as e:
        return f"❌ File not found: {e}"
    except Exception as e:
        return f"❌ Error reading tfstate: {e}"

    resources = _parse_resources(state)

    # Build summary
    category_counts: Dict[str, int] = {}
    resource_list = []
    for res in resources:
        category_counts[res["category"]] = category_counts.get(res["category"], 0) + 1
        resource_list.append({
            "terraform_type": res["tf_type"],
            "name": res["resource_name"],
            "diagram_type": res["diagram_type"],
            "category": res["category"],
            "module": res["module"] or "root",
        })

    summary = {
        "source": source,
        "tfstate_version": state.get("version"),
        "serial": state.get("serial"),
        "total_managed_resources": len(state.get("resources", [])),
        "diagrammable_resources": len(resources),
        "categories": category_counts,
        "resources": resource_list,
    }

    return json.dumps(summary, indent=2)


@tool
def tfstate_to_diagram(
    source: str,
    diagram_name: str = "Infrastructure Architecture",
    output_folder: str = "",
    include_types: str = "",
    exclude_types: str = "",
    enhance_with_llm: str = "false",
) -> str:
    """
    Read a Terraform state file and generate an architecture diagram (YAML + PNG).

    Reads the tfstate from a local path or S3 URI, extracts all managed AWS
    resources, maps them to diagram types, infers relationships, and produces
    a diagrams-as-code YAML file and a PNG architecture diagram.

    When enhance_with_llm is "true", the tool calls the LLM (via Bedrock) to
    review and enhance the auto-inferred relationships — adding missing
    connections, removing incorrect ones, and improving labels. This requires
    AWS Bedrock credentials. Defaults to "false" to keep standalone capability.

    Args:
        source: Path to the tfstate file. Either a local path
                (e.g. /path/to/terraform.tfstate) or an S3 URI
                (e.g. s3://my-bucket/env/terraform.tfstate).
        diagram_name: Name shown on the generated diagram.
        output_folder: Folder to save outputs. Auto-generated if empty.
        include_types: Comma-separated Terraform types to include (empty = all).
        exclude_types: Comma-separated additional Terraform types to exclude.
        enhance_with_llm: "true" to use LLM for relationship enhancement, "false" (default) for deterministic only.

    Returns:
        Status message with file paths and a summary of what was generated.
    """
    # Read state
    try:
        state = _read_tfstate(source)
    except FileNotFoundError as e:
        return f"❌ File not found: {e}"
    except Exception as e:
        return f"❌ Error reading tfstate: {e}"

    # Parse resources
    resources = _parse_resources(state)

    # Apply include/exclude filters
    if include_types:
        allowed = {t.strip() for t in include_types.split(",")}
        resources = [r for r in resources if r["tf_type"] in allowed]
    if exclude_types:
        blocked = {t.strip() for t in exclude_types.split(",")}
        resources = [r for r in resources if r["tf_type"] not in blocked]

    if not resources:
        return "❌ No diagrammable AWS resources found in the state file."

    # Infer relationships (deterministic pass)
    relationships = _infer_relationships(resources)
    relationship_method = "deterministic"

    # Optional LLM enhancement pass
    if enhance_with_llm.lower() == "true":
        relationships = _llm_enhance_relationships(resources, relationships)
        relationship_method = "LLM-enhanced"

    # Build YAML
    diagram_dict = _build_diagram_yaml(resources, relationships, diagram_name)
    yaml_content = yaml.dump(diagram_dict, default_flow_style=False, sort_keys=False)

    # Output folder
    if not output_folder:
        sanitized = re.sub(r"[^a-zA-Z0-9\s-]", "", diagram_name)
        sanitized = re.sub(r"\s+", "_", sanitized).lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = f"{sanitized}_{timestamp}"

    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save YAML
    yaml_filename = f"{diagram_name.replace(' ', '_').lower()}.yaml"
    yaml_path = output_dir / yaml_filename
    with open(yaml_path, "w") as f:
        f.write(yaml_content)

    # Generate PNG using the diagrams library
    png_path = output_dir / f"{diagram_name.replace(' ', '_').lower()}.png"
    diagram_result = _generate_png(diagram_dict, str(png_path))

    # Build category summary
    cat_counts: Dict[str, int] = {}
    for res in resources:
        cat_counts[res["category"]] = cat_counts.get(res["category"], 0) + 1
    cat_summary = ", ".join(f"{v} {k}" for k, v in sorted(cat_counts.items(), key=lambda x: -x[1]))

    return f"""✅ Terraform State → Architecture Diagram Generated!

📁 **Source**: {source}
📂 **Output Folder**: {output_folder}/
📄 **YAML File**: {yaml_path}
🖼️ **PNG Diagram**: {png_path}

📊 **Resources**: {len(resources)} AWS services mapped ({cat_summary})
🔗 **Relationships**: {len(relationships)} connections ({relationship_method})
🗂️ **Terraform State Version**: {state.get('version')}  |  Serial: {state.get('serial')}

{diagram_result}

📋 **YAML Preview** (first 600 chars):
{yaml_content[:600]}...
"""


def _generate_png(diagram_dict: dict, output_path: str) -> str:
    """Generate PNG from the diagram dict using the Python diagrams library."""
    try:
        from diagrams import Diagram, Cluster, Edge
        import diagrams.aws.network as aws_network
        import diagrams.aws.compute as aws_compute
        import diagrams.aws.database as aws_database
        import diagrams.aws.storage as aws_storage
        import diagrams.aws.security as aws_security
        import diagrams.aws.management as aws_management
        import diagrams.aws.devtools as aws_devtools
        import diagrams.aws.analytics as aws_analytics
        import diagrams.aws.integration as aws_integration
        import diagrams.aws.general as aws_general
        import diagrams.generic.network as generic_network
    except ImportError:
        return "⚠️ PNG generation skipped — install: pip install diagrams graphviz"

    diagram_info = diagram_dict.get("diagram", {})
    resources = diagram_info.get("resources", [])

    output_file = Path(output_path)
    output_stem = output_file.stem
    output_dir = output_file.parent

    NODE_MAP = {
        "aws.compute.EC2": aws_compute.EC2,
        "aws.compute.ECS": aws_compute.ECS,
        "aws.compute.EKS": aws_compute.EKS,
        "aws.compute.Lambda": aws_compute.Lambda,
        "aws.compute.Fargate": aws_compute.Fargate,
        "aws.compute.ElasticBeanstalk": aws_compute.ElasticBeanstalk,
        "aws.compute.ECR": aws_compute.ECR,
        "aws.compute.AppRunner": lambda n: aws_compute.EC2(n),
        "aws.compute.Batch": aws_compute.Batch,
        "aws.compute.Lightsail": aws_compute.Lightsail,
        "aws.network.ElbApplicationLoadBalancer": aws_network.ElbApplicationLoadBalancer,
        "aws.network.ElbNetworkLoadBalancer": aws_network.ElbNetworkLoadBalancer,
        "aws.network.ELB": aws_network.ELB,
        "aws.network.APIGateway": aws_network.APIGateway,
        "aws.network.CloudFront": aws_network.CloudFront,
        "aws.network.Route53": aws_network.Route53,
        "aws.network.VPC": aws_network.VPC,
        "aws.network.NATGateway": aws_network.NATGateway,
        "aws.network.InternetGateway": aws_network.InternetGateway,
        "aws.network.Endpoint": aws_network.Endpoint,
        "aws.network.TransitGateway": aws_network.TransitGateway,
        "aws.network.DirectConnect": aws_network.DirectConnect,
        "aws.network.VPNGateway": aws_network.VpnGateway,
        "aws.network.GlobalAccelerator": aws_network.GlobalAccelerator,
        "aws.network.CloudMap": aws_network.CloudMap,
        "aws.network.Privatelink": aws_network.Privatelink,
        "aws.database.RDS": aws_database.RDS,
        "aws.database.Aurora": aws_database.Aurora,
        "aws.database.Dynamodb": aws_database.Dynamodb,
        "aws.database.ElastiCache": aws_database.ElastiCache,
        "aws.database.Redshift": aws_database.Redshift,
        "aws.database.Neptune": aws_database.Neptune,
        "aws.database.DocumentDB": lambda n: aws_database.RDS(n),
        "aws.database.DynamodbDax": aws_database.DynamodbDax,
        "aws.database.Timestream": aws_database.Timestream,
        "aws.database.KeyspacesManagedApacheCassandraService": lambda n: aws_database.RDS(n),
        "aws.storage.S3": aws_storage.S3,
        "aws.storage.EFS": aws_storage.EFS,
        "aws.storage.EBS": aws_storage.EBS,
        "aws.storage.Fsx": aws_storage.Fsx,
        "aws.storage.Backup": aws_storage.Backup,
        "aws.storage.S3Glacier": aws_storage.S3Glacier,
        "aws.security.Cognito": aws_security.Cognito,
        "aws.security.WAF": aws_security.WAF,
        "aws.security.Shield": aws_security.Shield,
        "aws.security.CertificateManager": aws_security.CertificateManager,
        "aws.security.KMS": aws_security.KMS,
        "aws.security.SecretsManager": aws_security.SecretsManager,
        "aws.security.IAM": aws_security.IAM,
        "aws.security.Guardduty": aws_security.Guardduty,
        "aws.security.Inspector": aws_security.Inspector,
        "aws.security.Macie": aws_security.Macie,
        "aws.integration.SQS": aws_integration.SQS,
        "aws.integration.SNS": aws_integration.SNS,
        "aws.integration.Eventbridge": aws_integration.Eventbridge,
        "aws.integration.StepFunctions": aws_integration.StepFunctions,
        "aws.integration.MQ": aws_integration.MQ,
        "aws.integration.Appsync": aws_integration.Appsync,
        "aws.analytics.KinesisDataStreams": aws_analytics.KinesisDataStreams,
        "aws.analytics.KinesisDataFirehose": aws_analytics.KinesisDataFirehose,
        "aws.analytics.Glue": aws_analytics.Glue,
        "aws.analytics.Athena": aws_analytics.Athena,
        "aws.analytics.ElasticsearchService": aws_analytics.ElasticsearchService,
        "aws.analytics.EMR": aws_analytics.EMR,
        "aws.analytics.Quicksight": lambda n: aws_analytics.Athena(n),
        "aws.analytics.ManagedStreamingForKafka": aws_analytics.ManagedStreamingForKafka,
        "aws.management.Cloudwatch": aws_management.Cloudwatch,
        "aws.management.Cloudtrail": aws_management.Cloudtrail,
        "aws.management.Cloudformation": aws_management.Cloudformation,
        "aws.management.SystemsManager": aws_management.SystemsManager,
        "aws.management.Config": aws_management.Config,
        "aws.devtools.Codebuild": aws_devtools.Codebuild,
        "aws.devtools.Codepipeline": aws_devtools.Codepipeline,
        "aws.devtools.Codecommit": aws_devtools.Codecommit,
        "aws.devtools.Codedeploy": aws_devtools.Codedeploy,
    }

    try:
        with Diagram(diagram_info.get("name", "Architecture"), filename=str(output_dir / output_stem), show=False, direction="TB"):
            nodes = {}

            for res in resources:
                rid = res.get("id", "")
                rname = res.get("name", rid)
                rtype = res.get("type", "")

                node_cls = NODE_MAP.get(rtype, aws_general.General)
                if callable(node_cls):
                    nodes[rid] = node_cls(rname)
                else:
                    nodes[rid] = aws_general.General(rname)

            rel_count = 0
            for res in resources:
                rid = res.get("id", "")
                for rel in res.get("relates", []):
                    target = rel.get("to", "")
                    label = rel.get("label", "")
                    if rid in nodes and target in nodes:
                        try:
                            if label:
                                nodes[rid] >> Edge(label=label) >> nodes[target]
                            else:
                                nodes[rid] >> nodes[target]
                            rel_count += 1
                        except Exception:
                            pass

        return f"✅ PNG generated with {len(nodes)} nodes and {rel_count} edges"

    except Exception as e:
        return f"⚠️ PNG generation failed: {e}"
