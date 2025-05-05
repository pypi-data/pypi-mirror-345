import grpc
import time 
import threading
import federation_pb2_grpc
import event_service_pb2_grpc
from event_service_pb2 import EventRequest

class ClientHandler:
    def __init__(self, model, stub):
        self.token = "testToken"
        self.model = model
        self.stub = stub

    def fitting(self, data_train_eval):

        client_message = self.model.fit(data_train_eval, {})
        # print(f"weights params : {client_message}")

        # 3. Send the weights (which resulted from the fitting) to the server. Get as result aggregated weights.
        request_iterator = iter([client_message])
        responses = self.stub.Join(request_iterator)
        return responses

    def evaluating(self, aggregated_weights, data):

        # Setting Parameters 
        self.model.set_model_params(params=aggregated_weights)

        # Calculating Accuracy
        client_message = self.model.evaluate_model_params(data=data, config={})
        # print(f"calculated accuracy: {client_message}")

        # 5. Send the accuracy to the server. Does it perform some aggregation?
        request_iterator = iter([client_message])
        responses = self.stub.Join(request_iterator)
        return responses

    def handle_responses(self, responses): # The return value depends on the type of action! 
                                           # If is a fitting ... return aggregated weights
                                           # If is an evaluation ... return accuracy
        for response in responses: 
            field = response.WhichOneof("msg")
            print(f"field: {field}")

            if field == 'finished':  # Finished the n_rounds training! 
                return "finished"
            elif field == 'fit_ins':
                aggregated_weights = response.fit_ins.parameters
                # aggregated_weights_converted = parameters_to_ndarrays(aggregated_weights)
                # print(f"Result received: {aggregated_weights_converted}")

                return aggregated_weights
            elif field == 'evaluate_ins':
                aggregated_accuracy = response.evaluate_ins  # This has some sub-keys ...
                # print(f"Result received: {aggregated_accuracy}")

                return aggregated_accuracy
            else:
                print(f"some error occured... As response from server was expecting the weights aggregated, but some other operations were performed, or some errors occurred.")
        return



def client_run(server_address: str,
                client_id: str, 
                conf_res, 
                data_train_eval, 
                token_interceptor,
                model_class):
    

    channel = grpc.intercept_channel(grpc.insecure_channel(server_address), token_interceptor)

    stub = federation_pb2_grpc.FederationStub(channel)
    stub_events_servicer = event_service_pb2_grpc.EventServiceStub(channel)

    # 3. Send the weights (which resulted from the fitting) to the server. Get as result aggregated weights.
    model = model_class(conf_res)
    model.set_initial_params()

    client_handler = ClientHandler(model=model, stub=stub)

    # Starting a Parallel Thread... 
    def infinite_loop_func():
        print('Thread-t1:Start the loop')
        event_request = EventRequest(client_id=client_id)
        print(f"event_request: {event_request}")
        responses = stub_events_servicer.GetEventStream(event_request)
        print(f"event stream sent?")
        for response in responses:
            print(f"Time={response.time}, Message={response.message}")

    t1 = threading.Thread(target = infinite_loop_func, args=(), daemon=True) # daemon = True, fa sì che se stoppiamo il thread principale, allora si 
                                                                                    # stoppa anche lui! Prova a fare Ctrl + C ---> si stoppa...
    t1.start()  

    it = 0
    while True:
        # supposed training here
        # ins = {"server_round": it+1}

        responses = client_handler.fitting(data_train_eval)
        responses_server = client_handler.handle_responses(responses=responses)
        if responses_server == "finished":  # o altri errori messaggi da gestire poi
            print(f"FINISHED!!!")
            break
        else: #It means are aggregated weights
            aggregated_weights = responses_server
            # print(f"aggregated_weights: {aggregated_weights}")

        # supposed evaluation here
        responses = client_handler.evaluating(aggregated_weights=aggregated_weights, data = data_train_eval) # set new parameters && evaluates
        responses_server = client_handler.handle_responses(responses=responses)
        if responses_server == "finished":  # o altri errori messaggi da gestire poi
            print(f"FINISHED!!!")
            break
        else: #It means is accuracy
            aggregated_accuracy = responses_server
            # print(f"aggregated_accuracy: {aggregated_accuracy}")
        it+=1

        print(f"next_iteration...")
        time.sleep(1)

    print(f"finished ... with iterations: {it}")
    print(f"FINISSSSHHEEDD")