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

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from gmctl.gmclient import GitmoxiClient
from gmctl.db_functions import get_deployments
import re
import logging

logger = logging.getLogger(__name__)

import click
from gmctl.utils import print_table, print_status

@click.group()
@click.pass_context
def k8s(ctx):
    pass

@k8s.command()
@click.option('-r', '--repo-url', help='The repository URL')
@click.option('-c', '--commit-hash', help='The commit hash')
@click.option('-a', '--account-id', help='The AWS account ID')
@click.option('-re', '--region', help='The AWS region')
@click.option('-d', '--deployment', help='The EKS service')
@click.option('-cl', '--cluster', help='The EKS cluster')
@click.option('-n', '--namespace', help='The EKS cluster')
@click.option('-st', '--status', type=click.Choice(["PROCESSING", "PROCESSED_ERROR", "PROCESSED_SUCCESS"]), help='The deployment status')
@click.option('-N', '--number-of-records', help='Number of records', default=10)
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('-A', '--show-all', is_flag=True, help='Verbose for all deployments')
@click.pass_context
def get(ctx, repo_url, commit_hash, account_id, region, 
        deployment, cluster, namespace, status, number_of_records, verbose, show_all):
    """
    Retrieve EKS deployment records based on the specified filters.

    Args:
        repo_url (str): The repository URL to filter deployments.
        commit_hash (str): The commit hash to filter deployments.
        account_id (str): The AWS account ID to filter deployments.
        region (str): The AWS region to filter deployments.
        deployment (str): The EKS deployment name to filter deployments.
        cluster (str): The EKS cluster name to filter deployments.
        namespace (str): The namespace for the EKS deployment
        status (str): The deployment status to filter deployments. 
                      Choices are "PROCESSING", "PROCESSED_ERROR", "PROCESSED_SUCCESS".
        number_of_records (int): The number of records to retrieve (default is 10).
        verbose (bool): Enable verbose output for detailed information.
        show_all (bool): Show all deployments with verbose output.

    Example:
        gmctl eks get -r https://github.com/example/repo -re us-west-2 -s my-service -st PROCESSED_SUCCESS
    """       
    try:
        
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        conditions = {"repo_url": repo_url, "commit_hash": commit_hash, "account_id": account_id,
                      "region": region, "app_name": deployment, "namespace": namespace, "cluster": cluster, "status": status}
        deployments = get_deployments("k8s", gmclient, conditions, number_of_records)
        to_display = []
        summary_keys = ["id", "commit_hash", "app_name", "namespace", "cluster", "create_timestamp", "status"]
        if verbose:
            summary_keys = ["id", "commit_hash", "region", "service", 
                        "cluster", "create_timestamp", "status", "file_prefix","repo_url", "account_id"]
        for deployment in deployments:
            to_display.append({k: deployment.get(k) for k in summary_keys})
            
        print_table(to_display)
        if verbose:
            for deployment in deployments:
                if not show_all and deployment.get("status") != "PROCESSED_ERROR":
                    continue
                print("-------------------------------")
                print(f"\n{deployment.get('status')}, {deployment.get('repo_url')}, {deployment.get('file_prefix')}, "
                    f"{deployment.get('app_name')}, {deployment.get('namespace')}, {deployment.get('cluster')}, {deployment.get('account_id')}, {deployment.get('region')}: \n")             
                print_status(deployment.get("status_details", []))
                print("-------------------------------")
    except Exception as e:
        click.echo(f"Error: {e}")