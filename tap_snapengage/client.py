import json
import requests
import requests.exceptions
import singer
import time
import urllib

LOGGER = singer.get_logger()


class SnapEngageAPI:
    URL_TEMPLATE = 'https://www.snapengage.com/api/v2/{}/'
    MAX_RETRIES = 10

    def __init__(self, config):
        self.api_key = config['api_key']
        self.org_id = config['org_id']
        self.base_url = self.URL_TEMPLATE.format(self.org_id)
        self.headers = {'Authorization': self.api_key}

    def get(self, url, params=None):
        if not url.startswith('https://'):
            url = f'{self.base_url}{url}'

        for num_retries in range(self.MAX_RETRIES):

            LOGGER.info(f'snapengage get request {url}')

            resp = requests.get(url, headers=self.headers, params=params)

            try:
                resp.raise_for_status()
            except requests.exceptions.RequestException:
                if resp.status_code == 429 and num_retries < self.MAX_RETRIES:
                    LOGGER.info('api query snapengage rate limit', extra={
                        'org_id': self.org_id
                    })
                    time.sleep(15)
                elif resp.status_code >= 500 and num_retries < self.MAX_RETRIES:
                    LOGGER.info('api query snapengage 5xx error', extra={
                        'org_id': self.org_id
                    })
                    time.sleep(10)
                else:
                    raise Exception(f'snapengage query error: {resp.status_code}')

            if resp and resp.status_code == 200:
                break

        return resp.json()

    def paging_get(self, url, results_key, params):

        next_page = url

        while next_page:
            data = self.get(next_page, params)
            for record in data[results_key]:
                yield record

            next_page = data.get('linkToNextSetOfResults')
