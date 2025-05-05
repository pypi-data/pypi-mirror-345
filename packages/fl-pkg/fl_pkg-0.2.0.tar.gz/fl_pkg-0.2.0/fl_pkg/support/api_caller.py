import requests
import json
from typing import Any, Dict
import logging 

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MyRequests:

    """A class for making requests to APIs.

    This class provides a simple and convenient interface for making requests to APIs. It handles authentication and SSL verification for you.

    Args:
        api_root: The root URL of the API.
        auth_token: The authentication token for the API (if applicable).

    Attributes:
        api_root: The root URL of the API.
        header: The HTTP headers to send with each request.
        is_SSL_enabled: Whether to verify SSL certificates.
    """

    def __init__(self, api_root: str, auth_token: str = None, content_type: str = None):
        self.api_root = api_root
        self.header = {
            'x-auth-token': auth_token,
            'Content-Type': content_type
        }
        self.is_SSL_enabled = self.api_root.startswith("https://")

    def setAuthToken(self, auth_token):
        # comment
        self.header['x-auth-token'] = auth_token
    
    def setContentType(self, content_type):
        # comment
        self.header['Content-Type'] = content_type

    def request(self, method: str, end_point: str, data=None) -> requests.Response:
        """Performs a request to the specified endpoint.

        Args:
            method: The HTTP method to use.
            end_point: The endpoint to request.
            data: The data to send with the request.

        Returns:
            A `requests.Response` object.
        """

        # Validate the inputs.
        if method not in ['GET', 'POST', 'DELETE']:
            raise ValueError('Invalid HTTP method: {}'.format(method))
        if not end_point:
            raise ValueError('Endpoint cannot be blank.')
        
        # Make the request.
        try:
            return requests.request(method, self.api_root + end_point, data=json.dumps(data), headers=self.header, verify=self.is_SSL_enabled)
        except requests.exceptions.RequestException as e:
            raise ValueError('Error making request: {}'.format(e))

    def get(self, end_point: str) -> requests.Response:
        """Performs a GET request to the specified endpoint.

        Args:
            end_point: The endpoint to request.

        Returns:
            A `requests.Response` object.
        """

        return self.request('GET', end_point)

    def post(self, end_point: str, data) -> requests.Response:
        """Performs a POST request to the specified endpoint.

        Args:
            end_point: The endpoint to request.
            data: The data to send with the request.

        Returns:
            A `requests.Response` object.
        """

        return self.request('POST', end_point, data)

    def delete(self, end_point: str) -> requests.Response:
        """Performs a DELETE request to the specified endpoint.

        Args:
            end_point: The endpoint to request.

        Returns:
            A `requests.Response` object.
        """

        return self.request('DELETE', end_point)


    
def handle_response(response: requests.Response, type: str = "byte") -> Any:
    """Handles the response from the HubSpoke API.

    Args:
        response: The response from the HubSpoke API.
        type: The type of the response content (byte, text, or json).

    Returns:
        The response content, or an error message if the status code is not 200.
    """

    if type not in ['byte', 'text', 'json']:
        raise ValueError('Invalid content type: {}'.format(type))

    status = response.status_code

    # if status is 200 return content, otherwise the text error msg
    if status != 200:
        raise Exception(response.text)
    else:
        try: 
            if type == "byte":
                msg = response.content
            elif type == "text":
                msg = response.text
            else:
                msg = response.json()
            return msg
        except Exception as ex:
            raise ValueError('Error in content handling: {}'.format(ex))

def signin_api(api_root: str, end_point: str, email: str, password: str) -> requests.Response:
    """Signs in an host or guest to HubSpoke remote server.

    Args:
        api_root: The base URL of the API.
        end_point: The endpoint to sign in to.
        email: The user's email address.
        password: The user's password.

    Returns:
        A `requests.Response` object containing the status and message of the request.
    """

    my_requests = MyRequests(api_root)
    my_requests.setContentType('application/json')

    data = {
        "email": email,
        "password": password,
    }

    try: 
        response = my_requests.request("POST", end_point, data)
    except Exception as ex:
        raise ValueError('Error making request: {}'.format(ex))
    return response

def signin(api_root: str, email: str, password: str, host_id: str = None) -> str:
    """Signs in an host or guest to HubSpoke remote server.

    Args:
        api_root: The base URL of the API.
        email: The user's email address.
        password: The user's password.
        host_id: The host's ID (optional).

    Returns:
        A string containing the authentication token for the user.
    """
    logger.info("Logging to HubSpoke")

    if host_id is not None:
        end_point = "/guests/host/" + host_id + "/sign-in"
    else:
        end_point = "/hosts/sign-in"
    
    try:
        response = signin_api(api_root, end_point, email, password)
        token = handle_response(response, "text")
    except Exception as e:
        logger.error("Failed to sign in to HubSpoke: %s", e)
        raise Exception(e)
    
    logger.info("Successfully sign in to HubSpoke")
    return token

def get_hosts_api(api_root: str, email: str) -> requests.Response:
    """Gets a list of hosts for the given user.

    Args:
        api_root: The base URL of the API.
        email: The user's email address.

    Returns:
        A `requests.Response` object containing the status code and response body of the request.
    """

    my_requests = MyRequests(api_root)
    my_requests.setContentType('application/json')

    end_point = "/guests/hosts"

    data = {
        "email": email
    }

    try: 
        response = my_requests.request("POST", end_point, data)
    except Exception as ex:
        raise ValueError('Error making request: {}'.format(ex))
    return response

