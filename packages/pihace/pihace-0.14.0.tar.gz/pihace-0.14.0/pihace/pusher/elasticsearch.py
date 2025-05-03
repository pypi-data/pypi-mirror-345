# -*- coding: utf-8 -*-
"""pihace.pusher.elasticsearch: Push health check results to Elasticsearch."""

import traceback
from elasticsearch import Elasticsearch
from pihace.healthcheck import HealthCheck
from time import sleep

class ElasticSearchPusher:
    def __init__(self, healthcheck: HealthCheck, es_url: str, index: str = "pihace-health"):
        """
        Initialize the ElasticSearchPusher.

        :param es_url: URL to the Elasticsearch instance.
        :param healthcheck: Instance of HealthCheck to run and log.
        :param index: Name of the Elasticsearch index to use.
        """
        self.es = Elasticsearch([es_url])
        self.healthcheck = healthcheck
        self.index = index

    def push(self) -> bool:
        """
        Run the health check and push the result to Elasticsearch.

        :return: True if push succeeded, False otherwise.
        """
        try:
            result = self.healthcheck.check(output="dict")

            self.es.index(index=self.index, document=result)
            return True
        except Exception:
            print("Unexpected error:\n", traceback.format_exc())
            return False
    
            
    def push_forever_in_loop(self, interval: int = 60) -> None:
        """
        Run the health check and push the result to Elasticsearch in a loop.

        :param interval: Time in seconds between each health check.
        """
        while True:
            self.push()
            sleep(interval)

