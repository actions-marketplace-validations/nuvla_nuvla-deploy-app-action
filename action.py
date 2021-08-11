#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import atexit
from nuvla.api import Api

def init():
    """ Parse command-line args

    Returns:
        args: command-line argparse args
    """

    parser = argparse.ArgumentParser(description='Create NuvlaBox resource in Nuvla.io')

    parser.add_argument('--api-key',
                        dest='api_key',
                        metavar='KEY',
                        help='Nuvla.io User API Key',
                        required=True)
    parser.add_argument('--api-secret',
                        dest='api_secret',
                        metavar='SECRET',
                        help='Nuvla.io User API Secret',
                        required=True)
    parser.add_argument('--module-id',
                        dest='module_id',
                        metavar='MODULE_ID',
                        help='ID of the application module to deploy',
                        required=True)
    parser.add_argument('--credential-id',
                        dest='credential_id',
                        metavar='CREDENTIAL_ID',
                        help='ID of the credential for the infrastructure to deploy to',
                        required=True)
    parser.add_argument('--environment',
                        dest='environment',
                        metavar='ENV1=VAL1,ENV2=VAL2,...',
                        help='Comma separated list of environment variable to define for the deployment',
                        required=True)

    return parser.parse_args()


if __name__ == '__main__':
    args = init()

    api = Api("https://nuvla.io")

    api.login_apikey(args.api_key, args.api_secret)

    depl = api.add('deployment', {'module': {'href': args.module_id}}).data
    depl_id = depl.get('resource-id')

    atexit.register(api.delete, depl_id)

    depl = api.get(depl_id).data
    depl['parent'] = args.credential_id
    depl['tags'] = ["nuvla-deploy-app-action"]
    environment = []
    for env_var in args.environment.split(','):
        environment.append({
            "name": env_var.split('=')[0],
            "value": env_var.split('=')[1]
        })
    depl['module']['content']['environmental-variables'] = environment
    api.edit(depl_id, depl)

    api.get(depl_id + "/start")

    atexit.unregister(api.delete)

    print(f"::set-output name=DEPLOYMENT_ID::{depl_id}")

