

# from fl_pkg.support.parameter import *
# from fl_pkg.federation_pb2 import Scalar


from ..support.parameter import *
from ..federation_pb2 import Scalar

from typing import Optional, cast
import json

class ServerAgg:
    def __init__(self):
        self.some_parameters = 4

    def _get_tree_nums(self, xgb_model_org: bytes) -> tuple[int, int]:
        xgb_model = json.loads(bytearray(xgb_model_org))
        # Get the number of trees
        tree_num = int(
            xgb_model["learner"]["gradient_booster"]["model"]["gbtree_model_param"][
                "num_trees"
            ]
        )
        # Get the number of parallel trees
        paral_tree_num = int(
            xgb_model["learner"]["gradient_booster"]["model"]["gbtree_model_param"][
                "num_parallel_tree"
            ]
        )
        return tree_num, paral_tree_num


    def aggregate(self, 
        bst_prev_org: Optional[bytes],
        bst_curr_org: bytes,
    ) -> bytes:
        """Conduct bagging aggregation for given trees."""
        if not bst_prev_org:
            return bst_curr_org

        # Get the tree numbers
        tree_num_prev, _ = self._get_tree_nums(bst_prev_org)
        _, paral_tree_num_curr = self._get_tree_nums(bst_curr_org)

        bst_prev = json.loads(bytearray(bst_prev_org))
        bst_curr = json.loads(bytearray(bst_curr_org))

        bst_prev["learner"]["gradient_booster"]["model"]["gbtree_model_param"][
            "num_trees"
        ] = str(tree_num_prev + paral_tree_num_curr)
        iteration_indptr = bst_prev["learner"]["gradient_booster"]["model"][
            "iteration_indptr"
        ]
        bst_prev["learner"]["gradient_booster"]["model"]["iteration_indptr"].append(
            iteration_indptr[-1] + paral_tree_num_curr
        )

        # Aggregate new trees
        trees_curr = bst_curr["learner"]["gradient_booster"]["model"]["trees"]
        for tree_count in range(paral_tree_num_curr):
            trees_curr[tree_count]["id"] = tree_num_prev + tree_count
            bst_prev["learner"]["gradient_booster"]["model"]["trees"].append(
                trees_curr[tree_count]
            )
            bst_prev["learner"]["gradient_booster"]["model"]["tree_info"].append(0)

        bst_prev_bytes = bytes(json.dumps(bst_prev), "utf-8")

        return bst_prev_bytes


        
    def aggregate_weights(self, fit_res_list, server_round):
        '''Return aggregated parameters NOT converted to ndarrays'''

        print(f"aggreg w been called")

        # Aggregate all the client trees
        global_model: Optional[bytes] = None

        for fit_res in fit_res_list:
            update = fit_res.parameters.tensors
            for bst in update:
                global_model = self.aggregate(global_model, bst)
            
        # print(f"global-model: {global_model}")

        self.save_params(global_model, server_round)

        return Parameters(tensor_type="", tensors=[cast(bytes, global_model)])


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

        # print(f"params: {params}") it is bytes! 
        params_json = params.decode("utf-8")

        try:
            with open(f"round-{server_round}-weights.json", 'w', encoding='utf-8') as f:
                json.dump(params_json, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"exception e: {e}")
