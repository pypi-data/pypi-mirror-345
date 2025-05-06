import torch
import json
import os
from . import database as db
from .database import MahalanobisDistance

METRIC = MahalanobisDistance


class MahalanobisDistanceSeq:
    def __init__(self, embeddings_type: str = "decoder", parameters_path: str = None, model_id: str = "llama-3",
                 normalize: bool = False, device: str = "mps", version: int = 1):
        self.embeddings_type = embeddings_type
        self.parameters_path = parameters_path
        self.normalize = normalize
        self.device = torch.device(device)  # Explicitly specify device
        self.centroid = None
        self.sigma_inv = None
        self.min = 1e100
        self.max = -1e100
        self.is_fitted = False
        self.level = "sequence"
        self.ue_bounds_tensor = None
        self.model_id = model_id
        self.version = version

        if self.parameters_path is not None:
            self.load_parameters()

    def load_parameters(self):
        if os.path.exists(self.parameters_path):
            try:
                md_database = db.TensorSqliteDatabase(self.parameters_path)

                # load tensor data
                # Ensure all parameters are loaded to the same device
                self.centroid = md_database.load_tensor(METRIC, self.model_id, "centroid", self.version).to(self.device)
                self.sigma_inv = md_database.load_tensor(METRIC, self.model_id, "sigma_inv", self.version).to(self.device)
                self.min = md_database.load_tensor(METRIC, self.model_id, "min", self.version).to(self.device)
                self.max = md_database.load_tensor(METRIC, self.model_id, "max", self.version).to(self.device)

                try:
                    ue_bounds = md_database.load_json(METRIC, self.model_id, "ue_bounds", self.version)
                    # Pre-compute tensor for bounds
                    if ue_bounds and str(self) in ue_bounds:
                        self.ue_bounds_tensor = torch.tensor(
                            ue_bounds[str(self)],
                            dtype=torch.float32
                        ).to(self.device)
                except Exception as e:
                    print(f"Error loading bounds data: {e}")

                self.is_fitted = True
            except Exception as e:
                print(f"Error loading parameters: {e}")

    def __call__(self, embeddings):
        try:
            # Ensure input data is on the correct device
            if not torch.is_tensor(embeddings):
                embeddings = torch.tensor(embeddings, dtype=torch.float32, device=self.device)

            if not self.is_fitted:
                self.centroid = embeddings.mean(axis=0)
                # Ensure computations are on the same device
                embeddings_T = embeddings.T.to(self.device)
                cov_matrix = torch.cov(embeddings_T)
                self.sigma_inv = torch.inverse(cov_matrix).float().to(self.device)
                self.is_fitted = True

            # Perform all computations on the specified device
            diff = embeddings.unsqueeze(1) - self.centroid.unsqueeze(0)
            dists = torch.sqrt(torch.einsum("bcd,da,bsa->bcs",
                                            diff.float(),
                                            self.sigma_inv.float(),
                                            diff.float()))
            dists = torch.stack([torch.diag(dist) for dist in dists], dim=0)[:, 0]

            if self.normalize:
                dists = torch.clip((self.max - dists) / (self.max - self.min), min=0, max=1)

            return dists

        except Exception as e:
            print(f"Error in distance calculation: {e}")
            return None

    def normalize_ue(self, val: torch.Tensor, device: str = "mps") -> torch.Tensor:
        """Normalize uncertainty values"""
        # Ensure input value is on the correct device
        val_tensor = val if isinstance(val, torch.Tensor) else torch.tensor(val, dtype=torch.float32)
        val_tensor = val_tensor.to(device)

        if torch.isnan(val_tensor):
            return torch.tensor(1.0).to(device)

        if self.ue_bounds_tensor is None:
            print(
                f"Warning: Could not find normalizing bounds for estimator: {str(self)}. Will not normalize values.")
            return val_tensor

        return (self.ue_bounds_tensor < val_tensor).float().mean()

    def __str__(self):
        return f"MahalanobisDistanceSeq_{self.embeddings_type}"