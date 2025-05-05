import numpy as np
import json
import xgboost as xgb
from logging import INFO
from typing import Tuple, Union, Dict 

XY = Tuple[np.ndarray, np.ndarray]
Dataset = Tuple[XY, XY]
ModelParams = Union[XY, Tuple[np.ndarray]]

import os 
import sys 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Solo per runnare questo script isolato 

from fl_pkg.support.parameter import *
from fl_pkg.federation_pb2 import ClientMessage



num_local_round = 1

# REGRESSION
hyper_params_regression = {
    "objective": "reg:squarederror",  # reg:linear --> reg:squaredderror
    "eta": 0.1,
    "max_depth": 8,
    "eval_metric": "rmse"
}

# CLASSIFICATION
hyper_params_classification = {
    "objective": "binary:logistic",    # binary classification with logistic regression 
    "eta": 0.1,  # Learning rate
    "max_depth": 8,
    "eval_metric": "auc",
    "nthread": 16,
    "num_parallel_tree": 1,
    "subsample": 1,
    "tree_method": "hist",
}

class MyCustomModel:
    
    def __init__(self, configurations):
        """
        Initializes the model instance and extracts relevant configurations.

        Args:
            configurations: A dictionary containing model and dataset configurations.
        """
        
        self.configurations = configurations
        self.dataset_configuration = configurations["projects"]["datasetConfiguration"]
        # new_dict = {key: value for key, value in configurations["projects"]["modelConfiguration"].items() if key not in ["name", "type"]}
        # if configurations["projects"]["modelConfiguration"]["penalty"] == "elasticnet":
        #     new_dict["l1_ratio"] = 0.5
        self.local_model_bytes = []

        regressionOrClassification = configurations["projects"]["modelConfiguration"]["type"]
        self.type_problem = regressionOrClassification

        objective = configurations["projects"]["modelConfiguration"]["objective"]
        alpha = configurations["projects"]["modelConfiguration"]["alpha"]
        gamma = configurations["projects"]["modelConfiguration"]["gamma"]
        max_depth = configurations["projects"]["modelConfiguration"]["max_depth"]
        eta = configurations["projects"]["modelConfiguration"]["learning_rate"]

        if regressionOrClassification == "regression":
            self.hyper_params = {
                "objective": objective, 
                "eta": eta,
                "max_depth": max_depth,
                "gamma": gamma,
                "alpha": alpha,
                "eval_metric": "rmse"
            }
        elif regressionOrClassification == "classification":

            # Get Number Of Classes! 
            get_attribute_with_classes = [i for i in configurations['projects']['datasetConfiguration'] if i['isTarget'] == True and i['enum']]
            num_class = len(get_attribute_with_classes[0]['enum']) # Number Of Category!!

            if num_class >= 3 and objective == "binary:logistic":  # We have to change the objective, otherwise error if binary:logistic, because it expects only 2 categories
                objective = "multi:softprob"

            self.hyper_params = {
                "objective": objective,
                "num_class": num_class,
                "eta": eta,
                "max_depth": max_depth,
                "gamma": gamma,
                "alpha": alpha,
                "eval_metric": "auc",
                "nthread": 16,
                "num_parallel_tree": 1,
                "subsample": 1,
                "tree_method": "hist",
            }
            
            if num_class <= 2 and objective == "binary:logistic":
                del self.hyper_params['num_class']  # Se il numero di classi è 2 e abbiamo binary logistic, la doc. dice che non bisogna specificare num_class, o passarlo = 1.
                                                    # Altrimenti dà errore, come ho sperimentato. 
            
        print(f"problem type: {regressionOrClassification} and self.hyper_params: {self.hyper_params}")

        self.num_local_round = num_local_round

        self.xgb_model = xgb.Booster(params=self.hyper_params)

        print(f"hyper_params: {self.hyper_params}")
       
  
    def set_initial_params(self):       
        '''Metodo che viene sempre chiamato, per tutti i miei MyCustomModel '''
        self.local_model_bytes = []


    def set_model_params(self, params: Parameters):
        # Setting the local bytes
        self.local_model_bytes = params.tensors

        # loading the model 
        global_model = None
        for item in params.tensors:  # In realtà è sempre solo un tensore... Attento a far in modo che sia così nell'aggregation
            global_model = bytearray(item)
        if (global_model != None):
            self.xgb_model.load_model(global_model)

        return 
    
    
    def _local_boost(self, bst_input, data):  # bst_input è il modelo con 1. i parametri/hyper parametri 2. i pesi del modello 
        # Update trees based on local training data.

        x_train, y_train = data['x_train'], data['y_train']

        train_dmatrix = xgb.DMatrix(x_train, label=y_train)

        for i in range(self.num_local_round):
            bst_input.update(train_dmatrix, bst_input.num_boosted_rounds())  # il modelo viene fine tunato sul train_dmatrix

        # Bagging: extract the last N=num_local_round trees for sever aggregation
        bst = bst_input[
            bst_input.num_boosted_rounds()
            - self.num_local_round : bst_input.num_boosted_rounds()
        ]

        return bst
    
    def fit(self, data: any, config: Dict):
        
        x_train, y_train, x_test, y_test = data['x_train'], data['y_train'], data['x_test'], data['y_test']

        train_dmatrix = xgb.DMatrix(x_train, label=y_train)
        test_dmatrix = xgb.DMatrix(x_test, label=y_test)


        if len(self.local_model_bytes) == 0: # It means is the first round
            # First round local training
            bst = xgb.train(
                self.hyper_params,
                train_dmatrix,
                num_boost_round=self.num_local_round,
                evals=[(test_dmatrix, "validate"), (train_dmatrix, "train")],   
            )
            local_model = bst.save_raw("json")  # diventa praticamente un dizionario json stringa. 

            # saving model in local model bytes and in xgb_model
            self.local_model_bytes = [bytes(local_model)]
            self.xgb_model = bst 

        else:  # round >= 2    
            bst = self._local_boost(self.xgb_model, data)
            local_model = bst.save_raw("json")  # diventa praticamente un dizionario json stringa. 
            self.local_model_bytes = [bytes(local_model)]
        
        params = Parameters(tensor_type="", tensors=self.local_model_bytes)

        resp = ClientMessage(fit_res=ClientMessage.FitRes(parameters=params, num_examples=len(y_train)))

        return resp
    
    
    def evaluate_model_params(self, data: any, config: Dict):
        """
        Evaluates the model parameters on the provided dataset.

        Calculates different metrics based on the model type:
        - For classification: log_loss and accuracy.
        - For regression: log_loss and mean_squared_error.

        Args:
            x_set: The input data.
            y_set: The target data.

        Returns:
            A dictionary of evaluation metrics.
        """

        x_test, y_test = data['x_test'], data['y_test']
        test_dmatrix = xgb.DMatrix(x_test, label=y_test)
        
        # Run evaluation
        eval_results = self.xgb_model.eval_set(
            evals=[(test_dmatrix, "valid")],
            iteration=self.xgb_model.num_boosted_rounds() - 1,
        )

        print(f"eval_results: {eval_results}, and type: {type(eval_results)}")
        eval_error = round(float(eval_results.split("\t")[1].split(":")[1]), 4)

        print(f"AUC or MSE = {eval_error**2}")
        if self.type_problem == "regression": 
            metrics_result = {
                "accuracy": eval_error**2,
                "mse": eval_error**2
            }
        elif self.type_problem == "classification":
            metrics_result = {
                "accuracy": eval_error,
                "auc": eval_error
            }
        print(f"dict_result: {metrics_result}")

        res = ClientMessage(evaluate_res=ClientMessage.EvaluateRes(loss=eval_error, num_examples=len(y_test), metrics={}))
        return res



