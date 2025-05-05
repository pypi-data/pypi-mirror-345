import numpy as np
from tensorflow import Tensor
from keras.models import Model
from keras.layers import Dense, Dropout
from keras.optimizers import get as get_optim
from keras.losses import get as get_loss
from typing import Dict, Any

import os 
import sys 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Solo per runnare questo script isolato 
from fl_pkg.support.parameter import *
from fl_pkg.federation_pb2 import ClientMessage

ModelParams = Any

"""
A custom Keras model class for classification or regression tasks.

Attributes:
    type: str
        The task type, either "classification" or "regression".
    lossFunction: str
        The name of the loss function to use.
    optimizer: str
        The name of the optimizer to use.
    learning_rate: float
        The learning rate for the optimizer.
"""


class MyCustomModel(Model):
    def __init__(self, configurations: Dict):
        """
        Initializes the model instance and extracts relevant configurations.

        Args:
            configurations: A dictionary containing model and dataset configurations.
        """

        super().__init__()
        # save model configuration
        self.type = configurations["projects"]["modelConfiguration"]["type"]
        self.lossFunction = configurations["projects"]["modelConfiguration"]["lossFunction"]
        self.optimizer = configurations["projects"]["modelConfiguration"]["optimizer"]
        self.learning_rate = configurations["projects"]["modelConfiguration"]["learning_rate"]
        self.hidden_layers = list(
            configurations["projects"]["modelConfiguration"]["hidden_layers"])
        self.dropout = configurations["projects"]["modelConfiguration"]["dropout"]
        self.dataset_configuration = configurations["projects"]["datasetConfiguration"]

        n_classes = None
        # get number of classes if task is classification
        if self.type == "classification":
            x_col = []
            for column in self.dataset_configuration:
                if column["isTarget"] == True:
                    y_col = column
                else:
                    x_col.append(column["name"])
            # Find y unique classes
            unique_classes = y_col["enum"]
            n_classes = len(unique_classes)

        # Initialize model object
        self.dense_layers = []
        dropout = self.dropout > 0

        for neurons in self.hidden_layers:
            self.dense_layers.append(
                Dense(neurons, activation="relu")
            )
            if dropout:
                self.dense_layers.append(
                    Dropout(self.dropout)
                )

        if self.type == "regression":
            self.out = Dense(1, "linear")
        else:
            print(f"n_classes: {n_classes}")
            print(f"self.lossFunction is: {self.lossFunction}")
            if self.lossFunction in ['BinaryCrossentropy', 'BinaryFocalCrossentropy']:  
                # self.out = Dense(1, activation="softmax") # Worked!
                print(f"... Binary!!! ")
                self.out = Dense(1, activation="sigmoid") # Worked better, accuracy was indeed improving!! 
            elif self.lossFunction in ['SparseCategoricalCrossentropy']:
                self.out = Dense(n_classes, activation="softmax")
            else:
                # .... To handle if we add more LossFunctions
                self.out = Dense(n_classes, activation="softmax")

    def call(self, inputs: Tensor) -> Tensor:
        """
        Defines the forward pass of the model.

        Args:
            inputs: The input data.

        Returns:
            The model's output.
        """

        x = self.dense_layers[0](inputs)
        for l in self.dense_layers[1:]:
            x = l(x)
        outputs = self.out(x)
        return outputs

    def set_initial_params(self):
        """
        Sets up the optimizer, loss function, and metrics based on the configurations.
        """
        identifier = {
            "class_name": self.optimizer,
            "config": {
                "learning_rate": self.learning_rate
            }
        }
        optimizer = get_optim(identifier)
        loss = get_loss(self.lossFunction)
        if self.type == "classification":
            metrics = ["accuracy"]
        else:
            metrics = ["mean_squared_error"]

        # input_shape = [None, len([object for object in self.dataset_configuration if not object["isTarget"]])]
        input_shape = (None, len([object for object in self.dataset_configuration if not object["isTarget"]]))
        print(f"INPUT SHAPE: {input_shape}")

        # Actually these 2 lines PERFORMED THE CORRECT BUILD 
        dummy_input = np.zeros((1, input_shape[1]))
        self(dummy_input)  
        
        print(f"Before super building, self.built: {self.built}")
        super().build(input_shape)
        print(f"After super building, self.built: {self.built}")
        self.build(input_shape=input_shape)
        print(f"After building, self.built: {self.built}")

        print(f"Before compile")
        self.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        # See https://stackoverflow.com/questions/78905518/cannot-call-build-method-on-subclassed-tensorflow-model
        # and https://keras.io/guides/making_new_layers_and_models_via_subclassing/#best-practice-deferring-weight-creation-until-the-shape-of-the-inputs-is-known
        # Error here they are not being built these layers: the print say that 
        # self.dense_layers: [<Dense name=dense, built=False>] and its len: 1
        # self.out: <Dense name=dense_1, built=False>
        print(f"self.dense_layers: {self.dense_layers} and its len: {len(self.dense_layers)}")
        print(f"self.out: {self.out}")
        
        print(f"build of set initial parameters been called")

    
    def fit(self, data, config: Dict) -> Parameters:

        X, y = data['x_train'], data['y_train']

        # X is a list (of lists...)
        # y is also a list... 

        # But FCNN expects some np arrays:
        X = np.array(X)
        y = np.array(y)

        super().fit(X, y, **config) 

        resp = ClientMessage(fit_res=ClientMessage.FitRes(parameters=ndarrays_to_parameters(self.get_weights()), num_examples=len(y)))

        return resp
    

    def evaluate_model_params(self, data, config: Dict):
        """Sets new weights and evaluates model parameters on a given dataset.
        """

        X_test, y_test = data['x_test'], data['y_test']

        # X_test and y_test are lists. But FCNN wants np.arrays... Differently from LLR 
        X_test = np.array(X_test)
        y_test = np.array(y_test)

        val_steps = config.get('val_steps', 5)
        loss, metrics = self.evaluate(x=X_test, y=y_test, steps=val_steps)
        
        if self.type == "classification":
            metrics_name = "accuracy"
        else: 
            metrics_name = "mse"

        dict_res = {
                "loss": loss,
                "num_examples": len(X_test),
                "metrics": {
                    metrics_name: metrics,
                    "loss": loss}
                }
        print(f"dict_res: {dict_res}")

        res = ClientMessage(evaluate_res=ClientMessage.EvaluateRes(loss=loss, num_examples=len(y_test), metrics={}))

        return res
    
    def set_model_params(self, params: Parameters):
        """
        """
        weights = parameters_to_ndarrays(parameters=params)
        super().set_weights(weights)
        return 



    # BELOW ONLY FOR PREDICTION AND PLOTTING

    def load_model_params(self, file_path):
        
        params = np.load(file_path)
        final_params = list(params.values())
        self.set_weights(final_params)




    def custom_predict(self, x_set, return_label = False, return_proba = False, type = "classification"):
        """
        Generate predictions for the input data.

        Args:
            x_set: The input data for which predictions are needed.

        Returns:
            Predicted class labels.
        """

        # x_set is always passed as list of lists. But here we need to convert it to np.array:
        x_set = np.array(x_set)
        
        if return_label:
            if type == "classification":
                # find decoding map
                decoding_list = []
                for feature in self.dataset_configuration:
                    if feature.get("isTarget", False) and feature.get("enum", None):
                        decoding_map = {ind: item for ind, item in enumerate(feature["enum"])}
                        decoding_list.append(decoding_map)
                        
                # predict values             
                y_pred_encoded = super().predict(x_set).argmax(axis=1)

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
                y_pred = super().predict(x_set).argmax(axis=1)
            else:
                y_pred = super().predict(x_set)
            
        return y_pred