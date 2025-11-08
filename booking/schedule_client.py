import grpc
import schedule_pb2
import schedule_pb2_grpc

def get_schedule_client():
    # Le serveur Schedule écoute sur 3202 (comme dans schedule.py)
    channel = grpc.insecure_channel("localhost:3202")
    return schedule_pb2_grpc.ScheduleStub(channel)
