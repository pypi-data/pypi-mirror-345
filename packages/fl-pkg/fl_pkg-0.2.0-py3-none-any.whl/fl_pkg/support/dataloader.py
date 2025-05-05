import csv
import numpy as np
import re
import os

# Valid dataset configuration schemas:
enum_schema = {'name': '', 'description': '', 'isTarget': True, 'type': 'Class', 'enum': ['', '']}
multi_enum_schema = {'name': '', 'description': '', 'isTarget': True, 'type': 'Multiclass', 'enum': ['', '']}
num_schema = {'name': '', 'description': '', 'isTarget': False, 'type': 'Number', 'min': 0, 'max': 0}

def _has_valid_schema(dictionary: dict) -> bool:
    # Check if the dictionary matches either enum_schema, multi_enum_schema or num_schema
    for schema in [enum_schema, multi_enum_schema, num_schema]:
        if all(key in dictionary.keys() for key in schema.keys()):
            for key in schema.keys():
                # Check type field must be Class, Multiclass or Number
                if key == "type" and dictionary[key] not in [enum_schema["type"], multi_enum_schema["type"], num_schema["type"]]:
                    raise ValueError(f"Invalid type for key {key}")
                # Check data type
                if type(dictionary[key]) != type(schema[key]):
                    raise ValueError(f"Invalid type in key {key}")
            return True
        
    raise ValueError("Invalid configuration schema. Check keys in the dictionary.")

def _convert_dataset_configuration(dataset_configuration: list[dict], for_trainer: bool = True)-> tuple[list, dict]:
    
    # create a list with name,isTarget,type,value for each feature and save the row index for each configuration.
    # Example: config_list: [('gender', 'weight', 'height'), (True, False, False), ('Class', 'Number', 'Number'), (['M', 'F'], [0, 300], [0, 300])]
    #          row_index: {"name":0, "isTarget":1, "type":2, "value":3}
    row_index = {"name":0, "isTarget":1, "type":2, "value":3}
    config_list = []
    for feature in dataset_configuration:
        if for_trainer or not feature["isTarget"]: 
            if feature["type"]=="Class":
                config_list.append([feature["name"], feature["isTarget"], feature["type"], feature["enum"]])
            elif feature["type"]=="Multiclass":
                for i_enum in feature["enum"]:
                    feature_name = feature["name"]
                    config_list.append([f"{feature_name}__{i_enum}", feature["isTarget"], feature["type"], feature["enum"]])
            else:
                config_list.append([feature["name"], feature["isTarget"], feature["type"], [feature["min"], feature["max"]]])
            
    return list(zip(*config_list)), row_index

def validate_configuration(dataset_configuration: list[dict], for_trainer: bool = True) -> tuple[list, dict]:
    """
    Validates the configuration for each feature in the dataset and returns the processed configuration and row index information.

    Args:
        dataset_configuration (List[dict]): A list of dictionaries representing the configuration for each feature in the dataset.
        for_trainer (bool, optional): A flag indicating whether the configuration is being used for prediction (True) or training (False). Default value is True.

    Returns:
        Tuple[list, dict]: A tuple containing the processed configuration (`config_list`) and row index information (`row_index`).
    """
        
    all(_has_valid_schema(feature) for feature in dataset_configuration)
    
    config_list, row_index = _convert_dataset_configuration(dataset_configuration, for_trainer)
    
    # Check if there are any target features: no check if validation is for prediction step
    if for_trainer:   
        if not any(config_list[row_index["isTarget"]]):
            raise ValueError("No target features found in the configuration. Exiting...")
    
    # Check if there are any feature
    if False not in config_list[row_index["isTarget"]]:
        raise ValueError("No feature found in the configuration. Exiting...")
    
    return config_list, row_index
    
