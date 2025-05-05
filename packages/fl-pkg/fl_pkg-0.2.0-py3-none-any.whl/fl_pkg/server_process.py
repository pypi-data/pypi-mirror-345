import federation_pb2_grpc
from threading import Condition
from .ServerConcHandler import ServerConcHandler
from .EventsManager import EventsManager
from collections.abc import Iterator
from federation_pb2 import ServerMessage, ClientMessage
import grpc
from grpc import RpcContext
from concurrent import futures
import time 
import threading
import event_service_pb2_grpc
import sys



# I am not sure that all the methods below are implemented correctly... 
class ExtendServicerContext(grpc.ServicerContext):

    def __init__(self, context: grpc.ServicerContext, func_name):
        self._original_context = context
        meta = dict(context.invocation_metadata())
        self.new_value = "he111"  # My new Value!!! 

    def abort(self, code, details):
        return self._original_context.abort(code, details)

    def abort_with_status(self, status):
        return self._original_context.abort_with_status(status)

    def add_callback(self, callback):
        return self._original_context.add_callback(callback)

    def auth_context(self):
        return self._original_context.auth_context()

    def cancel(self):
        return self._original_context.cancel()

    def invocation_metadata(self):
        print(f"calling metadata original")
        return self._original_context.invocation_metadata() # Be careful also how also other methods are implemented 

    def is_active(self):
        return self._original_context.is_active()

    def peer(self):
        return self._original_context.peer()

    def peer_identities(self):
        return self._original_context.peer_identities()

    def peer_identity_key(self):
        return self._original_context.peer_identity_key()

    def send_initial_metadata(self, initial_metadata):
        return self._original_context.send_initial_metadata(initial_metadata)

    def set_code(self,code):
        return self._original_context.set_code(code)

    def set_details(self, details):
        return self._original_context.set_details(details)

    def set_trailing_metadata(self, trailing_metadata):
        return self._original_context.abort(trailing_metadata)

    def time_remaining(self):
        return self._original_context.time_remaining()

def require_authorization(func):
    def wrapper(self, request, context):
        value = 3
        return func(self, request, context, value)
    return wrapper

