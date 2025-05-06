# -----------------------------------------------------------------------------
# Copyright (c) 2025 SKAI Software Corporation. All rights reserved.
#
# This software and associated documentation files (the "Software") are the
# exclusive property of SKAI Software Corporation. Unauthorized copying,
# modification, distribution, resale, or use of this software or its components,
# in whole or in part, is strictly prohibited.
#
# The Software is licensed, not sold. All rights, title, and interest in and to
# the Software, including all associated intellectual property rights, remain
# with SKAI Software Corporation.
# -----------------------------------------------------------------------------

from tabulate import tabulate
import re

def print_table(data, tablefmt="simple"):
    """
    Prints a list of dictionaries as a table.

    Args:
        data: A list of dictionaries where each dictionary represents a row in the table.
        tablefmt: The table format to use. Defaults to "grid". Other popular formats include "plain", "pipe", "html", "latex", and more.
    """
    if not data:
        print("No data to display.")
        return

    headers = data[0].keys()
    rows = [list(item.values()) for item in data]

    print(tabulate(rows, headers=headers, tablefmt=tablefmt))

def print_status(status_details):
    """
    Prints the status of an operation.

    Args:
        status: A dictionary containing the status of an operation.
    """
    print("-------------------------------")                
    for status_detail in status_details:
        # Use regex to remove the second square-bracketed content
        modified_status = re.sub(r"\[.*?\] \[(.*?)\] ", "", status_detail)
        print(f"{modified_status}\n")
    print("-------------------------------")