from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
import numpy as np
from sklearn.metrics import accuracy_score
from typing import Dict, Any

from fl_pkg.support.parameter import *
from fl_pkg.federation_pb2 import ClientMessage

class MyCustomModel(LogisticRegression):
    
    def __init__(self, configurations):
        """
        Initializes the model instance and extracts relevant configurations.

        Args:
            configurations: A dictionary containing model and dataset configurations.
        """
        
        self.configurations = configurations
        self.dataset_configuration = configurations["projects"]["datasetConfiguration"]
        new_dict = {key: value for key, value in configurations["projects"]["modelConfiguration"].items() if key not in ["name", "type"]}
        if configurations["projects"]["modelConfiguration"]["penalty"] == "elasticnet":
            new_dict["l1_ratio"] = 0.5
        elif configurations["projects"]["modelConfiguration"]["penalty"] == "None":
            print(f"THIS IS THE CASE")
            new_dict["penalty"] = "none"
            new_dict["l1_ratio"] = 0
        else:
            new_dict.pop("l1_ratio", None)

        # Get Number Of Classes! 
        get_attribute_with_classes = [i for i in configurations['projects']['datasetConfiguration'] if i['isTarget'] == True and i['enum']]
        self.num_class = len(get_attribute_with_classes[0]['enum']) # Number Of Category!!
        print(f"---NUM class: {self.num_class}")

        if new_dict['fit_intercept'] == False:
            print(f" --- Fit Intercept is False!!!")
            self.intercept_ = 0
       
        super().__init__(solver = "saga", warm_start = True, **new_dict)


    def set_initial_params(self):
        """Sets initial parameters as zeros Required since model params are
        uninitialized until model.fit is called.

        But server asks for initial parameters from clients at launch. Refer
        to sklearn.linear_model.LogisticRegression documentation for more
        information.
        
        Args:
            None
        """

        x_col = []
        for column in self.dataset_configuration:
            if column["isTarget"] == True:
                y_col = column
            else:
                x_col.append(column["name"])

        unique_classes = y_col["enum"]

        num_columns = len(x_col)

        n_classes = len(unique_classes)
        n_features = num_columns
        self.classes_ = np.array([i for i in range(n_classes)])

        self.coef_ = np.zeros((n_classes, n_features))
        if self.fit_intercept:
            self.intercept_ = np.zeros((n_classes,))
    
        
    def fit(self, data, config: Dict) -> Parameters:

        X, y = data['x_train'], data['y_train']

        super().fit(X, y, **config) 

        if self.fit_intercept:
            params = [
                self.coef_,
                self.intercept_,
            ]
        else:
            params = [
                self.coef_,
            ]
            print("params: " + str(params))

        paramsConverted = ndarrays_to_parameters(params)

        resp = ClientMessage(fit_res=ClientMessage.FitRes(parameters=paramsConverted, num_examples=len(y)))

        return resp

    def evaluate_model_params(self, data, config: Dict):
        '''parameters such that first entry are the coeffs. The second entry is the coefficient of bias'''

        X_test, y_test = data['x_test'], data['y_test']

        # Predict using the updated model
        y_pred_test = self.predict_proba(X_test)

        loss = log_loss(y_test, y_pred_test, labels=[i for i in range(self.num_class)])
        score = self.score(X_test, y_test)   # This is the accuracy! 

        print(f"score: accuracy: {score}")
        
        res = ClientMessage(evaluate_res=ClientMessage.EvaluateRes(loss=loss, num_examples=len(y_test), metrics={}))

        return res
    
    def set_model_params(self, params: Parameters):
        """
        """
        weights = parameters_to_ndarrays(parameters=params)

        self.coef_ = weights[0]
        if self.fit_intercept:
            self.intercept_ = weights[1]
        return self
    
    ##### METHODS BELOW ONLY FOR PREDICTION AND PLOTTING 



    def load_model_params(self, file_path):
        params = np.load(file_path)
        final_params = list(params.values())

        self.coef_ = final_params[0]

        print(f"fit_ intercept: {self.fit_intercept}")
        if self.fit_intercept:
            self.intercept_ = final_params[1]
            
        return self


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
                        
                # predict values             
                y_pred_encoded = super().predict(x_set)

                # decode features
                if y_pred_encoded.ndim == 1:
                    y_pred_encoded = y_pred_encoded.reshape((len(y_pred_encoded),1))
                
                y_pred = []              
                for i in range(0, y_pred_encoded.shape[1]):             
                    y_decoded = y_pred_encoded[:, i].tolist()
                    if len(decoding_list) > 0 and decoding_list[i] != {}:
                        for ind, item in enumerate(y_pred_encoded[:, i]):
                            y_decoded[ind] = decoding_list[i][item]
                    y_pred.append(y_decoded)
                y_pred = np.column_stack(tuple(y_pred))
                if y_pred.shape[1] == 1:
                    y_pred = y_pred.ravel()

            elif type == "regression":
                y_pred = super().predict(x_set)  
        else:
            if return_proba == False:
                y_pred = super().predict_proba(x_set).argmax(axis=1)
            else:
                y_pred = super().predict_proba(x_set)
            
        return y_pred
