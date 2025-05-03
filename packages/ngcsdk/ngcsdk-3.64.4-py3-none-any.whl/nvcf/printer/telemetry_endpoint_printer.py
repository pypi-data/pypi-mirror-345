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


class TelemetryEndpointPrinter(NVPrettyPrint):
    """Telemetry Printer."""

    def print_list(self, telems):  # noqa: D102
        if self.format_type == "json":
            output = telems
        else:
            columns = [
                ("id", "ID"),
                ("name", "Name"),
                ("endpoint", "Endpoint"),
                ("protocol", "Protocol"),
                ("provider", "Provider"),
                ("types", "Types"),
            ]
            cols, disp = zip(*columns)
            output = [list(disp)]
            for telem in telems.telemetries:
                out = TelemetryOutput(telem)
                output.append([getattr(out, col, "") for col in cols])
        self.print_data(output, True)

    def print_info(self, telemetry_ep):  # noqa: D102
        if self.format_type == "json":
            self.print_data(telemetry_ep)
        else:
            output = TelemetryOutput(telemetry_ep.telemetry)
            outline_tbl = self.create_output(header=False, outline=True)
            tbl = self.add_sub_table(parent_table=outline_tbl, header=False, outline=False)
            tbl.set_title("Telemetry Info")
            tbl.add_label_line("Id", output.id)
            tbl.add_label_line("Name", output.name)
            tbl.add_label_line("Endpoint", output.endpoint)
            tbl.add_label_line("Protocol", output.protocol)
            tbl.add_label_line("Provider", output.provider)
            tbl.add_label_line("Types", output.types)
            tbl.add_separator_line()
            tbl.print()


class TelemetryOutput:  # noqa: D101
    def __init__(self, telemetry):
        self.telemetry = telemetry

    @property
    def types(self):  # noqa: D102
        return ", ".join(self.telemetry.types)

    @property
    def name(self):  # noqa: D102
        return self.telemetry.name

    @property
    def id(self):  # noqa: D102
        return self.telemetry.telemetryId

    @property
    def endpoint(self):  # noqa: D102
        return self.telemetry.endpoint

    @property
    def protocol(self):  # noqa: D102
        return self.telemetry.protocol

    @property
    def provider(self):  # noqa: D102
        return self.telemetry.provider