## HERE BELOW IS FOT PREDICT AND PLOTTING 


    def custom_predict(self, x_set, return_label = False, return_proba = False, type = "classification"):
        """
        Generate predictions for the input data.

        Args:
            x_set: The input data for which predictions are needed.

        Returns:
            Predicted class labels.
        """

        if return_label:
            if type == "classification":
                # find decoding map
                decoding_list = []
                for feature in self.dataset_configuration:
                    if feature.get("isTarget", False) and feature.get("enum", None):
                        decoding_map = {ind: item for ind, item in enumerate(feature["enum"])}
                        decoding_list.append(decoding_map)
                        
                print(f"decoding_list: {decoding_list}")
                # predict values          
                data_np = np.array(x_set)
                data_dmatrix = xgb.DMatrix(data_np)
                y_pred_encoded = self.xgb_model.predict(data_dmatrix)

                # print(f"y_pred_encoded size: {y_pred_encoded.size}, and y_pred_encoded dimensionality is dim 1?: {y_pred_encoded.ndim == 1}")

                if y_pred_encoded.ndim == 1:
                    list_classes_encoded = (y_pred_encoded >= 0.5).astype(int)
                    print(f"dim_encod = 1 -> y_pred_encoded: {y_pred_encoded[:24]}, and y_pred_labels: {list_classes_encoded[:24]}")
                    y_pred = np.array([[i for i in decoding_list if i][0][cls] for cls in list_classes_encoded])
                    print(f"y_pred: {y_pred[:24]}")
                
                elif y_pred_encoded.ndim == 2:
                # decode features
                    list_classes_encoded =  np.argmax(y_pred_encoded, axis=1)
                    y_pred = np.array([[i for i in decoding_list if i][0][cls] for cls in list_classes_encoded])
                    # print(f" dim of y_pred_encoded = 2 ---> list_classes_encoded: {list_classes_encoded} ")

            elif type == "regression":
                data_np = np.array(x_set)
                data_dmatrix = xgb.DMatrix(data_np)
                y_pred = self.xgb_model.predict(data_dmatrix)   
        else: 
            # if return_proba == False:
            #     y_pred = super().predict(x_set).argmax(axis=1)
            # else:
            #     y_pred = super().predict(x_set)
            
            data_np = np.array(x_set)
            data_dmatrix = xgb.DMatrix(data_np)
            y_pred = self.xgb_model.predict(data_dmatrix)   

            if return_proba == False and type == "classification":
                y_pred = np.argmax(y_pred, axis=1)  # Ma ha senso per la regressione? Se return_label = False && return_proba = False??
                                                    # Da controllare FCNN 
            
        return y_pred
        

    def load_model_params(self, file_path):
        
        try:
            ## 2. get with other weights.
            ## 2.1 READING PSEUDO JSON 
            with open(file_path, 'r') as file:
                json_data = file.read()
            params = json.loads(json_data)

            ## 2.2 SAVING TO JSON 
            python_dict = json.loads(params)
            output_json = "global_model.json"
            with open(output_json, 'w') as json_file:
                json.dump(python_dict, json_file, indent=4)
        except Exception as e:
            print(f"An error has occured: {e}")

        self.xgb_model.load_model(output_json)

        return

