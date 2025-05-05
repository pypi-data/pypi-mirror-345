from .utils import *
# import argparse
import json
import os
from .dataloader import validate_dataset_from_csv, validate_image_data


# input for testing:
# parser = argparse.ArgumentParser()
# parser.add_argument("-c", "--config", required=True, type=str)
# parser.add_argument("-ds", "--data", required=True, type=str)
# args = parser.parse_args()

# logger.info(f"config is: {args.config}")

def read_data(path_config, path_data): 
    '''
    -path_config is the path to the config file
    -path_data is the path to the data file
    
    returns the final config, which contains a key with x_train, y_train, x_test, y_test'''

    if path_config.endswith('.json'):
        with open(path_config) as config_data:
            config = json.load(config_data)
        config = setup(config)
    else: 
        logger.debug("Warning: config provided as dict. Continue without checking ...")
        json_parser = json.JSONDecoder()
        config = json_parser.decode(path_config)
        config = setup(config) 

    # Validate input data depending on input data type:
    if config["projects"]["modelConfiguration"]["name"] == "CNN":
        if(os.path.isdir(path_data)):
            validate_image_data(config['projects']['datasetConfiguration'], path_data)
            config["datasetLoader_res"] = {"image_path": path_data}
            data_final = run_federation_image(config)
        else:
            logger.error("Please, provide images folder path")   
    else:    
        if path_data.endswith('.csv'):
            validated_dataset, label_index, problem_type, decoding_list = validate_dataset_from_csv(config['projects']['datasetConfiguration'], path_data)
            validated_dataset = np.array(validated_dataset[1:])

            logger.debug(f"\n problem_type: {problem_type} \n label_index: {label_index}")
            print(f"validate_dataset: {validated_dataset}")
        else: 
            logger.debug("Warning: data provided as list. Continue without checking ...")
            json_parser = json.JSONDecoder()
            data = json_parser.decode(path_data)
            validated_dataset = np.array(data["validated_dataset"][1:])
            label_index = data["label_index"]
            problem_type = data["problem_type"]
        
        # Prepare and set up the data for further processing
        data_final = run_federation(config, validated_dataset, label_index, problem_type)

    return data_final

# res = read_data(args.config, args.data)

# print(f"res is : {res}")