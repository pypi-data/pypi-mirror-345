import torch
import numpy as np
from pyarrow import fs
import io

class IdenticalProductsPairModel(torch.nn.Module):
    def __init__(self, input_dim: int):
        super(IdenticalProductsPairModel, self).__init__()
        self.linear = torch.nn.Sequential(
            torch.nn.Linear(input_dim, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 1),
        )
        
    def forward(self, x):
        x = self.linear(x)
        x = torch.sigmoid(x)
        return x
    
def load_model(model_path: str) -> IdenticalProductsPairModel:
    model_state_dict = load_model_state_from_hdfs(model_path)
    model = IdenticalProductsPairModel(1923)
    model.load_state_dict(model_state_dict)
    model.eval()
    return model
    
def load_model_state_from_hdfs(model_path: str):
    filesystem = fs.HadoopFileSystem(host="default")
    with filesystem.open_input_file(model_path) as f:
        model_bytes = f.read()
    model_state_dict = torch.load(io.BytesIO(model_bytes))
    return model_state_dict

def preprocess_features(product_a, product_b):
    """
     preprocess_features must be a symetric function: f(a, b) = f(b, a)
    """
    if product_a["partner_id"] < product_b["partner_id"] and product_a["hashed_external_id"] <= product_b["hashed_external_id"]:
        product_1, product_2 = product_a, product_b
    else:
        product_1, product_2 = product_b, product_a
    x1 = np.array(product_1["text_embedding"])
    x2 = np.array(product_2["text_embedding"])
    diff_squared = (x1 - x2) ** 2
    diff_squared_sum = diff_squared.sum()
    same_cols = []
    for col_name in ["category_id", "brand_id"]:
        if product_1[col_name] == product_2[col_name]:
            same_cols.append(1)
        else:
            same_cols.append(0)
    res = np.concatenate([x1, x2, diff_squared, [diff_squared_sum], same_cols])
    return res

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
