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

from nvcf.command.function import FunctionCommand
from nvcf.command.utils import FunctionTarget
from nvcf.printer.function_instance_printer import FunctionInstancePrinter

from ngcbase.command.clicommand import CLICommand
from ngcbase.constants import ENABLE_TYPE

INSTANCE_FLAG = ENABLE_TYPE


class InstanceCommand(FunctionCommand):  # noqa: D101

    CMD_NAME = "instance"
    DESC = "description of the instance command"
    HELP = "function instance Help"
    CMD_ALIAS = []

    TARGET_HELP = "Function. Format: function-id:[version]"
    FUNCTION_METAVAR = "<function-id>:[<function-version-id>]"
    VERSION_METAVAR = "<function-id>:<function-version-id>"
    PAYLOAD_FILE_HELP = (
        "JSON file in format expected by given function. When stream is true, you may need to modify this payload."
    )
    FILTER_AUTHORIZATION_CHOICES = ["private", "public", "authorized"]
    CLI_HELP = INSTANCE_FLAG

    def __init__(self, parser):
        super().__init__(parser)
        self.parser = parser
        self.config = self.client.config
        self.printer = FunctionInstancePrinter(self.client.config)

    @CLICommand.arguments("target", metavar=FUNCTION_METAVAR, help=TARGET_HELP, type=str, default=None)
    @CLICommand.command(
        help="List a function version active instances",
        description="List a function version instances",
        aliases=["ls"],
        feature_tag=INSTANCE_FLAG,
    )
    def list(self, args):  # noqa: D102
        ft: FunctionTarget = FunctionTarget(
            target_string=args.target,
            id_required=True,
            version_required=True,
        )
        resp = self.client.cloud_function.functions.instances.list(function_id=ft.id, function_version_id=ft.version)
        self.printer.print_instances(resp.get("functionInstances", {}))

    @CLICommand.arguments(
        "--container-name",
        metavar="<container-name>",
        help="Target container to execute container",
        type=str,
        default=None,
    )
    @CLICommand.arguments(
        "--pod-name",
        metavar="<pod-name>",
        help="Target pod which including the target container",
        type=str,
        default=None,
    )
    @CLICommand.arguments(
        "--command",
        metavar="<command>",
        help="Command to execute",
        type=str,
        default=None,
    )
    @CLICommand.arguments("target", metavar=FUNCTION_METAVAR, help=TARGET_HELP, type=str, default=None)
    @CLICommand.arguments(
        "--timeout",
        metavar="<timeout>",
        help="Timeout for the command execution",
        type=int,
        default=60,
    )
    @CLICommand.command(
        help="Execute command on target container",
        description="Info about a version",
        aliases=["exec"],
        feature_tag=INSTANCE_FLAG,
    )
    def execute(self, args):  # noqa: D102
        ft: FunctionTarget = FunctionTarget(
            target_string=args.target,
            id_required=True,
            version_required=True,
        )
        resp = self.client.cloud_function.functions.instances.execute_commands(
            function_id=ft.id,
            function_version_id=ft.version,
            pod_name=args.pod_name,
            container_name=args.container_name,
            command=args.command,
            timeout=args.timeout,
        )

        self.printer.print_command_output(resp)

    @CLICommand.arguments(
        "--container-name",
        metavar="<container-name>",
        help="Target container to query logs. Must be used with --pod-name",
        type=str,
        default=None,
    )
    @CLICommand.arguments(
        "--pod-name",
        metavar="<pod-name>",
        help="Target pod which including the target container. Must be used with --container-name",
        type=str,
        default=None,
    )
    @CLICommand.arguments(
        "--instance-id",
        metavar="<instance-id>",
        help="Target instance id.",
        type=str,
        default=None,
    )
    @CLICommand.arguments("target", metavar=FUNCTION_METAVAR, help=TARGET_HELP, type=str, default=None)
    @CLICommand.command(
        help="Read the target instance logs help",
        description="Read the target instance logs",
        aliases=[],
        feature_tag=INSTANCE_FLAG,
    )
    def logs(self, args):  # noqa: D102
        ft: FunctionTarget = FunctionTarget(args.target)
        events = self.client.cloud_function.functions.instances.query_logs(
            function_id=ft.id,
            function_version_id=ft.version,
            pod_name=args.pod_name,
            container_name=args.container_name,
            instance_id=args.instance_id,
        )
        for event in events:
            print(event.data)
