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

from nvcf.api.deployment_spec import GPUSpecification
from nvcf.command.cloud_function import CloudFunctionCommand
from nvcf.printer.task_printer import TaskPrinter

from ngcbase.command.args_validation import check_dhms_duration, check_key_value_pattern
from ngcbase.command.clicommand import CLICommand
from ngcbase.constants import CANARY_ENV, DISABLE_TYPE, ENABLE_TYPE
from ngcbase.util.utils import get_environ_tag

RESULTS_HANDLING_STRATEGY_ENUM = ["UPLOAD", "NONE"]


class TaskCommand(CloudFunctionCommand):  # noqa: D101

    CMD_NAME = "task"
    DESC = "description of the task command"
    HELP = "Task Help"
    CMD_ALIAS = []

    TASK_ID_HELP = "Task ID"
    TASK_ID_METAVAR = "<task-id>"
    TELEMETRY_FLAG = ENABLE_TYPE if (get_environ_tag() <= CANARY_ENV) else DISABLE_TYPE

    def __init__(self, parser):
        super().__init__(parser)
        self.parser = parser
        self.config = self.client.config
        self.printer = TaskPrinter(self.client.config)

    @CLICommand.arguments(
        "--name",
        metavar="<name>",
        help=("Task name"),
        type=str,
        required=True,
        default=None,
    )
    @CLICommand.arguments(
        "--container-image",
        metavar="<org>/[<team>/]<image>:<tag>",
        help="Custom container image",
        type=str,
        default=None,
    )
    @CLICommand.arguments(
        "--container-args",
        metavar="<container-args>",
        help="Args to be passed in for inferencing",
        type=str,
        default=None,
    )
    @CLICommand.arguments(
        "--container-environment-variable",
        metavar="<key:value>",
        type=check_key_value_pattern,
        default=None,
        help="Environment settings for inferencing",
        action="append",
    )
    @CLICommand.arguments(
        "--gpu-specification",
        metavar="<gpu:instance_type[:backend]>",
        help="GPU specification. Format: gpu:instance_type[:backend]",
        type=str,
        required=True,
        default=None,
    )
    @CLICommand.arguments(
        "--model",
        metavar="<model>",
        help="Name of model(s) to use in the task.",
        default=None,
        action="append",
    )
    @CLICommand.arguments(
        "--resource",
        metavar="<resource>",
        help="Name of resource(s) to use in the task.",
        action="append",
        default=None,
    )
    @CLICommand.arguments(
        "--tag",
        metavar="<tag>",
        help="Tags to identify the function by, can accept multiple",
        action="append",
        default=None,
    )
    @CLICommand.arguments(
        "--description",
        metavar="<description>",
        help="Optional description for function/version",
        type=str,
        default=None,
    )
    @CLICommand.arguments(
        "--max-runtime-duration",
        metavar="<max-runtime-duration>",
        help=("Specifies the maximum runtime duration. Format: [nD][nH][nM][nS]."),
        type=str,
        action=check_dhms_duration(),
    )
    @CLICommand.arguments(
        "--max-queued-duration",
        metavar="<max-queued-duration>",
        help=("Specifies the maximum queued duration. Format: [nD][nH][nM][nS]."),
        type=str,
        action=check_dhms_duration(),
    )
    @CLICommand.arguments(
        "--termination-grace-period-duration",
        metavar="<termination-grace-period-duration>",
        help=("Specifies the duration for grace period after termination. Format: [nD][nH][nM][nS]."),
        type=str,
        action=check_dhms_duration(),
    )
    @CLICommand.arguments(
        "--result-handling-strategy",
        metavar="<result-handling-strategy>",
        help=("Specifies how results will be handled. Choices: {}".format(", ".join(RESULTS_HANDLING_STRATEGY_ENUM))),
        type=str,
        choices=RESULTS_HANDLING_STRATEGY_ENUM,
    )
    @CLICommand.arguments(
        "--result-location",
        metavar="<result-location>",
        help=("Specifies where result will be stored.}"),
        type=str,
    )
    @CLICommand.arguments(
        "--secret",
        metavar="<name:value>",
        type=check_key_value_pattern,
        default=None,
        help="Secret name/value pair",
        action="append",
    )
    @CLICommand.arguments(
        "--helm-chart",
        metavar="<org>/[<team>/]<helm-chart>:<tag>",
        help="Helm Chart in NGC used for deployment.",
        default=None,
    )
    @CLICommand.arguments(
        "--metrics-telemetry-id",
        metavar="<metrics-telemetry-id>",
        help="UUID representing the metrics telemetry.",
        type=str,
        default=None,
        feature_tag=TELEMETRY_FLAG,
    )
    @CLICommand.arguments(
        "--logs-telemetry-id",
        metavar="<logs-telemetry-id>",
        help="UUID representing the logs telemetry.",
        type=str,
        default=None,
        feature_tag=TELEMETRY_FLAG,
    )
    @CLICommand.command(help="Create a new task", description="Create a new task")
    @CLICommand.mutex(["container_image", "model"], ["helm_chart"])
    def create(self, args):  # noqa: D102
        gpu_spec = GPUSpecification.from_str(args.gpu_specification)
        resp = self.client.cloud_function.tasks.create(
            name=args.name,
            container_image=args.container_image,
            container_args=args.container_args,
            container_environment_variables=args.container_environment_variable,
            gpu_specification=gpu_spec,
            models=args.model,
            resources=args.resource,
            tags=args.tag,
            description=args.description,
            max_runtime_duration=args.max_runtime_duration,
            max_queued_duration=args.max_queued_duration,
            termination_grace_period_duration=args.termination_grace_period_duration,
            result_handling_strategy=args.result_handling_strategy,
            result_location=args.result_location,
            secrets=args.secret,
            helm_chart=args.helm_chart,
            logs_telemetry_id=args.logs_telemetry_id,
            metrics_telemetry_id=args.metrics_telemetry_id,
        )
        self.printer.print_info(resp.get("task", {}))

    @CLICommand.arguments("target", metavar=TASK_ID_METAVAR, help=TASK_ID_HELP, type=str, default=None)
    @CLICommand.arguments(
        "--secret",
        metavar="<name:value>",
        type=check_key_value_pattern,
        default=None,
        help="Secret name/value pair",
        action="append",
        required=True,
    )
    @CLICommand.command(
        name="update-secret",
        help="Update a task's secret values.",
        description="Update a task's secret value. Can specify multiple times.",
    )
    def update_secret(self, args):  # noqa: D102
        self.client.cloud_function.tasks.update_secrets(args.target, secrets=args.secret)
        self.printer.print_ok("Successfully updated secret.")

    @CLICommand.command(
        help="List of tasks",
        description="List of tasks",
        aliases=["ls"],
    )
    def list(self, _):  # noqa: D102
        resp = self.client.cloud_function.tasks.list()
        self.printer.print_list(resp)

    @CLICommand.arguments("target", metavar=TASK_ID_METAVAR, help=TASK_ID_HELP, type=str, default=None)
    @CLICommand.command(
        help="Info about a task",
        description="Info about a task",
    )
    def info(self, args):  # noqa: D102
        resp = self.client.cloud_function.tasks.info(args.target)
        self.printer.print_info(resp.get("task", {}))

    @CLICommand.arguments("target", metavar=TASK_ID_METAVAR, help=TASK_ID_HELP, type=str, default=None)
    @CLICommand.command(
        help="Delete a task",
        description="Delete a task",
        aliases=["remove", "rm"],
    )
    def delete(self, args):  # noqa: D102
        self.client.cloud_function.tasks.delete(args.target)
        self.printer.print_ok(f"Successfully deleted task {args.target}.")

    @CLICommand.arguments("target", metavar=TASK_ID_METAVAR, help=TASK_ID_HELP, type=str, default=None)
    @CLICommand.command(
        help="Cancel a task",
        description="Cancel a task",
    )
    def cancel(self, args):  # noqa: D102
        self.client.cloud_function.tasks.cancel(args.target)
        self.printer.print_ok(f"Successfully canceled task: {args.target}")

    @CLICommand.arguments("target", metavar=TASK_ID_METAVAR, help=TASK_ID_HELP, type=str, default=None)
    @CLICommand.command(
        help="List of events for a task",
        description="List of events for a task",
    )
    def events(self, args):  # noqa: D102
        resp = self.client.cloud_function.tasks.events(args.target)
        self.printer.print_task_events(resp)

    @CLICommand.arguments("target", metavar=TASK_ID_METAVAR, help=TASK_ID_HELP, type=str, default=None)
    @CLICommand.command(
        help="List of results for a task",
        description="List of results for a task",
    )
    def results(self, args):  # noqa: D102
        resp = self.client.cloud_function.tasks.results(args.target)
        self.printer.print_task_results(resp)

    @CLICommand.arguments("target", metavar=TASK_ID_METAVAR, help=TASK_ID_HELP, type=str, default=None)
    @CLICommand.command(
        help="List of logs for a task",
        description="List of logs for a task",
    )
    def logs(self, args):  # noqa: D102
        resp = self.client.cloud_function.tasks.logs(args.target)
        self.printer.print_task_logs(resp)
