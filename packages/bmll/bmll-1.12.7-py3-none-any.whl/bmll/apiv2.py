import time
import requests
import gzip
from http import HTTPStatus
from io import BytesIO

import pandas as pd

from bmll._rest import DEFAULT_SESSION


class ApiV2Client:
    """
    Helper class to manage asynchronous queries to APIv2 and their results.
    """

    def __init__(self, session=None, max_retries=300, wait_time=1):
        self._session = session if session is not None else DEFAULT_SESSION
        self._max_retries = max_retries
        self._wait_time = wait_time

    def initiate_query(self, payload, endpoint='/query'):
        """
        Initiates an asynchronous query and returns the query ID.

        Args:
            payload (dict): The payload for the POST request.
            endpoint (str): The API endpoint for initiating queries.

        Returns:
            str: The unique query ID.

        Raises:
            ValueError: If the response does not contain an 'id' key.
        """
        response = self._session.execute('post', 'apiv2', endpoint, json=payload)
        query_id = response.get('id')
        if query_id:
            return query_id
        else:
            raise ValueError(f"Response does not contain 'id': {response}")

    def poll_query(self, query_id, endpoint='/query'):
        """
        Polls the server for the status of a query until completion.

        Args:
            query_id (str): The unique ID of the query to poll.
            endpoint (str): The API endpoint for polling queries.

        Returns:
            str: A presigned URL for downloading the query results.

        Raises:
            TimeoutError: If the query does not complete within the maximum retries.
            ValueError: If the response does not contain expected data.
        """
        for attempt in range(self._max_retries):
            response = self._session.execute('get', 'apiv2', endpoint, params={'id': query_id})

            if response:
                status = response.get('status')
                if status == 'SUCCESS':
                    link = response.get('link')
                    if link:
                        return link
                    else:
                        raise ValueError(f"'link' not found in the response: {response}")
                elif status in {'FAILED', 'CANCELLED'}:
                    raise ValueError(f"Query failed or was cancelled. Status: {status}")
                else:
                    print(f"Attempt {attempt + 1}: Query status is '{status}'. Retrying...")
            else:
                raise ValueError(f"Invalid response received: {response}")

            time.sleep(self._wait_time)

        raise TimeoutError("Max retries reached. Query did not complete in time.")

    def download_data(self, url):
        """
        Downloads data from a presigned URL and loads it into a DataFrame.

        Args:
            url (str): The presigned S3 URL.


        Returns:
            pd.DataFrame: The downloaded data.

        Raises:
            Exception: If the download request fails.
        """

        # Download the data
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as gzipped_file:
                return pd.read_csv(gzipped_file)
        else:
            raise Exception(f"Failed to download data. HTTP status: {response.status_code}")

    def query(self, payload):
        """
        Orchestrates the asynchronous query process: initiation, polling, and downloading.

        Args:
            payload (dict): The payload for the POST request.

        Returns:
            pd.DataFrame: The query results as a DataFrame.
        """
        query_id = self.initiate_query(payload)

        download_link = self.poll_query(query_id)

        df = self.download_data(download_link)
        return df


_DEFAULT_CLIENT = ApiV2Client()
apiv2_query = _DEFAULT_CLIENT.query
