import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts

# Can't do local imports
# from ..common import (
#     BUCKET_ID,
#     DATABASE_NAME,
#     DATABASE_PASSWORD,
#     DATABASE_URL,
#     DATABASE_USER,
#     KUBECONFIG,
#     REPOSITORY_URL,
#     SERVICE_ACCOUNT_NAME,
# )

REPOSITORY_URL = "repo-url"
KUBECONFIG = "kubeconfig"
SERVICE_ACCOUNT_NAME = "sa-name"
DATABASE_URL = "db-url"
DATABASE_NAME = "db-name"
DATABASE_USER = "db-user"
DATABASE_PASSWORD = "db-pass"
BUCKET_ID = "bucket-id"

stack_ref = pulumi.StackReference("mzai-mlrunner/pulumi-aws/dev")


bucket_id = stack_ref.get_output(BUCKET_ID)

db_url = stack_ref.get_output(DATABASE_URL)
db_name = stack_ref.get_output(DATABASE_NAME)
db_user = stack_ref.get_output(DATABASE_USER)
db_pass = stack_ref.get_output(DATABASE_PASSWORD)


repository_url = stack_ref.get_output(REPOSITORY_URL)

ray_tag = ""
platform_tag = ""

service_account_name = stack_ref.get_output(SERVICE_ACCOUNT_NAME)

kubeconfig = stack_ref.get_output(KUBECONFIG)

# TODO Import DB Instance from prior stack
db_instance = stack_ref.get_output(DATABASE_URL)


# TODO Kube config assumes aws cli setup and running
cluster_provider = kubernetes.Provider(
    "clusterProvider", kubeconfig=kubeconfig, enable_server_side_apply=True
)  # opts=pulumi.ResourceOptions(depends_on=[cluster])

# helm install raycluster kuberay/ray-cluster --version 1.1.0
# TODO Get ray head svc address as output
# TODO Replace with CRD directly
kube_ray = Chart(
    "ray-cluster",
    ChartOpts(
        chart="ray-cluster",
        version="1.1.0",
        fetch_opts=FetchOpts(
            repo="https://ray-project.github.io/kuberay-helm/",
        ),
        values={
            "image": {
                "repository": "381492205691.dkr.ecr.us-east-2.amazonaws.com/repository-004e6f0",  # TODO
                "tag": "job-runner-0.1",  # TODO
            },
            "common": {
                "containerEnv": [
                    {"name": "BACKEND_HOST", "value": "backend-svc"},
                    {"name": "BACKEND_PORT", "value": "80"},
                ],
            },
        },
    ),
    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster_provider]),
)

platform_backend_deployment = kubernetes.apps.v1.Deployment(
    "platform-api",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels={
            "appClass": "platform-api",
        },
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=2,
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "appClass": "platform-api",
            },
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels={
                    "appClass": "platform-api",
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                service_account_name=service_account_name,
                containers=[
                    kubernetes.core.v1.ContainerArgs(
                        name="platform-api",
                        image=f"{repository_url}:{platform_tag}",
                        ports=[
                            kubernetes.core.v1.ContainerPortArgs(
                                name="http",
                                container_port=80,
                            )
                        ],
                        env=[
                            # TODO: Add Bucket Name
                            kubernetes.core.v1.EnvVarArgs(name="POSTGRES_DB", value=db_name),
                            kubernetes.core.v1.EnvVarArgs(name="POSTGRES_HOST", value=db_instance),
                            kubernetes.core.v1.EnvVarArgs(name="POSTGRES_USER", value=db_user),
                            kubernetes.core.v1.EnvVarArgs(name="POSTGRES_PASSWORD", value=db_pass),
                            kubernetes.core.v1.EnvVarArgs(name="POSTGRES_PORT", value="5432"),
                            kubernetes.core.v1.EnvVarArgs(
                                name="RAY_HEAD_NODE_HOST", value="ray-cluster-kuberay-head-svc"
                            ),
                            kubernetes.core.v1.EnvVarArgs(name="RAY_DASHBOARD_PORT", value="8265"),
                        ],
                    )
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster_provider]),
)

platform_svc = kubernetes.core.v1.Service(
    "backend-service",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="backend-svc",
        labels={
            "appClass": "platform-api",
        },
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        type="LoadBalancer",
        ports=[
            kubernetes.core.v1.ServicePortArgs(
                port=80,
                target_port="http",
            )
        ],
        selector={
            "appClass": "platform-api",
        },
    ),
    opts=pulumi.ResourceOptions(provider=cluster_provider, depends_on=[cluster_provider]),
)

# Export the URL for the load balanced service.
pulumi.export("svc-url", platform_svc.status.load_balancer.ingress[0].hostname)