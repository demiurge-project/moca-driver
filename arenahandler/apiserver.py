#!/usr/bin/python
""" 
This module uses the aiohttp library in order to create a web server which will
expose the service to run experiments and states. The asyncio  is also used to 
achieved asynchronous services and the negotiation between the client and the 
server is done via JSON messages.
"""
from aiohttp import web
import asyncio
import json
import time
import argparse

import experiment.experimentctrl as ec
import experiment.utils.logger as my_logger

logger = my_logger.get_logger('apiserver')


async def runExperiment(request):
    """ 
        runExperiment service is a HTTP POST request.
        ----------
        request : JSON
            Set of states and time for the corresponding experiment.
        Returns
        -------
        JSON to confirm the reception of the experiment.
    """
    logger.info("Experiment received")
    try:
        data = await request.json()
        asyncio.ensure_future(ec.runExperiment(data))
        response_obj = {'status': 'received'}
        return web.Response(text=json.dumps(response_obj))
    except ValueError as e:
        logger.error(e)
        response_obj = {'error': str(e)}
        return web.Response(text=json.dumps(response_obj))


async def runState(request):
    """ 
        runState service is a HTTP POST request.
        ----------
        request : JSON
            State to execute.
        Returns
        -------
        JSON to confirm the reception of the State.
    """
    try:
        logger.info("State received")
        data = await request.json()
        asyncio.ensure_future(ec.runState(data))
        response_obj = {'status': 'received'}
        return web.Response(text=json.dumps(response_obj))
    except ValueError as e:
        logger.error(e)
        response_obj = {'error': str(e)}
        return web.Response(text=json.dumps(response_obj))

def main():

    parser = argparse.ArgumentParser(description='ArenaHandler API Server')
    parser.add_argument(
        '--port', type=int, help='http listening port, default: 8080'
    )
    parser.add_argument(
        '--host', help='http listening host, default: localhost'
    )
    args = parser.parse_args()
    app = web.Application()
    app.router.add_post('/arena-handler/api/v1.0/experiment', runExperiment)
    app.router.add_post('/arena-handler/api/v1.0/state', runState)
    web.run_app(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