def _read_csv_file(csv_file_path: str, delimiter=None) -> np.ndarray:
    if not delimiter:
        # Open the file and read the first few lines to detect the delimiter
        with open(csv_file_path, 'r') as file:
            first_line = [next(file) for _ in range(1)]  # Read the header line
            semicolon_detected = ';' in first_line[0]
            delimiter = ';' if semicolon_detected else ','

    # Read the CSV file with the detected delimiter
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file, delimiter=delimiter)
        data = []
        for row in reader:
            data.append(row)

    return np.array(data)

def _check_Class(feature_array: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, dict]:

    invalid_values = []
    invalid_indices = []
    encoding_map = {item: ind for ind, item in enumerate(values)}
    decoding_map = {ind: item for ind, item in enumerate(values)}
    for index, element in enumerate(feature_array):
        if index > 0 and element not in values:
            invalid_values.append(element)
            invalid_indices.append(index + 1)
        elif index >0 and element in values:
            feature_array[index] = encoding_map[element]

    if invalid_values:
        raise ValueError(f"Invalid values: {invalid_values} in {feature_array[0]} column at rows: {invalid_indices}. {feature_array[0]} must contain string values in {values}.")

    return feature_array, decoding_map

def _check_Multiclass(feature_array: np.ndarray):  
    valid_values = set({"0", "1"})
    invalid_values = list(set(feature_array[1:].flatten()) - valid_values)
    is_not_binary = len(invalid_values) != 0
    
    if is_not_binary:
        raise ValueError(f"Invalid values: {invalid_values} in {feature_array[0]} column. {feature_array[0]} must contain only 0 or 1.")

def _check_Number(feature_array: np.ndarray, range: np.ndarray) -> np.ndarray:

    invalid_values = []
    invalid_indices = []
    
    for i, value in enumerate(feature_array):
        if i > 0:
            # Check comma separator and convert to float in-place
            parts = re.split(r'\D', value)
            if len(parts) > 2:
                value = value.replace(',', '.')
            
            try:
                feature_array[i] = float(value)
            except Exception:
                invalid_values.append(feature_array[i])
                invalid_indices.append(i+1)
                continue

            # Check range
            invalid_range = np.logical_or(feature_array[i] < range[0], feature_array[i] > range[1])
            if invalid_range:
                invalid_values.append(feature_array[i])
                invalid_indices.append(i+1)
  
    if len(invalid_indices) > 0:
        error_message = f"Invalid values: {invalid_values} in {feature_array[0]} column at rows: {invalid_indices}. {feature_array[0]} must contain numeric values in {range}."
        raise ValueError(error_message)

    return feature_array
        
