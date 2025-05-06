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
from gmctl.db_functions import get_deployments
import json
import logging
logger = logging.getLogger(__name__)
        
import click
from gmctl.utils import print_table


def print_relevant_files(dep_artifacts):
    latest_commit_hash = dep_artifacts.get('latest_commit_hash')
    last_known_commit_hash = dep_artifacts.get('last_known_commit_hash')
    service_key = ["ecs_relevant_files", "lambda_relevant_files", "k8s_relevant_files"]
    relevant_files = {}
    relevant_files["ecs_relevant_files"] = dep_artifacts.get('ecs', {}).get('ecs_relevant_files',{})
    relevant_files["lambda_relevant_files"] = dep_artifacts.get('lambda', {}).get('lambda_relevant_files',{})
    relevant_files["k8s_relevant_files"] = dep_artifacts.get('k8s', {}).get('k8s_relevant_files', {})
    change_type = ["added_or_modified", "deleted"]
    to_display = []
    for service in service_key:
        service_relevant_files = relevant_files.get(service, {})
        for change in change_type:
            changed_files = service_relevant_files.get(change, {})
            for file_prefix, file_names in changed_files.items():
                for file_name in file_names:
                    to_display.append({"latest_commit_hash": latest_commit_hash, "previous_processed_commit_hash": last_known_commit_hash, 
                                        "file": file_name, "change": change, "relevance": service})
    print_table(to_display)
        
# Commit group with subcommands
@click.group()
@click.pass_context  
def commit(ctx):
    """Commit related commands."""
    pass

@commit.command()
@click.option('-r', '--repo-url', help='The repository URL', required=True)
@click.option('-b', '--branch', help='The branch in the repository', required=True)
@click.option('-n', '--n', help='The number of commits to get', default=1)
@click.pass_context
def get(ctx, repo_url, branch, n):
    """
    Retrieve the latest commits from the specified repository and branch.

    Args:
        repo_url (str): The URL of the repository.
        branch (str): The branch to retrieve commits from.
        n (int): The number of commits to retrieve (default is 1).

    Example:
        gmctl commit get --repo-url https://github.com/example/repo --branch main --n 5
    """
    try:
        resource_path = "/commits"
        conditions = []
        conditions.append(f"repo_url={repo_url}")
        conditions.append(f"branch={branch}")
        conditions.append(f"n={n}")
        if conditions:
            resource_path += "?" + "&".join(conditions)
        logger.info(f"Getting last {n} commits for {repo_url} branch {branch}")
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        response = gmclient.get(resource_path)
        commits = response.get("commits", [])
        if not commits:
            logger.warning(f'No commits found for {repo_url} branch {branch}')
            commits = []
        summary_keys = ["commit_hash", "repo_url", "branch", "receive_timestamp", "status"]
        to_display = []
        for commit in commits:
            to_display.append({k: commit.get(k) for k in summary_keys})
        print_table(to_display)
    except Exception as e:
        click.echo(f"Error: {e}")

@commit.command()
@click.option('-r', '--repo-url', help='The repository URL', required=True)
@click.option('-b', '--branch', help='The branch in the repository', required=True)
@click.option('-f', '--force', help='Force deploy last known commit if there are no other changes', default=False, is_flag=True)
@click.option('-v', '--verbose', is_flag=True, default=False, help='Verbose output')
@click.pass_context
def deploy(ctx, repo_url, branch, force, verbose):
    """
    Deploy the latest commit from the specified repository and branch.

    Args:
        repo_url (str): The URL of the repository.
        branch (str): The branch to deploy from.
        force (bool): Force deployment of the last known commit if there are no changes.
        verbose (bool): Enable verbose output.

    Example:
        gmctl commit deploy -r https://github.com/example/repo -b main -force
    """
    try:
        resource_path = f"/commits/deploy"
        payload = {"repo_url": repo_url, "branch": branch, "force": force}
        logger.info(f'Deploying commit: {resource_path}')
        # make a POST call to the /commits/deploy endpoint
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        deploy_response = gmclient.post(resource_path, payload)
        commit_hash = deploy_response.get('latest_commit_hash')
        print_relevant_files(deploy_response)
        if verbose:
            print(json.dumps(deploy_response, indent=4))
    except Exception as e:
        click.echo(f"Error: {e}")

