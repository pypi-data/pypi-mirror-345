import os
import pandas as pd
from typing import Union, List
import requests
import json
import time
from brynq_sdk_brynq import BrynQ



class AbacusAPI(BrynQ):

    def __init__(self, interface_id: str, system_type:str ,debug: bool = False):
        """
        For the full documentation, see: https://apihub.abacus.ch/endpoints/2024
        """
        super().__init__()
        self.interface_id = interface_id
        self.system_type = system_type
        self.access_token, mandants = self._get_credentials()
        self.base_url = f"https://abaweb.arcon.ch/api/entity/v1/mandants/{mandants}"

    def _get_credentials(self):
        """
        Retrieves an OAuth2 access token using system credentials.
        """
        credentials = self.interfaces.credentials.get(interface_id=self.interface_id ,system='abacus', system_type=self.system_type)
        credentials = credentials['data']
        # def get(self, interface_id: str, system: str, system_type: Optional[str] = None,
        #         test_environment: bool = False) -> Union[dict, List[dict]]:

        url = "https://abaweb.arcon.ch/oauth/oauth2/v1/token?grant_type=client_credentials"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, headers=headers,
                                 auth=(credentials['client_id'], credentials['client_secret']))
        response.raise_for_status()  # Raise an HTTPError for bad responses

        access_token = response.json()['access_token']
        mandants = credentials['mandant_id']
        return access_token, mandants

    def _get_paginated_data(self, endpoint_or_url: str) -> List[dict]:
        """
        Retrieves data from the API, handling both paginated and single-entity responses.
        Automatically refreshes the access token after processing a certain number of records.
        :param endpoint_or_url: The API endpoint or URL to call.
        :return: A list of data records (either from 'value' or single-entity responses).
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        all_data = []
        next_url = None
        skip_count = 0  # Track how many records we've skipped for pagination

        while True:
            url = next_url if next_url else f"{self.base_url}/{endpoint_or_url}"
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 429:
                    # Handle rate limiting by waiting and retrying
                    retry_after = int(response.headers.get('Retry-After', 1))
                    print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    continue  # Retry the same request after waiting
                elif response.status_code == 401:
                    # Handle token expiration by refreshing credentials and updating headers
                    print("Access token expired. Refreshing token...")
                    self.access_token, _ = self._get_credentials()  # Use the stored label
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    continue  # Retry the same request after refreshing token
                else:
                    raise  # Re-raise other HTTP errors

            data = response.json()

            # Check if it's a single entity response or paginated 'value' response
            if 'value' in data:
                all_data.extend(data['value'])  # Paginated response, add the items
                skip_count += len(data['value'])  # Update skip count based on the number of records retrieved
            else:
                all_data.append(data)  # Single entity response, add the single item

            next_url = data.get('@odata.nextLink')

            # Refresh credentials after processing 20,000 records
            if skip_count >= 20000:
                print(f"Processed {skip_count} records. Refreshing access token...")
                self.access_token, _ = self._get_credentials()  # Use the stored label
                headers['Authorization'] = f'Bearer {self.access_token}'
                skip_count = 0  # Reset skip_count after refreshing the token

            if not next_url:
                break
            else:
                time.sleep(1)  # Sleep for 1 second between requests

        return all_data

    def generic_extraction(self, endpoint: str, sep: str = None, max_level: int = None) -> pd.DataFrame:
        """
        General method for extracting data without specific transformations.
        :param endpoint: The API endpoint to call.
        :param sep: Separator for nested JSON fields (used in pd.json_normalize).
        :param max_level: Maximum level of nesting for JSON normalization.
        :return: A pandas DataFrame containing the extracted data.
        """
        data = self._get_paginated_data(endpoint)
        df = pd.json_normalize(data, sep='.', max_level=None)
        return df


    def extract_and_save_endpoints(self, endpoints: List[str], save_directory: str):
        """
        Extract data for multiple endpoints and save the results as Parquet files.
        :param endpoints: List of endpoint names to extract data from.
        :param save_directory: Directory to save the extracted Parquet files.
        """
        try:
            os.makedirs(save_directory, exist_ok=True)  # Ensure the directory exists

            for endpoint in endpoints:
                # Extract data
                df = self.generic_extraction(endpoint=endpoint)

                # Save data as a Parquet file
                filename = f"{endpoint.replace('/', '_')}.parquet"
                file_path = os.path.join(save_directory, filename)
                df.to_parquet(file_path, index=False)

                # Log extraction success
                print(f"Extracted and saved {endpoint} to {file_path}")
        except Exception as e:
            print(f"Error extracting and saving endpoint {endpoint}: {e}")
            raise


    def get_banks(self) -> pd.DataFrame:
        """
        Retrieves bank information, fetching only the 'Id' and 'BankIdentifierCode' columns.
        :return: DataFrame containing 'Id' and 'BankIdentifierCode' for all financial institutes.
        """
        # Use $select to only retrieve the 'Id' and 'BankIdentifierCode' columns
        endpoint = "FinancialInstitutes?$select=Id,BankIdentifierCode"

        # Fetch the data using the paginated function
        data = self._get_paginated_data(endpoint)

        # Convert the data to a DataFrame, preserving only 'Id' and 'BankIdentifierCode'
        df_banks = pd.json_normalize(data)

        # Check if the DataFrame contains the required columns, just as a safeguard
        if 'Id' not in df_banks.columns or 'BankIdentifierCode' not in df_banks.columns:
            raise ValueError("The required columns 'Id' and 'BankIdentifierCode' are missing in the response.")

        return df_banks[['Id', 'BankIdentifierCode']]


    def get_address(self, history: bool = False) -> pd.DataFrame:
        """
        Get the address data from the API.
        :param history: If True, return all historical data. If False, return only the latest data.
        """
        data = self._get_paginated_data('Employees?$expand=Subject($expand=Addresses)')
        df = pd.json_normalize(data)[['Id', 'Subject.Addresses']]
        df = df.explode('Subject.Addresses')
        df = pd.json_normalize(df['Subject.Addresses'])

        if history:
            df = df.sort_values(by=['ValidFrom'], ascending=False)
        else:
            df = df.sort_values(by=['ValidFrom'], ascending=False).drop_duplicates(subset=['SubjectId'], keep='first')

        df = df[['Id', 'SubjectId', 'Street', 'HouseNumber', 'City', 'PostCode', 'CountryId', 'ValidFrom']]
        return df



    def create_employee(self, data: dict) -> requests.Response:
        """
        Create a new employee in the Abacus system.
        :param data: Dictionary containing the fields and values for the new employee.
        :return: The response object from the request.
        """
        required_fields = ['first_name', 'last_name']
        missing_required = [field for field in required_fields if field not in data or not data[field]]
        if missing_required:
            raise ValueError(f"Missing required fields for creating employee: {', '.join(missing_required)}")

        url = f"{self.base_url}/Employees"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        base_body = {
            "Sex": data.get('sex'),
            "DateOfBirth": data.get('date_of_birth'),
            "SocialInsuranceNumber": data.get('social_insurance_number'),
            "Subject": {
                "FirstName": data.get('first_name'),
                "Name": data.get('last_name'),
                "Addresses": [{
                    "Street": data.get('street'),
                    "HouseNumber": str(data.get('housenumber')),
                    "City": data.get('city'),
                    "PostCode": data.get('postal_code'),
                    "CountryId": data.get('country_code'),
                    "ValidFrom": data.get('address_valid_from')
                }]
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(base_body))
        response.raise_for_status()
        return response

    def update_employee(self, data: dict) -> requests.Response:
        """
        Update an existing employee's information in the Abacus system.
        :param data: Dictionary containing the fields and values to update.
        :return: The response object from the request.
        """
        required_fields = ['employee_id']
        missing_required = [field for field in required_fields if field not in data or not data[field]]
        if missing_required:
            raise ValueError(f"Missing required fields for updating employee: {', '.join(missing_required)}")

        url = f"{self.base_url}/Employees(Id={data['employee_id']})"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        base_body = {
            "Sex": data.get('sex'),
            "DateOfBirth": data.get('date_of_birth'),
            "SocialInsuranceNumber": data.get('social_insurance_number'),
            "Subject": {
                "FirstName": data.get('first_name'),
                "Name": data.get('last_name'),
                "Addresses": [{
                    "Id": data.get('address_id'),
                    "Street": data.get('street'),
                    "HouseNumber": str(data.get('housenumber')),
                    "City": data.get('city'),
                    "PostCode": data.get('postal_code'),
                    "CountryId": data.get('country_code'),
                    "ValidFrom": data.get('address_valid_from')
                }]
            }
        }

        response = requests.patch(url, headers=headers, data=json.dumps(base_body))
        response.raise_for_status()
        return response
