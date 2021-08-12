#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import atexit
import signal
from nuvla.api import Api
from contextlib import contextmanager


@contextmanager
def timeout(deadline, err):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(deadline)

    try:
        yield
    except TimeoutError:
        raise Exception(err)
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError


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


def stop_deployment(api, did):
    api.get(did + "/stop")


def delete_deployment(api, did):
    api.delete(did)


if __name__ == '__main__':
    args = init()

    api = Api("https://nuvla.io")

    api.login_apikey(args.api_key, args.api_secret)

    depl = api.add('deployment', {'module': {'href': args.module_id}}).data
    depl_id = depl.get('resource-id')

    atexit.register(delete_deployment, api, depl_id)

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

    atexit.register(stop_deployment, api, depl_id)

    with timeout(600, f'Timed out while waiting for deployment {depl_id} to get STARTED'):
        while True:
            live_depl = api.get(depl_id).data
            state = live_depl.get('state')
            if state == 'ERROR':
                raise Exception(f'Deployment {depl_id} failed to start')
            elif state == 'STARTED':
                break

    atexit.unregister(stop_deployment)
    atexit.unregister(delete_deployment)

    print(f"::set-output name=DEPLOYMENT_ID::{depl_id}")

