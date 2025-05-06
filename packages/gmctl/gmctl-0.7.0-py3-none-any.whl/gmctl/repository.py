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

from gmctl.gmclient import GitmoxiClient
import logging
logger = logging.getLogger(__name__)

import click
from gmctl.utils import print_table, print_status

# Repo group with subcommands
@click.group()
@click.pass_context 
def repo(ctx):
    """Repo related commands."""
    pass

@repo.command()
@click.option('-r', '--repo-url', required=True, help='The repository URL')
@click.option('-b', '--branches', required=True, help='The branches in the repository', multiple=True)
@click.option('-a', '--access-token-arn', required=True, help='The access token ARN')
@click.pass_context
def add(ctx, repo_url, branches, access_token_arn):
    """
    Add a new repository to Gitmoxi.

    Args:
        repo_url (str): The URL of the repository to add.
        branches (list): The branches in the repository to monitor.
        access_token_arn (str): The ARN of the access token for the repository.

    Example:
        gmctl repo add -r https://github.com/example/repo -b main -b dev -a arn:aws:secretsmanager:us-east-1:123456789012:secret:my-token
    """
    payload = {"repo_url": repo_url, "branches": list(branches), "access_token_arn": access_token_arn}
    gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
    resource_path = "/repositories/add"
    add_response = gmclient.post(resource_path, payload)
    response_message = add_response.get('message_list',[])
    print_status(response_message)

@repo.command()
@click.option('-r', '--repo-url', help='The repository URL')
@click.pass_context
def get(ctx, repo_url):
    """
    Retrieve repository details from Gitmoxi.

    Args:
        repo_url (str): The URL of the repository to retrieve. If not provided, retrieves all repositories.

    Example:
        gmctl repo get -r https://github.com/example/repo
    """
    try:
        resource_path = "/repositories"
        if repo_url:
            resource_path += f"?repo_url={repo_url}"
        logger.info(f'Getting repository: {resource_path}')
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        # make a GET call to the /repository/get endpoint with the repository URL
        response = gmclient.get(resource_path)
        if not response:
            click.echo(f'Failed to get repositories for: {resource_path}')
        keys = ['repo_url', 'branches', 'access_token_arn']
        to_display = [{k: v for k, v in repo.items() if k in keys} for repo in response]
        print_table(to_display)
    except Exception as e:
        click.echo(f"Error: {e}")

@repo.command()
@click.option('-r', '--repo-url', help='The repository URL', required=True)
@click.pass_context
def delete(ctx, repo_url):
    """
    Delete a repository from Gitmoxi.

    Args:
        repo_url (str): The URL of the repository to delete.

    Example:
        gmctl repo delete -r https://github.com/example/repo
    """
    try:
        # make a DELETE call to the /repository/delete endpoint with the repository URL
        resource_path = f"/repositories/delete?repo_url={repo_url}"
        logger.info(f'Deleting repository: {resource_path}')
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        delete_response = gmclient.delete(resource_path)
        click.echo(f"Delete response: {delete_response}")
    except Exception as e:
        click.echo(f"Error: {e}")
