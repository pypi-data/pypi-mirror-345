


from ..support.parameter import *
from ..federation_pb2 import Scalar

# from fl_pkg.support.parameter import *
# from fl_pkg.federation_pb2 import Scalar

import numpy as np
from functools import reduce


class ServerAgg:
    def __init__(self):
        self.some_parameters = 4


    def aggregate(self, results: list[tuple[NDArrays, int]]) -> NDArrays:
        """Compute weighted average."""
        # Calculate the total number of examples used during training
        num_examples_total = sum(num_examples for (_, num_examples) in results)

        # Create a list of weights, each multiplied by the related number of examples
        weighted_weights = [
            [layer * num_examples for layer in weights] for weights, num_examples in results
        ]

        # Compute average weights of each layer
        weights_prime: NDArrays = [
            reduce(np.add, layer_updates) / num_examples_total
            for layer_updates in zip(*weighted_weights)
        ]
        return weights_prime
    
    def aggregate_weights(self, fit_res_list, server_round):
        '''Return aggregated parameters NOT converted to ndarrays'''

        list_weights_with_samp = [(parameters_to_ndarrays(fit_res.parameters), fit_res.num_examples) for fit_res in fit_res_list]
        aggregated_weights = self.aggregate(list_weights_with_samp)

        self.save_params(aggregated_weights, server_round)

        return ndarrays_to_parameters(aggregated_weights)

    def aggregate_accuracies(self, accuracies):
        '''return aggregated accuracy NOT converted'''
        tot_samples = sum([i.num_examples for i in accuracies])
        losse_w_s = sum([i.loss*i.num_examples for i in accuracies])
        res = losse_w_s/tot_samples
        print(f"res------- {res}")

        scalar_value1 = Scalar()
        scalar_value1.float = res
        return scalar_value1
    
    def save_params(self, params, server_round): # params as nd arrays
        print(f"Saving round {server_round} aggregated_ndarrays...")
        np.savez(f"round-{server_round}-weights.npz", *params)