import grpc
from pryvx import pryvx_pb2
from pryvx import pryvx_pb2_grpc
import pickle
from concurrent import futures
import os
import shutil

# Directory to store received models
MODEL_SAVE_PATH = "received_models/"

def prepare_model_folder():
    # Delete the folder if it exists
    if os.path.exists(MODEL_SAVE_PATH):
        shutil.rmtree(MODEL_SAVE_PATH)
    # Create a new folder
    os.makedirs(MODEL_SAVE_PATH, exist_ok=True)


class ModelServicer(pryvx_pb2_grpc.ModelServiceServicer):
    def __init__(self):
        self.client_models = {}  # Store models from clients

    def SendModelParams(self, request, context):
        try:
            # Extract metadata (client ID)
            client_id = dict(context.invocation_metadata()).get("client_id", "unknown_client")
            
            # Deserialize model received from client
            model = pickle.loads(request.params)

            # Assign a unique client ID
            client_id = f"client_{len(self.client_models) + 1}"
            self.client_models[client_id] = model
            
            # Save model to disk
            model_filename = os.path.join(MODEL_SAVE_PATH, f"{client_id}_model.pkl")
            with open(model_filename, "wb") as f:
                
                pickle.dump(model, f)

            print(f"✅ Received and saved model from {client_id}")

            return pryvx_pb2.ModelResponse(message=f"Model from {client_id} received and saved.")
        except Exception as e:
            print(f"❌ Error processing model: {e}")
            return pryvx_pb2.ModelResponse(message="Failed to process model")


def start_server():
    prepare_model_folder()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pryvx_pb2_grpc.add_ModelServiceServicer_to_server(ModelServicer(), server)
    
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started. Listening on localhost:50051")

    server.wait_for_termination()

