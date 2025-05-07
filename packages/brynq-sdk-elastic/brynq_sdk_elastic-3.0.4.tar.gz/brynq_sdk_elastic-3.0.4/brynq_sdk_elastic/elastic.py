import warnings
import requests
import json
import datetime
import string
import random
import pandas as pd
import os


class Elastic:
    def __init__(self, api_key: str = None, customer_name: str = None, space_name: str = None, disabled: bool = False):
        """
        A package to create indexes, users, roles, getting data, etc.
        :param api_key: The api key to connect to elasticsearch if not provided in the .env file
        """
        try:
            self.verify = False
            self.disabled = disabled
            self.timeout = 60  # seconds before request to elastic fails
            elasticsearch_host = os.getenv("ELASTIC_HOST")
            elasticsearch_port = os.getenv("ELASTIC_PORT")
            kibana_port = os.getenv("KIBANA_PORT")
            elastic_token = os.getenv('ELASTIC_API_KEY', api_key)

            if not self.disabled:
                # Check for missing environment variables and show warnings
                if elasticsearch_host is None:
                    raise KeyError("Environment variable ELASTIC_HOST is not set. Please set it and try again")
                if elasticsearch_port is None:
                    elasticsearch_port = 9200
                    warnings.warn("Environment variable ELASTIC_PORT is not set. Using default port 9200")
                if kibana_port is None:
                    kibana_port = 5601
                    warnings.warn("Environment variable KIBANA_PORT is not set. Using default port 5601")
                if elastic_token is None:
                    raise KeyError("Environment variable ELASTIC_API_KEY is not set and no api_key is provided. Please specify either one and try again")
                if os.getenv("ELASTIC_SPACE") is None:
                    warnings.warn("Environment variable ELASTIC_SPACE is not set. Using 'default'")

            # Build the host URLs
            self.elasticsearch_host = f'https://{elasticsearch_host}:{elasticsearch_port}'
            self.kibana_host = f'http://{elasticsearch_host}:{kibana_port}'
            self.elastic_token = elastic_token if elastic_token is not None else api_key
            self.space_name = os.getenv('ELASTIC_SPACE', 'default') if space_name is None else space_name
            self.client_user = os.getenv('BRYNQ_SUBDOMAIN', 'default').lower().replace(' ', '_') if customer_name is None else customer_name.lower().replace(' ', '_')

            if self.client_user == 'default':
                warnings.warn("Environment variable BRYNQ_SUBDOMAIN is not set and customer_name is not specified. Using 'default'")

            print(f"Elasticsearch running on: {elasticsearch_host}")

            self.timestamp = int(datetime.datetime.now().timestamp())
            self.elastic_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'ApiKey {self.elastic_token}'
            }
            self.kibana_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'ApiKey {self.elastic_token}',
                'kbn-xsrf': 'true'
            }
            if not self.disabled:
                self.get_health()
                self.create_space(space_name=self.space_name)
        except Exception as e:
            raise ConnectionError('Could not establish a connection: {}'.format(str(e)))

    def get_health(self) -> str:
        """
        Check if a there is a connection with elasticsearch
        :return: if the connection is established or not
        """
        # Get the health of the database connection
        if self.disabled:
            return 'Healthy connection established with elasticsearch!'

        try:
            health = requests.get(url=f'{self.elasticsearch_host}/_cat/health?', headers=self.elastic_headers, verify=self.verify, timeout=self.timeout).status_code
            if health != 200:
                raise ConnectionError(f"Elasticsearch cluster health check failed with status code: {health}")
            else:
                return 'Healthy connection established with elasticsearch!'
        except Exception as e:
            raise ConnectionError(f'Elasticsearch was not reachable, error is: {e}')

    def initialize_customer(self):
        # Creates the index for the user if it does not exist yet
        self.create_index(index_name=f'task_execution_log_{self.client_user}')

        # creates the data view for the space and index if it does not exist yet
        self.create_data_view(space_name=self.space_name, view_name=f'task_execution_log_{self.client_user}', name=f'Task execution log {self.client_user}', time_field='started_at')

    def create_space(self, space_name: str) -> str:
        """
        This function creates a space in elasticsearch for the current customer
        :param space_name: The name of the space
        :return: The status of the creation of the space
        """
        try:
            if self.disabled:
                return 'Space creation disabled'

            url = f'{self.kibana_host}/api/spaces/space'
            data = {
                "id": space_name,
                "name": space_name,
                "description": f"This is the space for {space_name}",
                "color": "#aabbcc",
                "initials": space_name[0:2].upper(),
                "disabledFeatures": [],
            }

            response = requests.head(url=url + fr'/{space_name}', headers=self.kibana_headers, verify=self.verify, timeout=self.timeout)

            if response.status_code == 200:
                return f'Index \'{space_name}\' already exists'
            else:
                response = requests.post(url=url, headers=self.kibana_headers, data=json.dumps(data), verify=self.verify, timeout=self.timeout)
                if response.status_code == 200:
                    return f'space {space_name} created'
                else:
                    raise ConnectionError(f'Could not create space {space_name} with status code: {response.status_code}. Response: {response.text}')
        except:
            message = "Could not create space, since this is not strictly necessary to write logs, continue without it"
            print(message)
            return message

    def create_data_view(self, space_name: str, view_name: str, name: str, time_field: str) -> str:
        """
        This function creates a data view in elasticsearch for the current customer
        :param space_name: The name of the space
        :param view_name: The name of the data view
        :param time_field: The name of the time field
        :return: The status of the creation of the data view
        """
        try:
            if self.disabled:
                return 'Data view creation disabled'

            url = f'{self.kibana_host}/s/{space_name}/api/data_views/data_view'
            data = {
                "data_view": {
                    "title": f'{view_name}*',
                    "id": f'{view_name}',
                    "name": f'{name}',
                    "timeFieldName": time_field
                }
            }

            response = requests.head(url=url + fr'/{view_name}', headers=self.kibana_headers, verify=self.verify, timeout=self.timeout)

            if response.status_code == 200:
                return f'Data view \'{view_name}\' already exists'
            else:
                response = requests.post(url=url, headers=self.kibana_headers, data=json.dumps(data), verify=self.verify, timeout=self.timeout)
                if response.status_code == 200:
                    return f'data view {view_name} created'
                else:
                    raise ConnectionError(f'Could not create data view {view_name} with status code: {response.status_code}. Response: {response.text}')
        except:
            message = "Could not create data view, since this is not strictly necessary to write logs, continue without it"
            print(message)
            return message

    def get_all_docs_from_index(self, index: str) -> pd.DataFrame:
        """
        Get all the documents from a certain index
        :param index: the name of the index
        :return: The response of the request to elasticsearch
        """
        if self.disabled:
            return pd.DataFrame()

        size = 10000

        # Get all indices with the given index from the function parameter. For each day a new index.
        indices = requests.get(url=self.elasticsearch_host + '/' + index + '*/_settings', headers=self.elastic_headers, verify=self.verify, timeout=self.timeout).json()
        index_list = {}

        for index in indices:
            index_date = datetime.date(2023, 4, 3)
            index_list[str(index_date)] = index

        url = f'{self.elasticsearch_host}/{index}/_search'

        # initial request
        params = {"size": size, "scroll": "10m"}
        response = requests.get(url=url, headers=self.elastic_headers, params=params, verify=self.verify, timeout=self.timeout).json()

        # next requests until finished
        scroll_id = response['_scroll_id']
        total = response['hits']['total']['value']
        response = pd.json_normalize(response['hits']['hits'])
        response.drop(['_id', '_index', '_score'], axis=1, inplace=True)

        # start all the request to elastic based on the scroll_id and add to the initial response
        loop_boolean = True
        body = json.dumps({"scroll": "10m", "scroll_id": scroll_id})
        url = f'{self.elasticsearch_host}/_search/scroll'

        while loop_boolean and total > size:
            next_response = pd.json_normalize(requests.post(url=url, data=body, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout).json()["hits"]["hits"])
            next_response.drop(['_id', '_index', '_score'], axis=1, inplace=True)
            response = pd.concat([response, next_response], ignore_index=True)
            print(f'Received {len(next_response)} documents from index {index}')
            if len(next_response) != size:
                loop_boolean = False
        return response

    def delete_index(self, index_name) -> str:
        """
        Deletes an existing index if it exists. Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-delete-index.html
        :param index_name: The index you want to delete
        :return: The response of the request to elasticsearch
        """
        if self.disabled:
            return 'Index deletion disabled'

        # Check if index exists
        url = f'{self.elasticsearch_host}/{index_name}'
        response = requests.head(url=url, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout)

        # Delete index if it exists
        if response.status_code == 404:
            return f'Index \'{index_name}\' does not exist'
        else:
            response = requests.delete(url=url, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout)
            if response.status_code == 200:
                return f'Index \'{index_name}\' deleted'
            else:
                raise ConnectionError(f'Could not delete index {index_name} with status code: {response.status_code}. Response: {response.text}')

    def create_index(self, index_name: str) -> str:
        """
        Creates a new index in the elasticsearch instance. Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html
        :param index_name: The name of the desired index
        :return: The response of the request to elasticsearch
        """
        if self.disabled:
            return 'Index creation disabled'

        url = f'{self.elasticsearch_host}/{index_name}-000001'
        response = requests.head(url=url, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout)
        if response.status_code == 200:
            body = {
                "settings": {
                    "index.lifecycle.name": "task_execution_log",
                    "index.lifecycle.rollover_alias": f"{index_name}_rollover"
                }
            }
            response = requests.put(url=f"{url}/_settings", headers=self.elastic_headers, json=body, verify=self.verify, timeout=self.timeout)
            if response.status_code == 200:
                return f'Index {index_name} settings updated'
            else:
                raise ConnectionError(f'Could not update index {index_name} with status code: {response.status_code}. Response: {response.text}')
        else:
            body = {
                "aliases":
                    {
                        f"{index_name}_rollover": {
                            "is_write_index": True
                        }
                    },
                "settings": {
                    "index.lifecycle.name": "task_execution_log",
                    "index.lifecycle.rollover_alias": f"{index_name}_rollover"
                }
            }
            response = requests.put(url=url, headers=self.elastic_headers, json=body, verify=self.verify, timeout=self.timeout)
            if response.status_code == 200:
                return f'Index {index_name} created'
            else:
                raise ConnectionError(f'Could not create index {index_name} with status code: {response.status_code}. Response: {response.text}')

    def create_or_update_role(self, role_name: str, index: str) -> str:
        """
        Creates or updates a role. All the indexes which start with the same constraint as the role_name, are added to the role
        :param role_name: The name of the desired role. Most often the username which also is used for the mysql database user (sc_customer)
        :param index: one or more index names in a list.
        :return: The response of the request to elasticsearch
        """
        try:
            if self.disabled:
                return 'Role creation disabled'

            url = f'{self.kibana_host}/api/security/role/{role_name}'
            # Set the body
            body = {
                'elasticsearch': {
                    'cluster': ['transport_client'],
                    'indices': [
                        {
                            'names': [index],
                            'privileges': ['read', 'write', 'read_cross_cluster', 'view_index_metadata', 'index']
                        }
                    ]
                },
                'kibana': [{
                    'feature': {
                        'dashboard': ['read'],
                        'discover': ['read']
                    },
                    'spaces': [role_name],
                }],
                'metadata': {
                    'version': 1
                }
            }
            body = json.dumps(body)

            response = requests.head(url=url, headers=self.kibana_headers, verify=self.verify, timeout=self.timeout)

            if response.status_code == 200:
                return f'Role \'{role_name}\' already exists'
            else:
                response = requests.put(url=url, data=body, headers=self.kibana_headers, verify=self.verify, timeout=self.timeout)
                if response.status_code == 204:
                    return f'Role {role_name} created'
                else:
                    raise ConnectionError(f'Could not create role {role_name} with status code: {response.status_code}. Response: {response.text}')
        except:
            message = "Could not create role, since this is not strictly necessary to write logs, continue without it"
            print(message)
            return message

    def get_indices(self) -> dict:
        """
        Get all the indices in the elasticsearch instance
        :return: A dictionary with all the indices
        """
        if self.disabled:
            return {}

        indices = requests.get(url=f'{self.elasticsearch_host}/_cat/indices?format=json', headers=self.elastic_headers, verify=self.verify, timeout=self.timeout).json()
        return indices

    def create_user(self, user_name: str, password: str, user_description: str, roles: list) -> str:
        """
        Creates a user if it doesn't exist.
        :param user_name: The username. Most often the username which also is used for the mysql database user (sc_customer)
        :param password: Choose a safe password. At least 8 characters long
        :param user_description: A readable description. Often the customer name
        :param roles: Give the roles to which the user belongs in a list. Most often the same role_name as the user_name
        :return: The response of the request to elasticsearch
        """
        if self.disabled:
            return 'User creation disabled'

        url = f'{self.elasticsearch_host}/_security/user/{user_name}'
        body = {
            'password': f'{password}',
            'roles': roles,
            'full_name': f'{user_description}'
        }
        body = json.dumps(body)

        response = requests.head(url=url, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout)

        if response.status_code == 200:
            return f'user {user_name} already exists'
        else:
            response = requests.put(url=url, data=body, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout)
            if response.status_code == 200:
                return f'user {user_name}, with password: {password} has been created'
            else:
                raise ConnectionError(f'Could not create user {user_name} with status code: {response.status_code}. Response: {response.text}')

    def post_document(self, index_name: str, document: dict) -> requests.Response:
        """
        Posts a document to the specified index. Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-index_.html
        :param index_name: The name of the index to which the document should be posted
        :param document: The document to be posted
        :return: The response of the request to elasticsearch
        """
        if self.disabled:
            return None

        url = f'{self.elasticsearch_host}/{index_name}_rollover/_doc/'
        body = json.dumps(document)
        response = requests.post(url=url, data=body, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout)
        return response

    def get_document(self, index_name: str, document_id: str) -> requests.Response:
        """
        Gets a document from the specified index. Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-get.html
        :param index_name: The name of the index from which the document should be retrieved
        :param document_id: The id of the document to be retrieved
        :return: The response of the request to elasticsearch
        """
        if self.disabled:
            return None

        url = f'{self.elasticsearch_host}/{index_name}/_doc/{document_id}'
        response = requests.get(url=url, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout)
        return response

    def delete_document(self, index_name: str, document_id: str) -> requests.Response:
        """
        Deletes a document from the specified index. Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-delete.html
        :param index_name: The name of the index from which the document should be deleted
        :param document_id: The id of the document to be deleted
        :return: The response of the request to elasticsearch
        """
        if self.disabled:
            return None

        url = f'{self.elasticsearch_host}/{index_name}/_doc/{document_id}'
        response = requests.delete(url=url, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout)
        return response

    def task_execution_log(self, information: dict) -> requests.Response:
        """
        Write a document to the elasticsearch database
        :param information: the information to be inserted into the database.
        :return: the response of the post request
        """
        if self.disabled:
            return None

        # Add new document
        url = f'{self.elasticsearch_host}/task_execution_log_{self.client_user}_rollover/_doc/'
        body = json.dumps(information)
        response = requests.post(url=url, data=body, headers=self.elastic_headers, verify=self.verify, timeout=self.timeout)
        return response

    @staticmethod
    def generate_password(length=20):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
