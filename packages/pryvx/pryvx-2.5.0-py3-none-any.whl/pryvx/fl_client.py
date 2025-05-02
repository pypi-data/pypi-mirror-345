import grpc
from pryvx import pryvx_pb2
from pryvx import pryvx_pb2_grpc
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import pickle


def train_logistic_classifier(features, labels):
    model = LogisticRegression()
    model.fit(features, labels)
    serialized_model = pickle.dumps(model)
    return serialized_model, model


def train_random_forest_classifier(features, labels):
    print("Model training started...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(features, labels)
    serialized_model = pickle.dumps(model)
    print("Model training finished.")
    return serialized_model, model


def send_params(serialized_model, connection_url, client_id):

    with grpc.insecure_channel(connection_url) as channel:
        stub = pryvx_pb2_grpc.ModelServiceStub(channel)

        # Attach metadata (client ID) in the request
        metadata = (("client_id", client_id),)

        model_params = pryvx_pb2.ModelParams(params=serialized_model)

        response = stub.SendModelParams(model_params, metadata=metadata)

        print(f"✅ Model Params sent to server from {client_id}")

        return f"✅ Model Params sent to server from {client_id}"

