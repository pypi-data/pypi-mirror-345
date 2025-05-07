from brynq_sdk_brynq import BrynQ
import pandas as pd
from typing import Union, List
import requests
import json
from urllib.parse import urljoin


class Marad(BrynQ):
    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        For the full documentation, see: https://external.marad.ms/swagger/ui/index
        """
        super().__init__()
        self.headers = self.__get_headers(label=label)
        self.base_url = "https://external.marad.ms/api/"
        self.debug = debug
        self.timeout = 3600

    def __get_headers(self, label) -> dict:
        """
        Retrieves the API key for the given system and label, and constructs the headers required for an HTTP request.

        Args:
        label (str): The label used to identify the credentials in the system.

        Returns:
        dict: A dictionary containing the necessary headers, including the API key and the 'Content-Type' as 'application/json'.
        """
        credentials = self.get_system_credential(system='marad', label=label)
        api_key = credentials['api_key']
        headers = {
            'apiKey': api_key,
            'Content-Type': 'application/json'
        }
        return headers

    def get_data_from_system(self, end_point: str) -> pd.DataFrame | str:
        """
        Fetches data from the specified API endpoint and returns the data as a pandas DataFrame.
        If the request fails, it returns an error message.

        Args:
        end_point (str): The API endpoint to fetch data from.

        Returns:
        Union[Tuple[pd.DataFrame, Any], str]:
            - If successful, a tuple containing:
                - data_df (pd.DataFrame): The data normalized as a pandas DataFrame.
                - data_json (Any): The original JSON response from the API.
            - If unsuccessful, a string with an error message and status code.
        """
        end_point = end_point
        full_url = urljoin(self.base_url, end_point)
        payload = {}
        response = requests.request("GET", full_url, headers=self.headers, data=payload, timeout=self.timeout)

        if response.status_code == 200:
            data_df = pd.json_normalize(response.json())
            return data_df

        else:
            return f"Failed to retrieve data from the API. Status code: {response.status_code}, Error Message: {response.text}"

    def post_data_to_system(self, end_point: str, data: dict) -> requests.Response :
        """
        Sends a POST request to the specified endpoint with the provided data. It receives data in a dictionary format and
        coverts it to a list with the dict in it because the API accepts a list and we send one record at a time.

        Args:
        end_point (str): The API endpoint to send the POST request to.
        data (dict): The data to be sent in the body of the request, in JSON format.

        Returns:
        requests.Response: The HTTP response object from the API.

        Raises:
        HTTPError: If the response status code indicates an error.
        """
        end_point = end_point
        full_url = urljoin(self.base_url, end_point)
        json_data = json.dumps([data])

        if self.debug:
            print(json_data)

        response = requests.request("POST", full_url, headers=self.headers, data=json_data, timeout=self.timeout)
        response.raise_for_status()

        return response

    def put_data_to_system(self, end_point: str,data: dict) -> requests.Response:
        """
        Sends a PUT request to the specified end_point with the given data. It receives data in a dictionary format and
        coverts it to a list with the dict in it because the API accepts a list and we send one record at a time.

        Args:
        end_point (str): The API endpoint to send the request to.
        data (dict): The data to be sent in the request body.

        Returns:
        requests.Response: The HTTP response object returned from the request.

        Raises:
        HTTPError: If the request returned an unsuccessful status code.
        """
        end_point = end_point
        full_url = urljoin(self.base_url, end_point)
        json_data  = json.dumps([data])

        if self.debug:
            print(json_data)

        response = requests.request("PUT", full_url, headers=self.headers, data=json_data, timeout=self.timeout)
        response.raise_for_status()

        return response