def validate_dataset(dataset_configuration: list[dict], dataset: np.ndarray, for_trainer: bool = True) -> tuple[np.ndarray, list, str, list]:
    """
    Validates the provided dataset against the given configuration.

    Args:
        dataset_configuration (list[dict]): The dataset configuration specifying feature names, types, and values.
        dataset (np.ndarray): The dataset to be validated.
        for_trainer (bool, optional): A flag indicating whether the configuration is being used for prediction (True) or training (False). Default value is True.

    Returns:
        Tuple[np.ndarray, list, str]: A tuple containing the validated dataset with encoded string features (`validated_dataset`), a list of indices corresponding to the target labels in the validated dataset (`label_index`) and the type of problem, either "classification" or "regression" (`problem_type`).

    Raises:
        ValueError: If the dataset configuration is invalid or the dataset contains invalid values.
    """

    # Validate dataset configuration
    config_list, row_index = validate_configuration(dataset_configuration, for_trainer)
    
    # Convert the dtype of the array to object
    dataset = dataset.astype(object)

    # Check feature presence in the local dataset
    missing_features = set(config_list[row_index["name"]]) - set(dataset[0])
    if missing_features:
        raise ValueError(f"Missing features: {missing_features} in the local dataset. Exiting ...")

    # Cache feature type information
    feature_types = {feature: config_list[row_index["type"]][i] for i, feature in enumerate(config_list[row_index["name"]])}

    # Vectorized feature validation
    msg = []
    decoding_list = [{} for _ in range(dataset.shape[1])]
    for i in range(dataset.shape[1]):
            feature_array = dataset[:, i]
            feature_name = dataset[0, i]

            if feature_name in config_list[row_index["name"]]:
                column_index = config_list[row_index["name"]].index(feature_name)
                feature_type = feature_types[feature_name]

                if feature_type == "Class":
                    try:
                        validated_feature, decoding_map = _check_Class(feature_array, config_list[row_index["value"]][column_index], )
                        dataset[:, i] = validated_feature
                        decoding_list[i] = decoding_map
                    except ValueError as e:
                        msg.append(str(e))
                        continue
                elif feature_type == "Number":
                    try: 
                        dataset[:, i] = _check_Number(feature_array, config_list[row_index["value"]][column_index])
                    except ValueError as e:
                        msg.append(str(e))
                        continue
                elif feature_type == "Multiclass":
                    try:
                        _check_Multiclass(feature_array)
                    except ValueError as e:
                        msg.append(str(e))
                        continue
    if msg:
        raise ValueError("\n".join(msg))

    # Efficient feature removal using Boolean mask
    keep_mask = np.array([feature_name in config_list[row_index["name"]] for feature_name in dataset[0]])
    validated_dataset = dataset[:, keep_mask]
    decoding_list = [decoding_list[element] for i, element in enumerate(np.where(keep_mask)[0].tolist())]
     
    # Find indeces of target features
    target_label_index_from_config = [i for i, item in enumerate(config_list[row_index["isTarget"]]) if item == True]
    target_labels_name = [name for i, name in enumerate(config_list[row_index["name"]]) if i in target_label_index_from_config]
    # target_label_index_from_config != target_label_index_from_df
    target_label_index_from_df = [i for i, col_name in enumerate(validated_dataset[0,:]) if col_name in target_labels_name]

    print(f"target_label_index_from_df: {target_label_index_from_df}")

    
    # Find type of problem
    all_target_type = np.array(config_list[row_index["type"]])[target_label_index_from_config]
    if all(element == "Class" for element in all_target_type):
        problem_type = "classification"
    elif all(element == "Number" for element in all_target_type):
        problem_type = "regression"
    else:
        problem_type = "mixed"
    
    return validated_dataset, target_label_index_from_df, problem_type, decoding_list

def validate_dataset_from_csv(dataset_configuration: list[dict], csv_file_path: str, delimiter = None, for_trainer: bool = True) -> tuple[np.ndarray, list, str, list]:
        
    dataset = _read_csv_file(csv_file_path, delimiter)
    dataset, label_index, problem_type, decoding_list = validate_dataset(dataset_configuration, dataset, for_trainer)
    
    return dataset, label_index, problem_type, decoding_list

def check_img_folder(folder_path):
    if not os.path.exists(folder_path):
                raise FileExistsError(f"There is no folder named:{folder_path}")
    elif not len(os.listdir(folder_path)):
        raise FileExistsError(f"Empty directory {folder_path}")

    for filename in os.listdir(folder_path): # Better using Pillow
        image_extensions = (".jpeg", ".jpg", ".png", ".bmp", ".gif", ".db")
        if not filename.lower().endswith(image_extensions):
            raise ValueError(f"Find a file with incorrect extension: {filename}")
    

def validate_image_data(dataset_configuration: list[dict], image_folder_path: str, for_trainer: bool = True):
    
    if for_trainer:
        # Check classes:
        classes = []
        if len(dataset_configuration)>1:
                raise ValueError("Error in data classes in configuration file: there is more than one feature")    
        classes = dataset_configuration[0]["enum"]
            
        # Check folder classes:    
        for i_class in classes:
            class_path = os.path.join(image_folder_path, i_class)
            check_img_folder(class_path)
    else:
       check_img_folder(image_folder_path) 
    
    return image_folder_path    