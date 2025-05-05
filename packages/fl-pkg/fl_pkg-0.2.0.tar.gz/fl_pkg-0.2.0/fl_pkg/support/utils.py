import requests
import json
import tkinter as tk
from tkinter import filedialog
import logging
import numpy as np
from .dataloader import validate_dataset_from_csv
from .api_caller import *

#############################################################################################################################
# DEFINE UTILS FUNCTIONS AND CLASS:

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------------------------------------------------------

def setup(data):
    """Parses JSON data and ensures the presence of backend_url, project_id, path and env.
        If configuration values are missing, it retrieves them by getting the token and updates the JSON data.
    """
    # Parse the input JSON data
    # data_dict = json.loads(json_data)

    # Get the '_id' from 'projects' or raise an error if it's missing
    backend_url = data.get('config', {}).get("backendURL")
    if backend_url is None:
        raise KeyError("Missing 'backendURL' in the JSON data.")

    # Get the '_id' from 'projects' or raise an error if it's missing
    project_id = data.get('projects', {}).get("_id")
    if project_id is None:
        raise KeyError("Missing '_id' in the 'projects' section of the JSON data.")
    
    # Get the 'path' from 'projects' or raise an error if it's missing
    # path = data.get('projects', {}).get('path')
    # if path is None:
    #     raise KeyError("Missing 'path' in the 'projects' section of the JSON data.")

    # Get the 'env' from the 'config' dictionary or raise an error if it's missing
    # env = data.get('config', {}).get("env")
    # if env is None:
    #     raise KeyError("Missing 'env' in the JSON data.")


    # Build the URL using 'backend_url' and 'project_id'
    url = f"{backend_url}/projects/{project_id}"

    try:
        # Try to retrieve a token using a 'get_token' function
        token = get_token(data)
        
    except Exception as e:
        raise SystemExit(f"Error: {e}")

        
    # If 'federationConfiguration', 'datasetConfiguration', 'modelConfiguration' keys are present in 'projects', return dictionary data
    if not all(key in data['projects'] for key in ["federationConfiguration", "datasetConfiguration", "modelConfiguration", "deployment"]):

        # Set headers with the obtained token for the request
        headers = {
            'x-auth-token': token
        }

        # Make a GET request to the specified URL
        response = requests.get(url,headers=headers)

        # If the request is successful (status code 200), update the 'data'
        if response.status_code == 200:
            response_dict = json.loads(response.text)
            for key in response_dict:
                data["projects"][key] = response_dict[key]
        
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise SystemExit(f"Error")

        # try:
        #     # update 'userAuth' with UserID
        #     userID = get_user(data)
        #     data["userAuth"]['userID'] = userID
        # except Exception as e:
        #     raise SystemExit(f"Error: {e}")
    return data

def login(email, password, host, backend_url):
    """Performs user authentication by sending a request to 'backend_url' with 'email' and 'password'
        If successful, the response contains an authentication token, which is returned.
    """

    response = signin(backend_url, email, password, host)
    token = response

    return token

def get_token(data):
    """Retrieves an authentication token. It checks if a token
        is present in the JSON data, and if not, it obtaines one by
        calling the login function. The obtained token is returned.
    """

    # Parse the input JSON data
    # data_dict = json.loads(json_data)
    # Declare 'token' as a global variable
    global token
    

    if "token" in data['userAuth']:
        # If 'token' is present in the 'userAuth' section of the data, assign it to the global 'token' variable
        token = data['userAuth']['token']

    else:
        if all(key in data['userAuth'] for key in ["email", "password", "host"]):
            # If 'email', 'password', and 'host' keys are present in 'userAuth', attempt to obtain a token
            email = data['userAuth']['email']
            password = data['userAuth']['password']
            host = data['userAuth']['host']
            backend_url = data['config']['backendURL']

            try:
                # Attempt to obtain a token by calling the 'login' function
                token = login(email, password, host, backend_url)

            except Exception as e:
                raise Exception(f"Login failed: {e}")
        else:
            raise Exception("Input data must contain 'token' or 'email', 'password', and 'host'.")
            
    return token

def get_user(data):
    """Performs pairing with the backend, retrieve the user ID
    """
   
    response = pairing(data['config']['backendURL'], data['projects']['_id'], token)
    userID = response['user']
    return userID

