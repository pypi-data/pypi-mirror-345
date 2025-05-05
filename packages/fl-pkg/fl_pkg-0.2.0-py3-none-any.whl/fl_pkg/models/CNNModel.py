import numpy as np
from tensorflow import Tensor
import keras
from keras.models import Model
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, GlobalAveragePooling2D, Rescaling, Flatten
from keras.optimizers import get as get_optim
from keras.losses import get as get_loss
from typing import Dict, Any

import os
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
        self.test_size = configurations["projects"]["test_size"]
        self.type = configurations["projects"]["modelConfiguration"]["type"]
        self.lossFunction = configurations["projects"]["modelConfiguration"]["lossFunction"]
        self.optimizer = configurations["projects"]["modelConfiguration"]["optimizer"]
        self.learning_rate = configurations["projects"]["modelConfiguration"]["learning_rate"]
        self.class_labels =  configurations["projects"]["datasetConfiguration"][0]["enum"]
        # number of convolutional layers
        # (for now, we decide the number of filters)
        self.image_size = [
            configurations["projects"]["modelConfiguration"]["resolutionWidth"],
            configurations["projects"]["modelConfiguration"]["resolutionHeight"]
        ]
        
        self.image_path = configurations["datasetLoader_res"]["image_path"] if "datasetLoader_res" in configurations else None
        self.color_mode = configurations["projects"]["modelConfiguration"]["colorMode"]
        if self.color_mode == "grayscale":
            self.color_channel = 1
        elif self.color_mode == "rgb":
            self.color_channel = 3
        else:
            self.color_channel = 4
        self.conv_filters = configurations["projects"]["modelConfiguration"]["filters"]
        self.dense_neurons = list(
            configurations["projects"]["modelConfiguration"]["hidden_layers"]
        )
        self.dropout = configurations["projects"]["modelConfiguration"]["dropout"]

        n_classes = len(configurations["projects"]["datasetConfiguration"][0]["enum"])
        
        # Initialize model object
        self.conv_layers, self.dense_layers = [], []
        dropout = self.dropout > 0

        # conv blocks
        for filters in self.conv_filters:
            self.conv_layers += [
                Conv2D(filters, kernel_size=(3, 3), activation="relu"),
                MaxPooling2D(pool_size=(2, 2))
            ]
                
        # Add GlobalAveragePooling2D layer
        self.conv_layers.append(Flatten()) #GlobalAveragePooling2D
        
        # Add Dropout
        if dropout:
            self.conv_layers.append(Dropout(self.dropout))

        # dense layers
        for neurons in self.dense_neurons:
            self.dense_layers.append(
                Dense(neurons, activation="relu")
            )

        if self.type == "regression":
            self.out = Dense(1, "relu")
        else:
            if n_classes == 2:
                self.out = Dense(1, activation=None)
            else:
                self.out = Dense(n_classes, activation="softmax")


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
        loss = get_loss({"class_name": self.lossFunction, "config":{}})
        metrics = ["accuracy"] if self.type == "classification" else ["mean_squared_error"]

        self.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        self.build(input_shape=[None, self.image_size[0], self.image_size[1], self.color_channel])
        
        if self.image_path is not None:
            train_ds, val_ds = keras.utils.image_dataset_from_directory(
                self.image_path,
                class_names = self.class_labels,
                validation_split=self.test_size,
                subset="both",
                seed=1,
                image_size=self.image_size,
                color_mode=self.color_mode
            )
            
            self.train_ds = train_ds
            self.val_ds = val_ds
        
        
    def set_model_params(self, params: Parameters):
        parametersConvertedBack = parameters_to_ndarrays(params)
        if(len(parametersConvertedBack)==0):
            print("careful parameters empty or empty list!")
        else:
            self.set_weights(parametersConvertedBack)
        return 
    
    def fit(self, data: Dict, config: Dict):
        super().fit(self.train_ds, **config) 
        # print(f" data: {data}") # {'image_path': '.\\datasets_and_config_files\\CNN\\client2'} 

        resp = ClientMessage(fit_res=ClientMessage.FitRes(parameters=ndarrays_to_parameters(self.get_weights()), num_examples=len(self.train_ds.file_paths)))

        return resp
        

    def evaluate_model_params(self, data: Dict, config: Dict):
        """Evaluates model parameters on a given dataset.
        Solo in CNN data non viene usato, perché abbiamo settato val_ds in set_initial_params di questa classe... E' un caso un po' particolare

        Returns:
            A dictionary of evaluation metrics.
        """

        val_steps = config.get('val_steps', 5)
        loss, accuracy = self.evaluate(self.val_ds, steps=val_steps)
        metrics_name = "accuracy" if self.type == "classification" else "mean_squared_error"

        metrics ={metrics_name: accuracy,
                    "loss": loss}
        
        res = ClientMessage(evaluate_res=ClientMessage.EvaluateRes(loss=accuracy, num_examples=len(self.val_ds.file_paths), metrics={}))

        return res
    
    # def custom_predict(self, x_set, return_label = False, return_proba = False, type = "classification"):
    #     """
    #     Generate predictions for the input data.

    #     Args:
    #         x_set: The input data for which predictions are needed.

    #     Returns:
    #         Predicted class labels.
    #     """
        
    #     image_names=os.listdir(x_set)
    #     all_predictions = []
    #     for i, filename in enumerate(image_names):
    #         img = keras.utils.load_img(os.path.join(x_set, filename), target_size=self.image_size, color_mode=self.color_mode)
                
    #         x=keras.utils.img_to_array(img)
    #         x=np.expand_dims(x, axis=0)
    #         images = np.vstack([x])

    #         predictions = super().predict(images)
               
    #         if return_label:
    #             all_predictions.append([filename, self.class_labels[int(predictions.argmax(axis=-1))]])
    #         else: 
    #             all_predictions.append([filename, float(max(predictions[0]))])
         
    #     return all_predictions# y_pred
    
    # def load_model_params(self, file_path):
        
    #     params = np.load(file_path)
    #     final_params = list(params.values())
    #     self._old_set__model_params(final_params)
                
    #     return
    

    def call(self, inputs: Tensor) -> Tensor:
        """
        Defines the forward pass of the model.

        Args:
            inputs: The input data.

        Returns:
            The model's output.
        """
        
        x = Rescaling(1.0 / 255)(inputs)
        for l in self.conv_layers:
            x = l(x)
        for l in self.dense_layers:
            x = l(x)
        outputs = self.out(x)
        return outputs