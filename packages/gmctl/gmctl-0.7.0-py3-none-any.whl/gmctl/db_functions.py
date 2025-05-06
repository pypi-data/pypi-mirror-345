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

from typing import List, Dict, Any

def handle_pagination(gmclient, resource_path, payload, number_of_records):
    all_records = []
    start_key = None
    while True:
        payload["start_key"] = start_key
        response = gmclient.post(resource_path, payload)
        if not response:
            break
        records = response.get('deployments', [])
        start_key = response.get('last_evaluated_key', None)
        all_records.extend(records)
        if len(all_records) >= number_of_records or not start_key:
            break

    # trim all_records to number_of_records
    records = all_records[:number_of_records]
    return records

def get_deployments(service, gmclient, conditions, number_of_records) -> List[Dict[str, Any]]:
    resource_path = f"/deployments/{service}/query"
    payload = {}
    service_keys = {
        "ecs": ["repo_url", "commit_hash", "account_id", "region", "service", "cluster", "status"],
        "lambda": ["repo_url", "commit_hash", "account_id", "region", "function_name", "status"],
        "k8s" : ["repo_url", "commit_hash", "account_id", "region", "app_name", "namespace", "cluster", "status"]
    }
    keys = service_keys[service]
    for key in keys:
        if key in conditions and conditions[key]:
            payload[key] = conditions[key]
    deployments = handle_pagination(gmclient, resource_path, payload, number_of_records)
    return deployments