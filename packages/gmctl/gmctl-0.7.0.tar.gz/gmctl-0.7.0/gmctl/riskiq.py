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
import click
from gmctl.utils import print_table

logger = logging.getLogger(__name__)

@click.group()
@click.pass_context 
def riskiq(ctx):
    """RiskIQ related commands."""
    pass

@riskiq.command()
@click.option('-c', '--commit_hash', required=True, help='The commit hash to query')
@click.option('-f', '--file_path', required=False, help='Optional file path to filter within the commit')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('-p', '--prompt_file', required=False, help='File to write the prompt')
@click.pass_context
def get(ctx, commit_hash, file_path, verbose, prompt_file):
    """
    Retrieve RiskIQ deployment assessment details from Gitmoxi.

    Example:
        gmctl riskiq get -c 1234567890abcdef
        gmctl riskiq get -c 1234567890abcdef -f path/to/file
    """
    try:
        resource_path = f"/riskiq?commit_hash={commit_hash}"
        if file_path:
            resource_path += f"&file_path={file_path}"
        
        logger.info(f'Fetching RiskIQ assessment from: {resource_path}')
        gmclient = GitmoxiClient(ctx.obj['ENDPOINT_URL'])
        response = gmclient.get(resource_path)

        if not response:
            click.echo("No RiskIQ records found.")
            return

        
        for record in response:
            click.echo(f"commit_hash: {record.get('commit_hash')}, file_path: {record.get('file_path')}")
            click.echo("============RISK IQ============")
            click.echo(record.get('assessment'))
            click.echo("================================")
            if verbose:
                click.echo("=============PROMPT=============")
                click.echo(record.get('prompt'))
                click.echo("================================")
            if prompt_file:
                with open(prompt_file, 'a') as f:
                    f.write(record.get('prompt') + "\n")     
        
    except Exception as e:
        logger.error(f"Error fetching RiskIQ data: {e}")
        click.echo(f"Failed to retrieve RiskIQ data: {str(e)}")
