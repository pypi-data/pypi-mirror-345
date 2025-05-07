import hashlib
import json
from typing import Callable, Tuple, Any, Union, List
import requests
import pandas as pd

from brynq_sdk_brynq import BrynQ


class AllSolutions(BrynQ):
    def __init__(self, interface_id: int, debug: bool = False):
        super().__init__()
        self.timeout = 3600
        self.token = None
        self.refresh_token = None
        self.debug = debug
        credentials = self.interfaces.credentials.get(interface_id=interface_id, system='all-solutions', system_type=None)
        self.url = credentials['data']['url']
        self.client_id = credentials['data']['client_id']
        self.secret_id = credentials['data']['secret_id']
        self.username = credentials['data']['username']
        self.password = credentials['data']['password']
        self.content_type_header = {'Content-Type': 'application/json'}
        self.filter_freeform_string = "$filter-freeform"

    # authentication functions
    def _get_refreshtoken(self):
        signature = hashlib.sha1(f"{self.username}{self.client_id}{self.secret_id}".encode()).hexdigest()
        response = requests.post(url=f"{self.url}login",
                                 headers=self.content_type_header,
                                 data=json.dumps({
                                     "Username": self.username,
                                     "Signature": signature,
                                     "Password": self.password,
                                     "ClientId": self.client_id
                                 }),
                                 timeout=self.timeout)
        if self.debug:
            print(response.content)
        response.raise_for_status()
        self.token = response.json()['Token']
        self.refresh_token = response.json()['RefreshToken']

    def _get_token(self):
        signature = hashlib.sha1(f"{self.refresh_token}{self.secret_id}".encode()).hexdigest()
        response = requests.post(url=f"{self.url}refreshtoken",
                                 headers=self.content_type_header,
                                 data=json.dumps({
                                     "RefreshToken": self.refresh_token,
                                     "Signature": signature
                                 }),
                                 timeout=self.timeout)
        if self.debug:
            print(response.content)
        response.raise_for_status()
        self.token = response.json()['Token']
        self.refresh_token = response.json()['RefreshToken']

    def _get_headers_allsol(self):
        if self.token is None:
            self._get_refreshtoken()
        else:
            self._get_token()
        headers = {**self.content_type_header, **{'Authorization': f'{self.token}'}}

        return headers

    # Get functions
    def get_employees(self, filter: str = None):
        self._get_headers_allsol()
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        params.update({self.filter_freeform_string: filter}) if filter else None
        while more_results:
            response = requests.get(url=f"{self.url}mperso",
                                    headers=self._get_headers_allsol(),
                                    params=params,
                                    timeout=self.timeout)
            if self.debug:
                print(response.content)
            response.raise_for_status()
            more_results = response.json()['Paging']['More']
            params['cursor'] = response.json()['Paging']['NextCursor']
            total_response += response.json()['Data']

        return total_response

    def extract_employees_allsolutions_dataframe(self, column_map) -> pd.DataFrame:
        """
        This method is where you extract data from allsolutions
        :return: dataframe with allsolutions data
        """
        resp = self.get_employees()
        df_employees = pd.DataFrame(resp)
        df_employees['name_use_code'] = df_employees['ab02.naamstelling'].apply(lambda x: x.get('id'))
        df_employees['name_use_description'] = df_employees['ab02.naamstelling'].apply(lambda x: x.get('desc'))
        df_employees.rename(mapper=column_map, axis=1, inplace=True, errors='ignore')
        df_employees = df_employees[column_map.values()]
        return df_employees

    def get_sickleave(self, filter: str = None):
        self._get_headers_allsol()
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        if filter:
            params.update({self.filter_freeform_string: filter})

        while more_results:
            response = requests.get(url=f"{self.url}mzktml",
                                    headers=self._get_headers_allsol(),
                                    params=params,
                                    timeout=self.timeout)
            if self.debug:
                print(response.content)
            response.raise_for_status()
            data = response.json()
            more_results = data['Paging']['More']
            params['cursor'] = data['Paging']['NextCursor']
            total_response += data['Data']

        # Now make an additional call to retrieve the partial absence percentage
        for entry in total_response:
            sickleave_id = entry.get('Id')
            if sickleave_id:
                partial_response = requests.get(
                    url=f"{self.url}mzktml/{sickleave_id}/partieelverzuim",
                    headers=self._get_headers_allsol(),
                    timeout=self.timeout
                )
                partial_response.raise_for_status()
                partial_data = partial_response.json().get('Data', [])
                if partial_data:
                    entry['percentage'] = partial_data[0].get('ap47.prc', None)

        return total_response

    def get_detailed_sickleave(self, filter: str = None):
        self._get_headers_allsol()
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        if filter:
            params.update({self.filter_freeform_string: filter})

        while more_results:
            response = requests.get(
                url=f"{self.url}mzktml",
                headers=self._get_headers_allsol(),
                params=params
            )
            if self.debug:
                print(response.content)
            response.raise_for_status()
            data = response.json()
            more_results = data['Paging']['More']
            params['cursor'] = data['Paging']['NextCursor']
            total_response += data['Data']

        detailed_response = []

        # Iterate over each sick leave entry
        for entry in total_response:
            sickleave_id = entry.get('Id')
            employee_code = entry.get('ap46.persnr')  # Adjust the key as per actual data
            search_name = entry.get('ab02.zoeknaam')  # Adjust the key as per actual data
            sickleave_start_date = entry.get('ap46.ziektedat')
            sickleave_end_date = entry.get('ap46.dat-hervat-arbo')

            if sickleave_id:
                partial_response = requests.get(
                    url=f"{self.url}mzktml/{sickleave_id}/partieelverzuim",
                    headers=self._get_headers_allsol()
                )
                partial_response.raise_for_status()
                partial_data = partial_response.json().get('Data', [])

                # Iterate over each partial sick leave entry
                for partial_entry in partial_data:
                    partial_sickleave_id = partial_entry.get('Id')
                    partial_start_date = partial_entry.get('ap47.ingangsdat')
                    partial_end_date = partial_entry.get('h-einddat')
                    percentage = partial_entry.get('ap47.prc')

                    detailed_response.append({
                        'search_name': search_name,
                        'employee_code': employee_code,
                        'sickleave_id': sickleave_id,
                        'start_date': sickleave_start_date,
                        'end_date': sickleave_end_date,
                        'partial_sickleave_id': partial_sickleave_id,
                        'partial_start_date': partial_start_date,
                        'partial_end_date': partial_end_date,
                        'percentage': percentage
                    })

        return detailed_response

    def get_persons(self, filter: str = None):
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        params.update({self.filter_freeform_string: filter}) if filter else None
        while more_results:
            response = requests.get(url=f"{self.url}mrlprs",
                                    headers=self._get_headers_allsol(),
                                    params=params,
                                    timeout=self.timeout)
            if self.debug:
                print(response.content)
            response.raise_for_status()
            more_results = response.json()['Paging']['More']
            params['cursor'] = response.json()['Paging']['NextCursor']
            total_response += response.json()['Data']

        return total_response

    def get_contracts(self, filter: str = None):
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        if filter:
            params.update({self.filter_freeform_string: filter})

        while more_results:
            response = requests.get(url=f"{self.url}/mappar",  # Adjusted the endpoint
                                    headers=self._get_headers_allsol(),
                                    params=params,
                                    timeout=self.timeout)
            if self.debug:
                print(response.content)

            response.raise_for_status()

            response_data = response.json()
            more_results = response_data.get('Paging', {}).get('More', False)
            next_cursor = response_data.get('Paging', {}).get('NextCursor')

            if next_cursor:
                params['cursor'] = next_cursor
            else:
                more_results = False

            total_response += response_data.get('Data', [])

        return total_response

    def get_contract(self, employee_id: str, filter: str = None):
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        params.update({self.filter_freeform_string: filter}) if filter else None
        while more_results:
            response = requests.get(url=f"{self.url}mperso/{employee_id}/arbeidsovereenkomsten",
                                    headers=self._get_headers_allsol(),
                                    params=params,
                                    timeout=self.timeout)
            if self.debug:
                print(response.content)
            response.raise_for_status()
            more_results = response.json()['Paging']['More']
            params['cursor'] = response.json()['Paging']['NextCursor']
            total_response += response.json()['Data']

        return total_response

    def get_hours(self, employee_id: str, filter: str = None):
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        params.update({self.filter_freeform_string: filter}) if filter else None
        while more_results:
            response = requests.get(url=f"{self.url}mperso/{employee_id}/werktijden2wk",
                                    headers=self._get_headers_allsol(),
                                    params=params,
                                    timeout=self.timeout)
            response.raise_for_status()
            more_results = response.json()['Paging']['More']
            params['cursor'] = response.json()['Paging']['NextCursor']
            total_response += response.json()['Data']

        return total_response

    def get_managers(self, employee_id: str, filter: str = None):
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        params.update({self.filter_freeform_string: filter}) if filter else None
        while more_results:
            response = requests.get(url=f"{self.url}mperso/{employee_id}/manager",
                                    headers=self._get_headers_allsol(),
                                    params=params,
                                    timeout=self.timeout)
            response.raise_for_status()
            more_results = response.json()['Paging']['More']
            params['cursor'] = response.json()['Paging']['NextCursor']
            total_response += response.json()['Data']

        return total_response

    def get_functions(self, employee_id: str, filter: str = None):
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        params.update({self.filter_freeform_string: filter}) if filter else None
        while more_results:
            response = requests.get(url=f"{self.url}mperso/{employee_id}/functies",
                                    headers=self._get_headers_allsol(),
                                    params=params,
                                    timeout=self.timeout)
            response.raise_for_status()
            more_results = response.json()['Paging']['More']
            params['cursor'] = response.json()['Paging']['NextCursor']
            total_response += response.json()['Data']

        return total_response

    def get_costcenters(self, employee_id: str, filter: str = None):
        total_response = []
        more_results = True
        params = {"pageSize": 500}
        params.update({self.filter_freeform_string: filter}) if filter else None
        while more_results:
            headers = self._get_headers_allsol()
            response = requests.get(url=f"{self.url}mperso/{employee_id}/thuisafdelingen",
                                    headers=headers,
                                    params=params,
                                    timeout=self.timeout)
            response.raise_for_status()
            more_results = response.json()['Paging']['More']
            params['cursor'] = response.json()['Paging']['NextCursor']
            total_response += response.json()['Data']

        return total_response \
 \
    # Post functions
    def create_employee(self, data: dict) -> json:
        """
        Create a new employee in All Solutions
        :param data: all the fields that are required to create a new employee
        :return: response json
        """
        required_fields = ["employee_code", "employee_id_afas", "date_in_service", "email_work", "costcenter", "search_name", "function", "person_id", "hours_week", "employment", 'parttime_factor']
        allowed_fields = {
            "note": "ab02.notitie-edit",
            "birth_date": "ab02.geb-dat",
            "email_private": "ab02.email",
            'employment': "ab02.srt-mdw",
            "phone_work": "ab02.telefoon-int",
            "mobile_phone_work": "ab02.mobiel-int",
            "contract_end_date": "ab02.einddat-contract",
            "nickname": "ab02.roepnaam",
            "costcenter": "ab02.ba-kd",
            "function": "ab02.funktie",
            "manager_employee_code": "ab02.manager",
            "name_use": "ab02.naamstelling",
            "parttime_factor": "h-dt-factor-afas"
        }
        self.__check_fields(data=data, required_fields=required_fields)

        payload = {
            "Data": [
                {
                    "ab02.persnr": data['employee_code'],
                    "ab02.kenmerk[113]": data['employee_id_afas'],
                    "ab02.zoeknaam": data['search_name'],
                    "ab02.indat": data['date_in_service'],
                    "ab02.email-int": data['email_work'],
                    "ab02.ba-kd": data['costcenter'],
                    "ab02.funktie": data['function'],
                    "ab02.srt-mdw": data["employment"],
                    "h-aanw": data['hours_week'],
                    "h-aanw2": data['hours_week'],
                    "h-default7": True,
                    "ab02.contr-srt-kd": "1",
                    "ab02.notitie-edit": "Afas koppeling"
                }
            ]
        }
        if 'contract_end_date' in data:
            # also add "ab02.einddat-proef" as the same date
            payload['Data'][0].update({"ab02.uitdat": data['contract_end_date']})
        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        url = f'{self.url}mrlprs/{data["person_id"]}/medewerkergegevens'
        print(payload)

        response = requests.post(url=url,
                                 headers=self._get_headers_allsol(),
                                 data=json.dumps(payload))
        if self.debug:
            print(response.content)
            print(payload)
            response.raise_for_status()

        return response

    def create_person(self, data: dict) -> json:
        """
        Create a new person in All Solutions
        :param data: data of the person
        :return: response json
        """
        required_fields = ["search_name", "employee_id_afas", "employee_code", "birth_date", "initials", "city", "lastname",
                           "street", "housenumber", "postal_code"]
        allowed_fields = {
            "note": "ma01.notitie-edit",
            "prefix": "ma01.voor[1]",
            'firstname': "ma01.voornaam",
            'gender': "ma01.geslacht",
            # "mobile_phone_private": "ma01.mobiel",
            # "email_private": "ma01.email",
            # "phone_private": "ma01.telefoon",
            "prefix_birthname": "ma01.voor[2]",
            "housenumber_addition": "ma01.b-appendix",
            "birthname": "ma01.persoon[2]",
        }
        self.__check_fields(data=data, required_fields=required_fields)

        payload = {
            "Data": [
                {
                    "ma01.zoeknaam": data['search_name'],
                    'ma01.kenmerk[43]': data['employee_id_afas'],
                    "ma01.persnr": data['employee_code'],
                    "ma01.geb-dat": data['birth_date'],
                    "ma01.voorl": data['initials'],
                    "ma01.roepnaam": data['nickname'],
                    "ma01.b-wpl": data['city'],
                    "ma01.persoon[1]": data['lastname'],
                    "ma01.b-adres": data['street'],
                    "ma01.b-num": data['housenumber'],
                    "ma01.b-pttkd": data['postal_code'],
                    "h-default6": True,
                    "h-default8": True,
                    "ma01.rel-grp": 'Medr',
                    "h-chk-ma01": False  # Check if person already exists
                }
            ]
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.post(url=f"{self.url}mrlprs",
                                 headers=self._get_headers_allsol(),
                                 data=json.dumps(payload),
                                 timeout=self.timeout)
        # if self.debug:
        # print("______________________payload______________________")
        # print(payload)
        # print("______________________response______________________")
        # print(response.content)
        response.raise_for_status()

        return response

    def create_timetable(self, data: dict) -> json:
        """
        Update hours in all solutions
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'parttime_factor', 'start_date', 'hours_per_week']

        self.__check_fields(data=data, required_fields=required_fields)
        rounded_partime_factor = round(data['parttime_factor'], 4)
        # hours_per_week = 38 * rounded_partime_factor
        # make sure the hours per week are rounded to 2 decimals
        # hours_per_week = round(hours_per_week, 2)

        payload = {
            "Data": [
                {
                    "ap23.datum": data['start_date'],
                    "h-aanw": data['hours_per_week'],
                    "h-default1": True,
                    "h-aanw2": data['hours_per_week'],
                    "h-default2": True,
                    "ap23.dt-factor-afas": rounded_partime_factor,
                    "h-dt-factor-2wk": rounded_partime_factor

                }
            ]
        }
        if self.debug:
            print('new timetable')
            print(payload)
            print(data['employee_id_afas'])
        response = requests.post(url=f"{self.url}mperso/{data['employee_id']}/werktijden2wk",
                                 headers=self._get_headers_allsol(),
                                 data=json.dumps(payload),
                                 timeout=self.timeout)
        response.raise_for_status()
        return response

    def create_contract(self, data: dict) -> json:
        """
        Update person in all solutions
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'tracking_number', 'costcenter', 'function', 'hours_per_week', 'parttime_factor']
        allowed_fields = {
            "contract_start_date": "ap11.indat",
            "contract_end_date": "ap11.einddat-contract",
            "employee_type": "ab02.srt-mdw",
            "employment": "ab02.srt-mdw"
        }

        self.__check_fields(data=data, required_fields=required_fields)

        payload = {
            "Data": [
                {
                    "ap11.vlgnr": data['tracking_number'],
                    "ab02.ba-kd": data['costcenter'],
                    "ab02.funktie": data['function'],
                    "h-aanw": data['hours_per_week'],
                    "h-aanw2": data['hours_per_week'],
                    "h-default7": True,
                    "h-dt-factor-afas": data['parttime_factor']
                }
            ]
        }
        # add the uitdat field if it is present in the data
        if 'contract_end_date' in data:
            payload['Data'][0].update({"ap11.uitdat": data['contract_end_date']})

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.post(url=f"{self.url}mperso/{data['employee_id']}/arbeidsovereenkomsten",
                                 headers=self._get_headers_allsol(),
                                 data=json.dumps(payload),
                                 timeout=self.timeout)
        if self.debug:
            print(response.content)
            print(payload)
        response.raise_for_status()

        return response

    def create_costcenter(self, data: dict) -> json:
        """
        Update function in all solutions
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'start_year', 'start_week', 'costcenter']
        self.__check_fields(data=data, required_fields=required_fields)

        payload = {
            "Data": [
                {
                    "ab09.jaar": data['start_year'],
                    "ab09.periode": data['start_week'],
                    "ab09.ba-kd": data['costcenter']
                }
            ]
        }

        response = requests.post(url=f"{self.url}mperso/{data['employee_id']}/thuisafdelingen",
                                 headers=self._get_headers_allsol(),
                                 data=json.dumps(payload),
                                 timeout=self.timeout)
        if self.debug:
            print(response.content)
            print(payload)
        response.raise_for_status()

        return response

    def create_function(self, data: dict) -> json:
        """
        Update department in all solutions
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'start_year', 'start_week', 'function']
        self.__check_fields(data=data, required_fields=required_fields)

        allowed_fields = {
            "end_year": "ab13.tot-jaar",
            "end_week": "ab13.tot-week"
        }

        payload = {
            "Data": [
                {
                    "ab13.jaar": data['start_year'],
                    "ab13.week": data['start_week'],
                    "ab13.funktie": data['function']
                }
            ]
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.post(url=f"{self.url}mperso/{data['employee_id']}/functies",
                                 headers=self._get_headers_allsol(),
                                 data=json.dumps(payload),
                                 timeout=self.timeout)
        if self.debug:
            print(response.content)
            print(payload)
        response.raise_for_status()

        return response

    def create_sickleave(self, data):
        """
               Update hours in all solutions
               :param data: data to update
               :return: json response
               """
        required_fields = ['employee_code', 'start_date', 'activity_code', 'sickleave_code_afas']

        allowed_fields = {'end_date': "ap46.dat-hervat-arbo"}

        self.__check_fields(data=data, required_fields=required_fields)
        payload = {
            "Data": [
                {
                    "ap46.persnr": data['employee_code'],
                    "ap46.aktkd": data['activity_code'],
                    "ap46.ziektedat": data['start_date'],
                    # "ap46.dat-meld-arbo": data['start_date'],
                    "ap46.opm": f"Afas koppeling {data['sickleave_code_afas']}"

                }
            ]
        }
        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})
        url = f"{self.url}mzktml"

        if self.debug:
            print('sickleave')
            print(url)
            print(payload)

        response = requests.post(url=url,
                                 headers=self._get_headers_allsol(),
                                 data=json.dumps(payload),
                                 timeout=self.timeout)
        return response

    def create_partial_sickleave(self, data):
        """
        Upload partial sick leave data for each entry to all solutions.
        :param data: Data to upload in the request body (the entire row as a dictionary)
        :return: JSON response
        """
        # Required fields that must be present in the entry
        required_fields = ['partieel_verzuim_start_datum', 'percentage', 'sickleave_id']

        # Check required fields in the data
        self.__check_fields(data=data, required_fields=required_fields)

        # Map your data fields to the API's expected field names
        api_field_mapping = {
            'partieel_verzuim_start_datum': 'ap47.ingangsdat',
            'percentage': 'ap47.prc',
            'sickleave_code_afas': 'ap47.opm'
        }

        # Construct the payload for the entry
        payload_entry = {}
        for field, api_field in api_field_mapping.items():
            if field in data and pd.notna(data[field]) and data[field] != '':
                payload_entry[api_field] = data[field]

        payload = {
            "Data": [payload_entry]
        }

        # Construct the URL using the sickleave_id from data
        sickleave_id = data['sickleave_id']
        url = f"/mzktml/{sickleave_id}/partieelverzuim"

        # Make the POST request to the given URL
        response = requests.post(
            url=f"{self.url}{url}",
            headers=self._get_headers_allsol(),
            data=json.dumps(payload)
        )
        # Return the response (JSON)
        return response

    def update_partial_sickleave(self, data):
        """
        Upload partial sick leave data for each entry to all solutions.
        :param data: Data to upload in the request body (the entire row as a dictionary)
        :return: JSON response
        """
        # Required fields that must be present in the entry
        required_fields = ['partieel_verzuim_start_datum', 'percentage', 'sickleave_id', 'partial_sickleave_id']

        # Check required fields in the data
        self.__check_fields(data=data, required_fields=required_fields)

        # Map your data fields to the API's expected field names
        api_field_mapping = {
            'partieel_verzuim_start_datum': 'ap47.ingangsdat',
            'percentage': 'ap47.prc',
            'remarks': 'ap47.opm'
        }

        # Construct the payload for the entry
        payload_entry = {}
        for field, api_field in api_field_mapping.items():
            if field in data and pd.notna(data[field]) and data[field] != '':
                payload_entry[api_field] = data[field]

        payload = {
            "Data": [payload_entry]
        }

        # Construct the URL using the sickleave_id from data
        url = f"/mzktml/{data['sickleave_id']}/partieelverzuim/{data['partial_sickleave_id']}"

        if self.debug:
            print('partial sickleave')
            print(url)
            print(payload)

        # Make the POST request to the given URL
        response = requests.put(
            url=f"{self.url}{url}",
            headers=self._get_headers_allsol(),
            data=json.dumps(payload),
            timeout=self.timeout
        )
        # Return the response (JSON)
        return response

    def create_manager(self, data: dict) -> json:
        """
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'manager_employee_code', 'year', 'week']
        allowed_fields = {"year_to": "ap15.tot-jaar", "week_to": "ap15.tot-week"}
        self.__check_fields(data=data, required_fields=required_fields)

        payload = {"Data": [{"ap15.jaar": data['year'], "ap15.week": data['week'], "ap15.manager": data['manager_employee_code']}]}

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.post(url=f"{self.url}mperso/{data['employee_id']}/manager", headers=self._get_headers_allsol(), data=json.dumps(payload), timeout=self.timeout)
        if self.debug:
            print(response.content)
            print(payload)
        response.raise_for_status()

        return response

    # Put functions
    def update_timetable(self, data: dict) -> json:
        """
        Update hours in all solutions
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'hours_per_week', 'start_date', 'timetable_id', 'parttime_factor']

        rounded_partime_factor = round(data['parttime_factor'], 4)

        self.__check_fields(data=data, required_fields=required_fields)
        payload = {
            "Data": [
                {
                    "ap23.datum": data['start_date'],
                    "h-aanw": data['hours_per_week'],
                    "h-default1": True,
                    "h-aanw2": data['hours_per_week'],
                    "h-default2": True,
                    "ap23.dt-factor-afas": rounded_partime_factor

                }
            ]
        }
        if self.debug:
            print('edit')
            print(payload)
            print(data['employee_id_afas'])
        response = requests.put(url=f"{self.url}mperso/{data['employee_id']}/werktijden2wk/{data['timetable_id']}",
                                headers=self._get_headers_allsol(),
                                data=json.dumps(payload),
                                timeout=self.timeout)
        response.raise_for_status()
        return response

    def update_contract(self, data: dict) -> json:

        """
                Update person in all solutions
                :param data: data to update
                :return: json response
                """
        required_fields = ['employee_id', 'contract_id', 'tracking_number']
        allowed_fields = {
            "contract_end_date": "ap11.einddat-contract"
        }

        self.__check_fields(data=data, required_fields=required_fields)

        payload = {
            "Data": [
                {
                    "ap11.vlgnr": data['tracking_number']
                }
            ]
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.put(url=f"{self.url}mperso/{data['employee_id']}/arbeidsovereenkomsten/{data['contract_id']}",
                                headers=self._get_headers_allsol(),
                                data=json.dumps(payload),
                                timeout=self.timeout)
        if self.debug:
            print(response.content)
            print(payload)
        response.raise_for_status()

        return response

    def update_employee(self, data: dict) -> json:
        """
        Update an existing employee in All Solutions
        :param data: data to update
        :return:
        """
        required_fields = ['employee_id']
        allowed_fields = {
            'employee_code': 'ab02.persnr',
            'birth_date': 'ab02.geb-dat',
            'employee_id_afas': "ab02.kenmerk[113]",
            'date_in_service': 'ab02.indat',
            'date_in_service_custom': 'ab02.kenmerk[62]',
            'termination_date': 'ab02.uitdat',
            'email_work': 'ab02.email-int',
            'email_private': 'ab02.email',
            'phone_work': 'ab02.telefoon-int',
            'mobile_phone_work': 'ab02.mobiel-int',
            'note': "ab02.notitie-edit",
            'employment': "ab02.srt-mdw",
            "nickname": "ab02.roepnaam",
            "name_use": "ab02.naamstelling"
        }

        self.__check_fields(data=data, required_fields=required_fields)

        payload = {
            "Data": [
                {
                    "h-default7": True,
                    "h-default6": True,  # Find corresponding employee details
                    "h-default5": True,  # Find name automatically
                    "h-corr-adres": True,  # save address as correspondence address
                    "ab02.contr-srt-kd": "1"
                }
            ]
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.put(url=f"{self.url}mperso/{data['employee_id']}",
                                headers=self._get_headers_allsol(),
                                data=json.dumps(payload),
                                timeout=self.timeout)
        if self.debug:
            print(response.content)
            print(payload)
        response.raise_for_status()

        return response

    def update_person(self, data: dict) -> json:
        """
        Update person in all solutions
        :param data: data to update
        :return: json response
        """
        required_fields = ['person_id']
        allowed_fields = {
            "search_name": "ma01.zoeknaam",
            "employee_id_afas": "ma01.mail-nr",
            "employee_code": "ma01.persnr",
            "birth_date": "ma01.geb-dat",
            "initials": "ma01.voorl",
            "firstname": "ma01.voornaam",
            "nickname": "ma01.roepnaam",
            "prefix": "ma01.voor[1]",
            "prefix_partner": "ma01.voor[2]",
            "city": "ma01.b-wpl",
            "birth_name": "ma01.persoon[1]",
            "lastname_partner": "ma01.persoon[2]",
            "street": "ma01.b-adres",
            "housenumber": "ma01.b-num",
            "housenumber_addition": "ma01.b-appendix",
            "postal_code": "ma01.b-pttkd",
            "note": "ma01.notitie-edit",
            'gender': "ma01.geslacht"
        }

        self.__check_fields(data=data, required_fields=required_fields)

        payload = {
            "Data": [
                {
                    "h-default6": True,
                    "h-default8": True,
                    "ma01.rel-grp": 'Medr'
                }
            ]
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.put(url=f"{self.url}mrlprs/{data['person_id']}",
                                headers=self._get_headers_allsol(),
                                data=json.dumps(payload),
                                timeout=self.timeout)
        if self.debug:
            print(response.content)
            print(payload)

        response.raise_for_status()

        return response

    def update_costcenter(self, data: dict) -> json:
        """
        Update function in all solutions
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'start_year', 'start_week', 'costcenter', 'costcenter_id']
        self.__check_fields(data=data, required_fields=required_fields)

        allowed_fields = {
            "end_year": "ab09.tot-jaar",
            "end_week": "ab09.tot-per"
        }

        payload = {
            "Data": [
                {
                    "ab09.jaar": data['start_year'],
                    "ab09.periode": data['start_week'],
                    "ab09.ba-kd": data['costcenter']
                }
            ]
        }
        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.put(url=f"{self.url}mperso/{data['employee_id']}/thuisafdelingen/{data['costcenter_id']}",
                                headers=self._get_headers_allsol(),
                                data=json.dumps(payload),
                                timeout=self.timeout)
        if self.debug:
            print(response.content)
            print(payload)
        response.raise_for_status()

        return response

    def update_function(self, data: dict) -> json:
        """
        Update department in all solutions
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'start_year', 'start_week', 'function', 'function_id']
        self.__check_fields(data=data, required_fields=required_fields)

        allowed_fields = {
            "end_year": "ab13.tot-jaar",
            "end_week": "ab13.tot-week"
        }
        payload = {
            "Data": [
                {
                    "ab13.jaar": data['start_year'],
                    "ab13.week": data['start_week'],
                    "ab13.funktie": data['function']
                }
            ]
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.put(url=f"{self.url}mperso/{data['employee_id']}/functies/{data['function_id']}",
                                headers=self._get_headers_allsol(),
                                data=json.dumps(payload),
                                timeout=self.timeout)
        if self.debug:
            print(response.content)
            print(payload)
        response.raise_for_status()

        return response

    def update_worked_hours(self, data: dict) -> json:
        """
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'id', 'hours']
        self.__check_fields(data=data, required_fields=required_fields)

        payload = {
            "Data": [
                {
                    "h-aanw": data['hours']
                }
            ]
        }

        if self.debug:
            print(json.dumps(payload))
        response = requests.post(url=f"{self.url}mperso/{data['employee_id']}/Tijdelijkewerktijden",
                                 headers=self._get_headers_allsol(),
                                 data=json.dumps(payload),
                                 timeout=self.timeout)
        if self.debug:
            print(response.content)
        response.raise_for_status()

        return response.json()

    def update_contracts(self, data: dict) -> json:
        """
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_id', 'hours', 'id']
        self.__check_fields(data=data, required_fields=required_fields)

        payload = {
            "Data": [
                {
                    "h-aanw": data['hours']
                }
            ]
        }

        if self.debug:
            print(json.dumps(payload))
        response = requests.post(url=f"{self.url}mperso/{data['employee_id']}/arbeidsovereenkomsten/{data['id']}",
                                 headers=self._get_headers_allsol(),
                                 data=json.dumps(payload),
                                 timeout=self.timeout)
        if self.debug:
            print(response.content)
        response.raise_for_status()

        return response.json()

    def update_sickleave(self, data):
        """
        Update sickleave in all solutions
        :param data: data to update
        :return: json response
        """
        required_fields = ['employee_code', 'start_date', 'sickleave_id', 'sickleave_code_afas']
        allowed_fields = {'end_date': "ap46.dat-hervat-arbo"}

        self.__check_fields(data=data, required_fields=required_fields)
        payload = {
            "Data": [
                {
                    "ap46.persnr": data['employee_code'],
                    "ap46.ziektedat": data['start_date'],
                    "ap46.opm": f"Afas koppeling {data['sickleave_code_afas']}"
                }
            ]
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['Data'][0].update({allowed_fields[field]: data[field]})

        response = requests.put(url=f"{self.url}mzktml/{data['sickleave_id']}",
                                headers=self._get_headers_allsol(),
                                data=json.dumps(payload),
                                timeout=self.timeout)
        response.raise_for_status()
        return response

    @staticmethod
    def __check_fields(data: dict, required_fields: List):
        for field in required_fields:
            # Check if the field is present
            if field not in data:
                raise ValueError(f'Field {field} is required. Required fields are: {tuple(required_fields)}')

            # Check if the value of the field is None or an empty string
            if data[field] is None or data[field] == '':
                raise ValueError(f'Field {field} cannot be empty or None. Required fields are: {tuple(required_fields)}')


def format_dates(df: pd.DataFrame, date_cols: List[str]) -> pd.DataFrame:
    """
    Parse the columns in *date_cols* to pandas datetime and format them back
    to ISO‑8601 strings (YYYY‑MM‑DD). Missing/invalid values become "".
    The function mutates *df* in‑place and also returns it for convenience.
    """
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
        df[col] = df[col].dt.strftime("%Y-%m-%d").fillna("")
    return df


def build_unique_key(
        df: pd.DataFrame, *, id_col: str, date_col: str, key_col: str
) -> pd.DataFrame:
    """
    Construct a textual unique key of the form  <id>_<YYYY‑MM‑DD>.
    - *id_col*   : column holding a unique employee or entity identifier
    - *date_col* : column with a (string or datetime) date
    - *key_col*  : name of the column to create/replace
    Mutates *df* in‑place and returns it.
    """
    df[key_col] = df[id_col].astype(str) + "_" + df[date_col].astype(str)
    return df


# ---------------------------------------------------------------------------
#                OPTIONAL: duplicate‑partial‑rows logger
# ---------------------------------------------------------------------------
def log_duplicate_partials(
        df_partial: pd.DataFrame,
        write_log: Callable[[str], None],
        subset: str | List[str] = "unique_key_partial",
) -> None:
    """
    Detect rows that share the same *subset* key(s) and send a readable
    message to *write_log* for each duplicate found.
    Parameters
    ----------
    df_partial : DataFrame
        The partial‑sick‑leave DataFrame.
    write_log  : callable(str)
        Typically TaskScheduler.write_execution_log or any function that
        accepts a single string argument.
    subset     : str | list[str]
        Column(s) that must be unique; defaults to 'unique_key_partial'.
    """
    dupes = df_partial[df_partial.duplicated(subset=subset, keep=False)]
    for _, row in dupes.iterrows():
        write_log(message=
        (
            "Duplicate partial sick‑leave record — "
            f"employee_id_afas={row.get('employee_id_afas')} "
            f"employee_code={row.get('employee_code')} "
            f"key={row.get(subset)}"
        ), data=None, loglevel="INFO"
        )
