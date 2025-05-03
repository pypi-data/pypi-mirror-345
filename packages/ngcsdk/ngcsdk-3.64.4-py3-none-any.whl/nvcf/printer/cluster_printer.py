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


class ClusterPrinter(NVPrettyPrint):
    """Cluster Printer."""

    def print_cluster_register_command(  # noqa: D102
        self,
        cluster_id: str,
        api_key: str,
        nca_id: str,
        operator_url: str,
    ):
        nvca_operator_install_cmd = (
            f'helm upgrade nvca-operator -n nvca-operator --create-namespace -i --reset-values --wait "{operator_url}"'
            f" --username='$oauthtoken' --password=\"{api_key}\""
            f' --set ngcConfig.serviceKey="{api_key}"'
            f' --set ncaID="{nca_id}"'
            f' --set clusterID="{cluster_id}"'
        )
        if self.format_type == "ascii":
            self.print_ok(
                "Install NVIDIA Cluster Agent Operator"
                "by copying and pasting this helm install command to your cluster.",
                title=True,
            )
            self.print_ok(nvca_operator_install_cmd)
        elif self.format_type == "json":
            self.print_data(nvca_operator_install_cmd)

    def print_list(self, cluster_list):  # noqa: D102
        if self.format_type == "json":
            output = cluster_list
        else:
            columns = [
                ("cluster_name", "Name"),
                ("cluster_id", "Id"),
                ("status", "Status"),
                ("occupied", "GPUs Occupied"),
                ("cluster_version", "Cluster Agent Version"),
            ]
            cols, disp = zip(*columns)
            output = [list(disp)]
            for cluster in cluster_list:
                out = ClusterOutput(cluster)
                output.append([getattr(out, col, "") for col in cols])
        self.print_data(output, True)

    def print_info(self, cluster):  # noqa: D102
        if self.format_type == "json":
            self.print_data(cluster)
        else:
            output = ClusterOutput(cluster)
            outline_tbl = self.create_output(header=False, outline=True)
            tbl = self.add_sub_table(parent_table=outline_tbl, header=False, outline=False)
            tbl.add_separator_line()
            tbl.set_title("Cluster Information")
            tbl.add_label_line("Name", output.cluster_name)
            tbl.add_label_line("Group Name", output.cluster_group_name)
            tbl.add_label_line("Id", output.cluster_id)
            tbl.add_label_line("Status", output.status)
            tbl.add_label_line("Cluster Agent Version", output.cluster_version)
            tbl.add_label_line("GPUs Occupied", output.occupied)
            tbl.add_label_line("Cloud Provider", output.cloud_provider)
            for gpu in output.gpus:
                gpu_tbl = self.add_sub_table(parent_table=tbl, header=False, outline=False)
                gpu_tbl.set_title(gpu.name)
                gpu_tbl.add_label_line(
                    "Instance Types", ",".join([instance_type.name for instance_type in gpu.instanceTypes])
                )
            tbl.add_separator_line()
            tbl.print()


class ClusterOutput:  # noqa: D101
    def __init__(self, cluster):
        self.cluster = cluster

    @property
    def cluster_name(self):  # noqa: D102
        return self.cluster.get("clusterName", None)

    @property
    def cluster_group_name(self):  # noqa: D102
        return self.cluster.get("clusterGroupName", None)

    @property
    def cluster_id(self):  # noqa: D102
        return self.cluster.get("clusterId", None)

    @property
    def cloud_provider(self):  # noqa: D102
        return self.cluster.get("cloudProvider", None)

    @property
    def cluster_description(self):  # noqa: D102
        return self.cluster.get("clusterDescription", None)

    @property
    def cluster_version(self):  # noqa: D102
        return self.cluster.get("nvcaVersion", None)

    @property
    def status(self):  # noqa: D102
        return self.cluster.get("status", None)

    @property
    def region(self):  # noqa: D102
        return self.cluster.get("region", None)

    @property
    def occupied(self):  # noqa: D102
        gpu_usage = self.cluster.get("gpuUsage", {})
        if not gpu_usage:
            return ""
        total_capacity = sum(usage["capacity"] for usage in gpu_usage.values())
        used_capacity = sum(usage["capacity"] - usage["available"] for usage in gpu_usage.values())
        return f"{used_capacity}/{total_capacity}" if total_capacity else "0/0"

    @property
    def gpus(self):  # noqa: D102
        return self.cluster.get("gpus", [])