class FederationServicer(federation_pb2_grpc.FederationServicer):
    def __init__(self, server_conc_handler: ServerConcHandler, events_manager: EventsManager):
        self.server_conc_handler = server_conc_handler
        self.events_manager = events_manager

        self.condition = Condition()

    def handle_client_disconnected(self, context, client_id):
        if context.code() == grpc.StatusCode.CANCELLED:
            print(f"Stopping execution of This Thread, because client {client_id} has disconnected prematurely")
            self.events_manager.remove_client(client_id)
        # self.server_conc_handler.fit_res_list.__delitem__(client_id) # Remove From Fit Res List the relative weights!!! 
        # sys.exit(0) # Stopping Execution

    # @require_authorization
    def fitting_server(self, request: ClientMessage, context):
        # print(f"fitting called....")
        client_id = dict(context.invocation_metadata()).get('client_id')
        # print(f"until here re fit worked")
        # new_data = context.new_value
        # print(f"FIT client_id: {client_id}, new_data: {new_data}")
        
        self.server_conc_handler.fit_res_list[client_id] = request.fit_res

        context.add_callback(lambda: self.handle_client_disconnected(context=context, client_id=client_id))

        len_connected_cl = len(self.events_manager.get_connected_clients())
        min_nr_cl = self.server_conc_handler.nr_clients
        len_fit_res = len(self.server_conc_handler.fit_res_list)
        print(f"len conn cl: {len_connected_cl}; min_nr_cl: {min_nr_cl}; len_fit_res: {len_fit_res}")

        #### WAITING FOR CONNECTION 
        if (len_connected_cl < min_nr_cl) or (len_fit_res != min_nr_cl):
            print(f"Received first parameters")
            self.condition.wait()   # So every 2 seconds goes in timeout (if not unblocked by a thread in notify all)  
        else: 
            print(f"received other params... Starting FITTING...")
            self.condition.notify_all()

        ### AGGREGATION 
        self.server_conc_handler.handling_aggregation(server_round=self.server_conc_handler.actual_round + 1)
        aggregated_params = self.server_conc_handler.aggregated_params

        return ServerMessage(fit_ins=ServerMessage.FitIns(parameters=aggregated_params))

    def evaluating_server(self, request: ClientMessage, context):
        self.server_conc_handler.accuracies[context.peer()] = request.evaluate_res

        len_connected_cl = len(self.events_manager.get_connected_clients())
        min_nr_cl = self.server_conc_handler.nr_clients
        nr_acc = len(self.server_conc_handler.accuracies)
        
        print(f"len_con_cl: {len_connected_cl} and min_nr_cl: {min_nr_cl} and nr_acc: {nr_acc}")

        if (nr_acc < min_nr_cl) or (len_connected_cl < min_nr_cl):
            print(f"Received first accuracies")
            self.condition.wait()
        else: 
            print(f"received other accuracies... AVG evaluation...")
            self.condition.notify_all()


        self.server_conc_handler.handle_evaluation()
        aggregated_accuracy = self.server_conc_handler.aggregated_accuracy

        return ServerMessage(evaluate_ins=ServerMessage.EvaluateIns(parameters=None, config={"avg_loss": aggregated_accuracy}) )

    @require_authorization
    def Join(self, request_iterator: Iterator[ClientMessage], context, value) -> Iterator[ServerMessage]:

        print(f"!!!!!My New Value is : {value}")

        # Or taking the token from here
        # metadata = dict(context.invocation_metadata())
        # token = metadata.get('token')
        # print(f"token sent is token: {token}")

        for request in request_iterator:
            field = request.WhichOneof("msg")

            with self.condition:
                if self.server_conc_handler.actual_round == self.server_conc_handler.nr_rounds:
                    print(f"Federation Finished!")
                    print(f"History Of Accuracies: {self.server_conc_handler.history_accuracies}")
                    ## Codice per far salvare // self.server_conc_handler.history_accuracies
                    yield ServerMessage(finished=ServerMessage.Finished(finished = True))
                else:
                    if field == "fit_res":
                        yield self.fitting_server(request=request, context=context)
                    elif field == "evaluate_res":
                        yield self.evaluating_server(request=request, context=context)





def server_run(server_address, nr_clients: int, nr_rounds: int, max_thread_parallel: int, token_interceptor, server_agg):
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_thread_parallel), interceptors=(token_interceptor,))
    server_conc_handler = ServerConcHandler(nr_clients=nr_clients, nr_rounds=nr_rounds, server_agg=server_agg) # note that only he has the nr_clients and the FederationServicer does not require it anymore! 
    events_manager = EventsManager()

    # Instantiating first Service
    federation_pb2_grpc.add_FederationServicer_to_server(FederationServicer(server_conc_handler=server_conc_handler, 
                                                                            events_manager=events_manager), server)

    # Instantiating second Service: 
    event_service_pb2_grpc.add_EventServiceServicer_to_server(servicer=events_manager, server=server)
    
    ########## THREAD THAT SEES THE CONNECTED CLIENTS
    def infinite_loop_func(my_event):
        while not my_event.is_set():
            responses = events_manager.get_connected_clients()
            print(f"list connected clients: {responses}")
            time.sleep(2)

    my_event = threading.Event()
    t1 = threading.Thread(target = infinite_loop_func, args=(my_event,), daemon=True) # daemon = True, fa sì che se stoppiamo il thread principale, allora si 
                                                                                    # stoppa anche lui! Prova a fare Ctrl + C ---> si stoppa...
    t1.start()  



    # Starting
    server.add_insecure_port(server_address) 
    server.start()
    print(f"Server started on {server_address}")
    server.wait_for_termination()