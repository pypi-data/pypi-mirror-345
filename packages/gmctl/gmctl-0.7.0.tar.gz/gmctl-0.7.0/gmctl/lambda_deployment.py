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

import click
from gmctl.gmclient import GitmoxiClient
from gmctl.db_functions import get_deployments
from gmctl.utils import print_table, print_status
import logging
import re

logger = logging.getLogger(__name__)

@click.group(name="lambda")
@click.pass_context
def lambda_cmd(ctx):
    """Lambda-related commands."""
    pass

@lambda_cmd.command()
@click.option('-r', '--repo-url', help='The repository URL')
@click.option('-c', '--commit-hash', help='The commit hash')
@click.option('-a', '--account-id', help='The AWS account ID')
@click.option('-re', '--region', help='The AWS region')
@click.option('-fn', '--function-name', help='The Lambda function name')
@click.option('-st', '--status', type=click.Choice(["PROCESSING", "PROCESSED_ERROR", "PROCESSED_SUCCESS"]), help='The deployment status')
@click.option('-N', '--number-of-records', help='Number of records', default=10)
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('-A', '--show-all', is_flag=True, help='Verbose for all deployments')
@click.pass_context
def get(ctx, repo_url, commit_hash, account_id, region, 
        function_name, status, number_of_records, verbose, show_all):
    """
    Retrieve Lambda deployment records based on the specified filters.

    Example:
        gmctl lambda get -r https://github.com/example/repo -re us-east-1 -fn my-function -st PROCESSED_SUCCESS
    """        
    try:
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        conditions = {
            "repo_url": repo_url,
            "commit_hash": commit_hash,
            "account_id": account_id,
            "region": region,
            "function_name": function_name,
            "status": status
        }

        deployments = get_deployments("lambda", gmclient, conditions, number_of_records)
        to_display = []
        summary_keys = ["repo_url", "commit_hash", "account_id", "region", "function_name", 
                        "create_timestamp", "status", "file_prefix"]

        for deployment in deployments:
            to_display.append({k: deployment.get(k) for k in summary_keys})
        
        print_table(to_display)

        if verbose:
            for deployment in deployments:
                if not show_all and deployment.get("status") != "PROCESSED_ERROR":
                    continue
                print("-------------------------------")
                print(f"\n{deployment.get('status')}, {deployment.get('repo_url')}, {deployment.get('file_prefix')}, "
                      f"{deployment.get('function_name')}, {deployment.get('account_id')}, {deployment.get('region')}: \n")
                print_status(deployment.get("status_details", []))
                print("-------------------------------")
        return

    except Exception as e:
        click.echo(f"Error: {e}")
        return