def get_hosts(api_root: str, email: str) -> Dict:
    """Gets a list of hosts for the given user.

    Args:
        api_root: The base URL of the API.
        email: The user's email address.

    Returns:
        A dictionary containing a list of hosts.
    """

    logger.info("Asking for %s hosts list", email)
    
    try:
        response = get_hosts_api(api_root, email)
        hosts = handle_response(response, "json")
    except Exception as e:
        logger.error("Failed to get hosts list: %s", e)
        raise Exception(e)
    
    logger.info("Successfully get hosts list")
    return hosts

def pairing_api(api_root: str, project_id: str, token: str) -> requests.Response:
    """Initiates a pairing request for the given project.

    Args:
        api_root: The base URL of the API.
        project_id: The project ID.
        token: The authentication token.

    Returns:
        A `requests.Response` object containing the status code and response body of the request.
    """

    my_requests = MyRequests(api_root)
    my_requests.setAuthToken(token)

    end_point = "/pairings/project/" + project_id + "/pair"

    try: 
        response = my_requests.request("POST", end_point)
    except Exception as ex:
        raise ValueError('Error making request: {}'.format(ex))
    return response

def pairing(api_root: str, project_id: str, token: str) -> Dict:
    """Gets a list of hosts for the given user.

    Args:
        api_root: The base URL of the API.
        email: The user's email address.

    Returns:
        A dictionary containing a list of hosts.
    """

    logger.info("Asking for connection with server: project %s ", project_id)
    
    try:
        response = pairing_api(api_root, project_id, token)
        hosts = handle_response(response, "json")
    except Exception as e:
        logger.error("Failed to connect with server: project %s", project_id)
        raise Exception(e)
    
    logger.info("Connection to server established")
    return hosts

def get_projects_api(api_root: str, project_id: str, token: str) -> requests.Response:
    """Gets the project with the given ID.

    Args:
        api_root: The base URL of the API.
        project_id: The project ID.
        token: The authentication token.

    Returns:
        A `requests.Response` object containing the status code and response body of the request.
    """

    my_requests = MyRequests(api_root)
    my_requests.setAuthToken(token)

    end_point = "/projects/" + project_id

    try: 
        response = my_requests.request("GET", end_point)
    except Exception as ex:
        raise ValueError('Error making request: {}'.format(ex))
    return response

def get_projects(api_root: str, project_id: str, token: str) -> Dict:
    """Gets the project with the given ID.

    Args:
        api_root: The base URL of the API.
        project_id: The project ID.
        token: The authentication token.

    Returns:
        A dictionary containing the project information.
    """

    logger.info("Asking for project details: project %s ", project_id)
    
    try:
        response = get_projects_api(api_root, project_id, token)
        project = handle_response(response, "json")
    except Exception as e:
        logger.error("Failed to get project details: project %s", project_id)
        raise Exception(e)
    
    logger.info("Successfully get project details")
    return project

def download_client_api(api_root: str, project_id: str, token: str) -> requests.Response:
    """Gets the project with the given ID.

    Args:
        api_root: The base URL of the API.
        project_id: The project ID.
        token: The authentication token.

    Returns:
        A `requests.Response` object containing the status code and response body of the request.
    """

    my_requests = MyRequests(api_root)
    my_requests.setAuthToken(token)

    end_point = "/projects/" + project_id + "/download-project-scripts"

    try: 
        response = my_requests.request("GET", end_point)
    except Exception as ex:
        raise ValueError('Error making request: {}'.format(ex))
    return response

def download_client(api_root: str, project_id: str, token: str) -> Dict:
    """Gets the project with the given ID.

    Args:
        api_root: The base URL of the API.
        project_id: The project ID.
        token: The authentication token.

    Returns:
        A dictionary containing the project information.
    """

    logger.info("Downloading project %s ", project_id)
    
    try:
        response = download_client_api(api_root, project_id, token)
        code = handle_response(response, "byte")
    except Exception as e:
        logger.error("Failed to download the project %s", project_id)
        raise Exception(e)
    
    logger.info("Download completed")
    return code

###########################################################################################


def download_ca_api(api_root: str, token: str) -> requests.Response:
    """Gets the project with the given ID.

    Args:
        api_root: The base URL of the API.
        project_id: The project ID.
        token: The authentication token.

    Returns:
        A `requests.Response` object containing the status code and response body of the request.
    """

    my_requests = MyRequests(api_root)
    my_requests.setAuthToken(token)

    end_point = "/certificate-authority/download-ca"

    try: 
        response = my_requests.request("GET", end_point)
    except Exception as ex:
        raise ValueError('Error making request: {}'.format(ex))
    return response

def download_ca(api_root: str, token: str) -> str:
    """Gets the global CA for hub&spoke.

    Args:
        api_root: The base URL of the API.
        token: The authentication token.

    Returns:
        A string with the global CA certificate.
    """

    logger.info("Downloading the global CA certificate.")
    
    try:
        response = download_ca_api(api_root, token)
        code = handle_response(response, "text")
    except Exception as e:
        logger.error("Failed to download the CA certificate.")
        raise Exception(e)
    
    logger.info("Download completed")
    return code
