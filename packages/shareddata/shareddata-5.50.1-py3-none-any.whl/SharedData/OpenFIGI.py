import requests
import os
import json

class OpenFIGI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENFIGI_API_KEY')
        self.base_url = 'https://api.openfigi.com/v3'
        self.headers = {'Content-Type': 'application/json'}
        if self.api_key:
            self.headers['X-OPENFIGI-APIKEY'] = self.api_key

        # Load mapping values at startup
        self.mapping_values = self.load_mapping_values()

    def create_mapping_job(self, id_type, id_value, 
                           exch_code=None, mic_code=None, currency=None, market_sec_des=None, 
                           security_type=None, security_type2=None, include_unlisted_equities=False, 
                           option_type=None, strike=None, contract_size=None, coupon=None, 
                           expiration=None, maturity=None, state_code=None):
        """
        Create a mapping job dictionary for the /v3/mapping endpoint.

        Args:
            id_type (str): Type of third-party identifier.
            id_value (str or int): The value for the third-party identifier.
            exch_code (str, optional): Exchange code of the desired instrument.
            mic_code (str, optional): Market identification code.
            currency (str, optional): Currency of the desired instrument.
            market_sec_des (str, optional): Market sector description.
            security_type (str, optional): Security type.
            security_type2 (str, optional): Alternative security type.
            include_unlisted_equities (bool, optional): Include unlisted equities.
            option_type (str, optional): Option type (Call or Put).
            strike (list, optional): Strike price interval [a, b].
            contract_size (list, optional): Contract size interval [a, b].
            coupon (list, optional): Coupon interval [a, b].
            expiration (list, optional): Expiration date interval [a, b].
            maturity (list, optional): Maturity date interval [a, b].
            state_code (str, optional): State code.

        Returns:
            dict: A dictionary representing a mapping job.
        """
        job = {
            'idType': id_type,
            'idValue': id_value
        }

        # Add optional parameters if provided
        if exch_code is not None:
            job['exchCode'] = exch_code
        if mic_code is not None:
            job['micCode'] = mic_code
        if currency is not None:
            job['currency'] = currency
        if market_sec_des is not None:
            job['marketSecDes'] = market_sec_des
        if security_type is not None:
            job['securityType'] = security_type
        if security_type2 is not None:
            job['securityType2'] = security_type2
        if include_unlisted_equities:
            job['includeUnlistedEquities'] = include_unlisted_equities
        if option_type is not None:
            job['optionType'] = option_type
        if strike is not None:
            job['strike'] = strike
        if contract_size is not None:
            job['contractSize'] = contract_size
        if coupon is not None:
            job['coupon'] = coupon
        if expiration is not None:
            job['expiration'] = expiration
        if maturity is not None:
            job['maturity'] = maturity
        if state_code is not None:
            job['stateCode'] = state_code

        return job

    def map_identifiers(self, mapping_jobs):
        """
        Map third-party identifiers to FIGIs.

        Args:
            mapping_jobs (list): A list of mapping job dictionaries.

        Returns:
            list: A list of results corresponding to each mapping job.
        """
        # Validate mapping jobs
        for job in mapping_jobs:
            self.validate_mapping_job(job)

        url = f"{self.base_url}/mapping"
        response = requests.post(url, json=mapping_jobs, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def validate_mapping_job(self, job):
        """
        Validate a mapping job against loaded mapping values.

        Args:
            job (dict): The mapping job to validate.

        Raises:
            ValueError: If any of the job's values are invalid.
        """
        for key in job:
            if key in self.mapping_values:
                if job[key] not in self.mapping_values[key]:
                    raise ValueError(f"Invalid value '{job[key]}' for key '{key}'. Valid values are: {self.mapping_values[key]}")        

    def get_mapping_values(self, key):
        """
        Get the current list of values for a given key.

        Args:
            key (str): The key for which to fetch the mapping values.

        Returns:
            list: The list of mapping values.
        """
        url = f"{self.base_url}/mapping/values/{key}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        if 'values' in data:
            return data['values']
        elif 'error' in data:
            raise Exception(data['error'])
        elif 'warning' in data:
            print("Warning:", data['warning'])
            return []
        return []

    def save_mapping_values_to_json(self, json_file='openfigi_mapping_values.json'):
        """
        Save all mapping values to a JSON file at startup.
        
        Args:
            json_file (str): The filename to save the mapping values.
        
        Returns:
            dict: The mapping values from the API.
        """
        keys = ['idType', 'exchCode', 'micCode', 'currency', 'marketSecDes',
                'securityType', 'securityType2', 'stateCode']
        
        mapping_values = {}
        print("Starting the process to save mapping values.")
        for key in keys:
            try:
                print(f"Fetching mapping values for key: {key}")
                mapping_values[key] = self.get_mapping_values(key)
                print(f"Successfully retrieved values for key: {key}")
            except Exception as e:
                print(f"Error retrieving values for key {key}: {e}")
        
        print(f"Saving mapping values to {json_file}...")
        with open(json_file, 'w') as f:
            json.dump(mapping_values, f, indent=4)
        print("Mapping values successfully saved to JSON file.")
        
        return mapping_values

    def load_mapping_values(self, json_file='openfigi_mapping_values.json'):
        """
        Load mapping values from JSON file.

        Args:
            json_file (str): The filename to load the mapping values from.

        Returns:
            dict: The loaded mapping values.
        """
        if not os.path.exists(json_file):
            return self.save_mapping_values_to_json(json_file)
        
        # print(f"Loading mapping values from {json_file}...")
        with open(json_file, 'r') as f:
            return json.load(f)
