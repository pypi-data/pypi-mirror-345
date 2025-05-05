import event_service_pb2_grpc
from event_service_pb2 import EventRequest, EventResponse
import datetime

from collections.abc import Iterator

import time
import threading

class EventsManager(event_service_pb2_grpc.EventServiceServicer):
    def __init__(self):
        self.connected_clients: dict = {}
        self.events = []
        self.events_lock = threading.Lock()

    def GetEventStream(self, request: EventRequest, context) -> Iterator[EventResponse]:
        print("get event stream started")
        client_id = request.client_id
        print(f"Client {client_id} connected.")

        self.add_client(client_id)
        
        last_event_index = 0

        while context.is_active():
            # Check if there are new events (no lock needed for read-only access)
            if last_event_index < len(self.events):
                for event in self.events[last_event_index:]:
                    yield EventResponse(time=event["time"], message=event["message"])
                last_event_index = len(self.events)  # Update the last event index

            time.sleep(1)  # Poll for new events every second

        print(f"Client {client_id} disconnected.")
        self.remove_client(client_id)
        

    
    def add_event(self, message):
        event_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with self.events_lock:
            self.events.append({"time": event_time, "message": message})

    def add_client(self, client_id: str):
        print(f"Adding client: {client_id}")
        event_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.add_event(f"Client {client_id} connected.")
        self.connected_clients[client_id] = event_time
    
    def remove_client(self, client_id: str):
        print(f"removing client: {client_id}")
        self.add_event(f"Client {client_id} disconnected.")  # Add disconnection event
        self.connected_clients.__delitem__(client_id)

    def get_connected_clients(self):
        return self.connected_clients


