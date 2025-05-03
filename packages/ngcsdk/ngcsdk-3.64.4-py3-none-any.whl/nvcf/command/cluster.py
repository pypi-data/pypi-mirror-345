#
# Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. ALL RIGHTS RESERVED.
#
# This software product is a proprietary product of Nvidia Corporation and its affiliates
# (the "Company") and all right, title, and interest in and to the software
# product, including all associated intellectual property rights, are and
# shall remain exclusively with the Company.
#
# This software product is governed by the End User License Agreement
# provided with the software product.
#

from nvcf.command.cloud_function import CloudFunctionCommand
from nvcf.printer.cluster_printer import ClusterPrinter

from ngcbase.command.clicommand import CLICommand
from ngcbase.errors import NgcException


class ClusterCommand(CloudFunctionCommand):  # noqa: D101

    CMD_NAME = "cluster"
    DESC = "Description of the cluster command"
    HELP = "Get information about clusters available"
    CMD_ALIAS = []

    TARGET_HELP = "Cluster Id"
    CLUSTER_METAVAR = "<cluster-id>"

    def __init__(self, parser):
        super().__init__(parser)
        self.parser = parser
        self.config = self.client.config
        self.printer = ClusterPrinter(self.client.config)

    @CLICommand.command(help="List Clusters", description="List clusters.", aliases=["ls"])
    def list(self, _):  # noqa: D102
        clusters = self.client.cloud_function.clusters.list()
        self.printer.print_list(clusters)

    @CLICommand.arguments("target", metavar=CLUSTER_METAVAR, help=TARGET_HELP, type=str, default=None)
    @CLICommand.command(help="Info about a cluster", description="Info about a cluster")
    def info(self, args):  # noqa: D102
        cluster = self.client.cloud_function.clusters.info(args.target)
        self.printer.print_info(cluster)

    @CLICommand.arguments("target", metavar=CLUSTER_METAVAR, help=TARGET_HELP, type=str, default=None)
    @CLICommand.command(help="Delete a cluster", description="Delete a cluster", aliases=["rm", "remove"])
    def delete(self, args):  # noqa: D102
        self.client.cloud_function.clusters.delete(args.target)
        self.printer.print_ok(f"Succesfully deleted cluster {args.target}")

    @CLICommand.arguments(
        "--cluster-name",
        help="The name for the cluster. This field is not changeable once configured.",
        type=str,
        required=True,
    )
    @CLICommand.arguments(
        "--cluster-group-name",
        help=(
            "The name of the cluster group, typically identical to the cluster name,"
            "allowing function deployment across grouped clusters."
        ),
        type=str,
        required=True,
    )
    @CLICommand.arguments(
        "--cloud-provider",
        help="The cloud platform on which the cluster is deployed.",
        type=str,
        required=True,
        choices=["AZURE", "AWS", "OCI", "ON-PREM", "GCP", "DGX-CLOUD"],
    )
    @CLICommand.arguments(
        "--region",
        help="The region where the cluster is deployed.",
        type=str,
        required=True,
        choices=[
            "us-east-1",
            "us-west-1",
            "us-west-2",
            "eu-central-1",
            "eu-west-1",
            "eu-north-1",
            "eu-south-1",
            "ap-east-1",
        ],
    )
    @CLICommand.arguments(
        "--cluster-description",
        help="Optional description providing additional context about the cluster.",
        type=str,
        default=None,
    )
    @CLICommand.arguments("--ssa-client-id", help="SSA client ID", type=str, required=True)
    @CLICommand.arguments(
        "--capability",
        help="Capabilities",
        action="append",
        default=["DynamicGPUDiscovery"],
        choices=["DynamicGPUDiscovery", "LogPosting", "CachingSupport"],
    )
    @CLICommand.arguments(
        "--attribute",
        help="Attributes",
        action="append",
        default=None,
    )
    @CLICommand.arguments(
        "--custom-attribute",
        help="Custom attributes",
        action="append",
        default=None,
    )
    @CLICommand.arguments(
        "--authorized-nca-id",
        help="Authorized NCA IDs",
        action="append",
        default=None,
    )
    @CLICommand.arguments("--nvca-version", help="NVCA version", type=str, default=None)
    @CLICommand.command(
        help="Register a new cluster",
        description="Register a new cluster with the specified details",
        aliases=["create", "register"],
    )
    def create(self, args):  # noqa: D102
        if not self.config.starfleet_kas_session_key:
            raise NgcException("Requires browser authentication. Use ngc config set --auth-option email.")
        cluster_id, api_key, nca_id, operator_url = self.client.cloud_function.clusters._register(
            cluster_name=args.cluster_name,
            cluster_group_name=args.cluster_group_name,
            cluster_description=args.cluster_description,
            cloud_provider=args.cloud_provider,
            region=args.region,
            ssa_client_id=args.ssa_client_id,
            capabilities=args.capability,
            custom_attributes=args.custom_attribute,
            nvca_version=args.nvca_version,
            authorized_nca_ids=args.authorized_nca_id,
        )

        self.printer.print_cluster_register_command(
            cluster_id,
            api_key,
            nca_id,
            operator_url,
        )
