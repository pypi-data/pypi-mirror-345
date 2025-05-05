
import threading




class ServerConcHandler:
    def __init__(self, nr_clients, nr_rounds, server_agg):
        self.nr_clients = nr_clients
        self.nr_rounds = nr_rounds
        self.server_agg = server_agg

        self.actual_round = 0

        self._lock = threading.RLock()

        # Aggregation Of Weights 
        self.fit_res_list = {}  # Is a dictionary where key is the IP/context.peer() --> Value: Weights 
        self.agg_weig_executed = [False] * self.nr_rounds
        self.aggregated_params = None

        # Aggregation Of Accuracies 
        self.accuracies = {}  # Is a dictionary where key is the IP/context.peer() --> Value: Accuracy 
        self.agg_acc_executed = [False] * self.nr_rounds
        self.aggregated_accuracy = None

        # Keeping history of every round, but maybe better to save in a db... 
        self.global_model_list = [] 
        self.history_accuracies = []


    def handling_aggregation(self, server_round):
        with self._lock: 
            print(f"inside handling agg... len fit res list: {len(self.fit_res_list)}")
            if not self.agg_weig_executed[self.actual_round] and len(self.fit_res_list) == self.nr_clients:


                aggregated_params = self.server_agg.aggregate_weights(list(self.fit_res_list.values()), server_round)  # Because the agg func expects only a LIST of weights, not interested in IP (context.peer), or the key of the dict
                                                                                                # and the server_round!! 
                self.aggregated_params = aggregated_params
                self.global_model_list.append(aggregated_params) 

                # Emptying for the next round...
                self.fit_res_list = {}

                # Executing the Aggregation Of Weights
                self.agg_weig_executed[self.actual_round] = True



    def handle_evaluation(self):
        with self._lock: 
            print(f"EVALUATE -- self.actual_round: {self.actual_round}")
            if (len(self.accuracies) == self.nr_clients) and (not self.agg_acc_executed[self.actual_round]): 
                # The first condition is required because parallel threads 
                # will enter after the first thread has already executed actaul_round +=1
                # Therefore, they go to the flag related to the next round, but
                # they are supposed to analyse the flag of this round 
                # Thus, the first flag resolve this condition. Moreover,
                # also solve when we reach n --> n+1 would be index out of range,
                # but evaluating immediately to false the first condition, does not
                # valuate and throw error in the second condition
                # Executing the Aggregation Of Weights
                self.agg_acc_executed[self.actual_round] = True

                aggregated_accuracy = self.server_agg.aggregate_accuracies(list(self.accuracies.values()))
                self.aggregated_accuracy = aggregated_accuracy
                print(f"Aggregated Accuracy: ---- {self.aggregated_accuracy}")
                self.history_accuracies.append(aggregated_accuracy) 

                # Increasing the round count
                self.actual_round += 1

                # Emptying for the next round...
                self.accuracies = {}