def split_data(data: np.ndarray, target_list: list, problem_type: str, test_size: float = 0.2, num_class: int = 1) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Splits the provided dataset into training and testing sets, selecting the target labels from a specified list.

    Args:
        data: A NumPy array containing the dataset, where rows represent data points and columns represent features followed by target labels.
        target_list: A list of target label indeces to be extracted from the dataset.
        problem_type: The type of machine learning problem, either "classification" or "regression".
        test_size: A float value between 0.0 and 1.0 specifying the proportion of the data to be used for testing.

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: A tuple containing the training features, training labels, testing features, and testing labels.
        - x_train (np.ndarray): The training features, represented as a NumPy array.
        - y_train (np.ndarray): The training labels, represented as a NumPy array.
        - x_test (np.ndarray): The testing features, represented as a NumPy array.
        - y_test (np.ndarray): The testing labels, represented as a NumPy array.

    Raises:
        ValueError: if the `test_size` is not between 0.0 and 1.0.
    """

    # Check if `test_size` is between 0.0 and 1.0
    if not (0.0 <= test_size <= 1.0):
        raise ValueError("`test_size` must be a float value between 0.0 and 1.0.")
  
    if problem_type == "regression":
        print(f"--- utils data shuffling -- regression")
        # Shuffle the data randomly
        np.random.shuffle(data)

        # Extract target labels based on `target_list`
        features = np.delete(data, target_list, axis=1)
        labels = data[:, target_list]

        # print(f"SPLIT: labels: {labels}, and target_list: {target_list}, and data: {data}, and features: {features}")

        # Split features and labels into training and testing sets
        split_index = int(len(data) * test_size)
        x_test = features[:split_index]
        y_test = labels[:split_index]        
        x_train = features[split_index:]
        y_train = labels[split_index:]
    elif problem_type == "classification":
        y_classes = [i for i in range(num_class)]

        print(f"--- utils data shuffling -- classification")

        count_shuffle = 0
        appear_at_least_once = False
        max_nr_repetitions = num_class*10
        print(f"max_nr_repetitions: {max_nr_repetitions}")

        while ((not appear_at_least_once) and (count_shuffle <= max_nr_repetitions)):
            # Shuffle the data randomly
            count_shuffle += 1

            np.random.shuffle(data)

            features = np.delete(data, target_list, axis=1)
            labels = data[:, target_list]

            split_index = int(len(data) * test_size)
            x_test = features[:split_index]
            y_test = labels[:split_index]        
            x_train = features[split_index:]
            y_train = labels[split_index:]

            appear_at_least_once_train = np.isin(y_classes, y_train).all()
            appear_at_least_once_test = np.isin(y_classes, y_test).all()

            appear_at_least_once = appear_at_least_once_train and appear_at_least_once_test
            print(f"count_shuffle: {count_shuffle}")
            print(f"appear_at_least_once: {appear_at_least_once_train}, and {appear_at_least_once_test} --> {appear_at_least_once}")
        
        if count_shuffle > max_nr_repetitions:
            print(f"Exceeded maximumm number!")
            raise Exception("Dataset is too small for enough eterogeneous testing!")

    # if dim < 1 cast to array:  
    if len(target_list) < 2:
        y_test = y_test.ravel()
        y_train = y_train.ravel()
    
    # Change type from object to int or float depending of the type
    if problem_type == "classification":
        y_test = y_test.astype('int')
        y_train = y_train.astype('int')
    elif problem_type == "regression":
        y_test = y_test.astype('float')
        y_train = y_train.astype('float')

    return x_train, y_train, x_test, y_test

def run_federation(data, validated_dataset, target_list, problem_type):
    """ Prints model info and x_train, y_train, x_test, y_test shape and calls class DatasetLoader. Returns x_train, y_train, x_test, y_test in output
    """
    # Logging information about the project and dataset
    logging.info("----------------------------------------")
    logging.info("Model details for project %s:", data['projects']['_id'])
    logging.info(f"Model: {data['projects']['modelConfiguration']}")
    logging.info(f"Federation: {data['projects']['federationConfiguration']}")
    logging.info("----------------------------------------")
    logging.info("Check if the dataset is compliant with project specifications...")

    # Load and process the dataset, then log data shapes
    #csv_file_path = data['projects']['path']
    if problem_type == "classification":
        # Get Number Of Classes! 
        get_attribute_with_classes = [i for i in data['projects']['datasetConfiguration'] if i['isTarget'] == True and i['enum']]
        num_class = len(get_attribute_with_classes[0]['enum']) # Number Of Category!!
        x_train, y_train, x_test, y_test = split_data(validated_dataset, target_list, problem_type, test_size = data['projects']['test_size'], num_class = num_class)
    elif problem_type == "regression":
        x_train, y_train, x_test, y_test = split_data(validated_dataset, target_list, problem_type, test_size = data['projects']['test_size'])
    
    # FCNN cannot convert numpy array to tensor, so convert data to list
    if data['projects']['modelConfiguration']['name'] == "FCNN":
        data["datasetLoader_res"] = {"x_train":x_train.tolist(), "y_train":y_train.tolist(), "x_test":x_test.tolist(), "y_test":y_test.tolist()}
    else:   
        data["datasetLoader_res"] = {"x_train":x_train, "y_train":y_train, "x_test":x_test, "y_test":y_test}
    
    # Log data shapes
    logging.info("Train data shape: %s", x_train.shape)
    logging.info("Test data shape: %s", x_test.shape)
    logging.info("Train target shape: %s", y_train.shape)
    logging.info("Test target shape: %s", y_test.shape)

    logging.info("----------------------------------------")
    logging.info("Request connection to server...")
    # try:
    #     # update 'userAuth' with UserID
    #     userID = get_user(data)
    #     data["userAuth"]['userID'] = userID
    # except Exception as e:
    #     raise SystemExit(f"Error: {e}")
    # logging.info("----------------------------------------")
    # logging.info("Run federation...")

    return data

def run_federation_image(config_data):
    logging.info("Request connection to server...")
    # config_data["userAuth"]['userID'] = "fake so it works"
    # try:
    #     # update 'userAuth' with UserID
    #     userID = get_user(config_data)
    #     config_data["userAuth"]['userID'] = userID
    # except Exception as e:
    #     raise SystemExit(f"Error: {e}")
    # logging.info("----------------------------------------")
    # logging.info("Run federation...")
    return config_data

def file_chooser():
    """Opens a file dialog box and returns the path to the selected file."""
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', True)
    file_path = filedialog.askopenfilename()
    root.destroy()
    return file_path