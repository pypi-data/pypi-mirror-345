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

#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from ngcbase.printer.nvPrettyPrint import NVPrettyPrint


class FunctionInstancePrinter(NVPrettyPrint):
    """NVCF Function Instance Printer."""

    def print_instances(self, function_instances_list: list):
        """Print function instances which flattened by pod and container.

        Args:
            function_instances_list (list): list of function instance objects
        """
        if self.format_type == "json":
            self.print_data(function_instances_list)
        else:
            columns = [
                ("clusterName", "Cluster Name"),
                ("region", "Region"),
                ("instanceId", "Instance Id"),
                ("instanceType", "Instance Type"),
                ("podName", "Pod Name"),
                ("containerName", "Container Name"),
            ]
            cols, disp = zip(*columns)
            output = [list(disp)]
            for function_instance in function_instances_list:
                for pod in function_instance["pods"]:
                    for container in pod["containers"]:
                        flatten_fuction_instance = {}
                        flatten_fuction_instance["instanceId"] = function_instance["instanceId"]
                        flatten_fuction_instance["instanceType"] = function_instance["instanceType"]
                        flatten_fuction_instance["region"] = function_instance["region"]
                        flatten_fuction_instance["clusterName"] = function_instance["clusterName"]
                        flatten_fuction_instance["podName"] = pod["podName"]
                        flatten_fuction_instance["containerName"] = container["containerName"]
                        out = FunctionInstanceOutput(flatten_fuction_instance)
                        output.append([getattr(out, col, "") for col in cols])
            self.print_data(output, True)

    def print_command_output(self, command_execution_result: dict):
        """Print command execution result.

        Args:
            command_execution_result (dict): command execution result object
        """
        if self.format_type == "json":
            self.print_data(command_execution_result)
        else:
            stdout = "=============== stdout ===============\n"
            if "stdout" in command_execution_result:
                stdout += command_execution_result["stdout"]
                self.print_ok(stdout)

            stderr = "=============== stderr ===============\n"
            if "stderr" in command_execution_result and command_execution_result["stderr"]:
                stderr += command_execution_result["stderr"]
                self.print_error(stderr)


class FunctionInstanceOutput:  # noqa: D101
    def __init__(self, function_instance):
        self.function_instance = function_instance

    @property
    def clusterName(self):  # noqa: D102
        return self.function_instance.get("clusterName", None)

    @property
    def region(self):  # noqa: D102
        return self.function_instance.get("region", "")

    @property
    def instanceType(self):  # noqa: D102
        return self.function_instance.get("instanceType", "")

    @property
    def instanceId(self):  # noqa: D102
        return self.function_instance.get("instanceId", "")

    @property
    def podName(self):  # noqa: D102
        return self.function_instance.get("podName", "")

    @property
    def containerName(self):  # noqa: D102
        return self.function_instance.get("containerName", "")