@commit.command()
@click.option('-r', '--repo-url', help='The repository URL', required=True)
@click.option('-b', '--branch', help='The branch in the repository', required=True)
@click.option('-p', '--process_template', help='Perform template processing on the changed files and return file details.', default=False, is_flag=True)
@click.option('-v', '--verbose', is_flag=True, default=False, help='Verbose output')
@click.pass_context
def dryrun(ctx, repo_url, branch, process_template, verbose):
    """
    Perform a dry run to identify changes in the specified repository and branch.

    Args:
        repo_url (str): The URL of the repository.
        branch (str): The branch to perform the dry run on.
        process_template (bool): Process templates for changed files.
        verbose (bool): Enable verbose output.

    Example:
        gmctl commit dryrun -r https://github.com/example/repo -b main -p
    """
    try:
        resource_path = f"/commits/dryrun"
        payload = {"repo_url": repo_url, "branch": branch, "process_template": process_template}
        # make a POST call to the /commits/dryrun endpoint
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        dryrun_response = gmclient.post(resource_path, payload)
        dep_artifacts = dryrun_response.get('deployment_artifacts_from_changed_files',{})
        if not dep_artifacts:
            click.echo(f'No changes found for {repo_url} branch {branch}')
            return
        print_relevant_files(dep_artifacts)    
        if verbose:
            print(json.dumps(dep_artifacts, indent=4))
    except Exception as e:
        click.echo(f"Error: {e}")

@commit.command()
@click.option('-r', '--repo-url', help='The repository URL', required=True)
@click.option('-b', '--branch', help='The branch in the repository', required=True)
@click.option('-l', '--llm-provider', help='LLM provider to use (supported: openai, anthro, groq; default: groq)')
@click.option('-m', '--llm-model', help='LLM model to use')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Verbose output')
@click.pass_context
def riskiq(ctx, repo_url, branch, llm_provider, llm_model, verbose):
    """
    Perform an LLM-based risk assessment on the latest commit in specified repository and branch.

    Args:
        repo_url (str): The URL of the repository.
        branch (str): The branch to perform the dry run on.
        verbose (bool): Enable verbose output.

    Example:
        gmctl commit dryrun -r https://github.com/example/repo -b main -p
    """
    try:
        resource_path = f"/commits/riskiq"
        payload = {"repo_url": repo_url, "branch": branch, "llm_model": llm_model, "llm_provider": llm_provider}
        # make a POST call to the /commits/dryrun endpoint
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        dryrun_response = gmclient.post(resource_path, payload)
        dep_artifacts = dryrun_response.get('deployment_artifacts_from_changed_files',{})
        if not dep_artifacts:
            click.echo(f'No changes found for {repo_url} branch {branch}')
            return
        print_relevant_files(dep_artifacts)    
        if verbose:
            print(json.dumps(dep_artifacts, indent=4))
    except Exception as e:
        click.echo(f"Error: {e}")
    
@commit.command()
@click.option('-c', '--commit-hash', help='The commit hash to get relevant files.', required=True)
@click.pass_context
def files(ctx, commit_hash):
    """
    Retrieve relevant files for a specific commit.

    Args:
        commit_hash (str): The commit hash to retrieve relevant files for.

    Example:
        gmctl commit files -c abc123
    """
    try:
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        resource_path = f"/commits/{commit_hash}"
        logger.info(f'Get commit: {resource_path}')
        # make a DELETE call to the /commits/{commit_hash} endpoint
        response = gmclient.get(resource_path)
        commits = response.get("commits", [])
        summary_keys = ["receive_timestamp", "file", "change" "relevance"]
        to_display = []
        service_key = ["ecs_relevant_files", "lambda_relevant_files", "k8s_relevant_files"]
        change_type = ["added_or_modified", "deleted"]
        
        for commit in commits:
            receive_timestamp = commit.get("receive_timestamp")
            for service in service_key:
                service_relevant_files = commit.get(service, {})            
                for change in change_type:
                    changed_files = service_relevant_files.get(change, {})
                    for file_prefix, file_names in changed_files.items():
                        for file_name in file_names:
                            to_display.append({"receive_timestamp": receive_timestamp, "file": file_name, "change": change, "relevance": service})
        
        print_table(to_display)
    except Exception as e:
        click.echo(f"Error: {e}")
