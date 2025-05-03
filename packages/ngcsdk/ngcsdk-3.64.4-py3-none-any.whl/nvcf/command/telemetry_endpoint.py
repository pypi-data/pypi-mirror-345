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
from nvcf.printer.telemetry_endpoint_printer import TelemetryEndpointPrinter

from ngcbase.command.clicommand import CLICommand
from ngcbase.constants import ENABLE_TYPE


class TelemetryEndpointCommand(CloudFunctionCommand):  # noqa: D101

    CMD_NAME = "telemetry-endpoint"
    DESC = "Description of the telemetry command"
    HELP = "Get information about telemetry endpoints."
    CMD_ALIAS = []
    CLI_HELP = ENABLE_TYPE

    def __init__(self, parser):
        super().__init__(parser)
        self.parser = parser
        self.config = self.client.config
        self.printer = TelemetryEndpointPrinter(self.client.config)

    @CLICommand.command(help="List Telemetries.", description="List telemetries.", aliases=["ls"])
    def list(self, _):  # noqa: D102
        telemetries = self.client.cloud_function.telemetry_endpoints.list()
        self.printer.print_list(telemetries)

    @CLICommand.arguments(
        "--name",
        metavar="<name>",
        help="Telemetry Name",
        required=True,
        default=None,
    )
    @CLICommand.arguments(
        "--key",
        metavar="<key>",
        help="Telemetry key",
        required=True,
        default=None,
    )
    @CLICommand.arguments(
        "--endpoint",
        metavar="<endpoint>",
        help="Telemetry endpoint URL",
        required=True,
        default=None,
    )
    @CLICommand.arguments(
        "--protocol",
        metavar="<protocol>",
        help="Protocol used for communication",
        required=True,
        default=None,
        choices=["HTTP", "GRPC"],
    )
    @CLICommand.arguments(
        "--provider",
        metavar="<provider>",
        help="Protocol used for communication",
        required=True,
        default=None,
        choices=[
            "DATADOG",
            "GRAFANA_CLOUD",
        ],
    )
    @CLICommand.arguments(
        "--type",
        metavar="<Telemetry type>",
        help="Set of telemetry data types",
        required=True,
        action="append",
        default=None,
        choices=[
            "LOGS",
            "METRICS",
        ],
    )
    @CLICommand.arguments(
        "--instance",
        metavar="<instance>",
        help="Instance id for telemetry endpoints.",
        default=None,
    )
    @CLICommand.command(
        help="Create a new telemetry endpoint.",
        description="Create a new telemetry endpoint.",
        aliases=["add"],
    )
    def create(self, args):  # noqa: D102
        telemetry_endpoint = self.client.cloud_function.telemetry_endpoints.create(
            name=args.name,
            endpoint=args.endpoint,
            protocol=args.protocol,
            provider=args.provider,
            types=args.type,
            key=args.key,
            instance=args.instance,
        )
        self.printer.print_info(telemetry_endpoint)

    @CLICommand.arguments(
        "target",
        metavar="<telemetry-id>",
        help="Id of telemtry endpoint to delete",
        type=str,
    )
    @CLICommand.command(
        help="Delete a telemetry endpoint.",
        description="Delete a telemetry endpoint.",
        aliases=["delete", "rm"],
    )
    def remove(self, args):  # noqa: D102
        self.client.cloud_function.telemetry_endpoints.delete(args.target)
        self.printer.print_ok(f"Succesfully deleted telemetry {args.target}")
