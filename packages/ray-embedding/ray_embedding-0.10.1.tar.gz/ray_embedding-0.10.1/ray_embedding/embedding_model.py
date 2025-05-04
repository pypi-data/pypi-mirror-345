import logging
import os.path
import time
from typing import Optional, Dict, Any, List

import torch
from fastapi import FastAPI, HTTPException
from ray import serve
from sentence_transformers import SentenceTransformer

from ray_embedding.dto import EmbeddingResponse, EmbeddingRequest

web_api = FastAPI(title=f"Ray Embeddings - OpenAI-compatible API")


@serve.deployment(
    num_replicas="auto",
    ray_actor_options={
        "num_cpus": 1,
        "num_gpus": 0
    },
    autoscaling_config={
        "target_ongoing_requests": 2,
        "min_replicas": 0,
        "initial_replicas": 1,
        "max_replicas": 1,
    }
)
@serve.ingress(web_api)
class EmbeddingModel:
    def __init__(self, model: str, backend: Optional[str] = "torch", matryoshka_dim: Optional[int] = None,
                 trust_remote_code: Optional[bool] = False, model_kwargs: Dict[str, Any] = None):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.backend = backend or "torch"
        self.matryoshka_dim = matryoshka_dim
        self.trust_remote_code = trust_remote_code or False
        self.model_kwargs = model_kwargs or {}
        self.torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger.info(f"Initializing embedding model: {self.model}")
        self.embedding_model = SentenceTransformer(self.model, backend=self.backend, trust_remote_code=self.trust_remote_code,
                                                   model_kwargs=self.model_kwargs)

        self.served_model_name = os.path.basename(self.model)
        self.available_models = [
            {"id": self.served_model_name,
             "object": "model",
             "created": int(time.time()),
             "owned_by": "openai",
             "permission": []}
        ]
        self.logger.info(f"Successfully initialized embedding model {self.model} using device {self.torch_device}")

    @web_api.post("/v1/embeddings", response_model=EmbeddingResponse)
    async def create_embeddings(self, request: EmbeddingRequest):
        """Generate embeddings for the input text using the specified model."""
        try:
            assert request.model == self.served_model_name, (
                f"Model '{request.model}' is not supported. Use '{self.served_model_name}' instead."
            )
            if isinstance(request.input, str):
                request.input = [request.input]

            truncate_dim = request.dimensions or self.matryoshka_dim

            # Compute embeddings and convert to a PyTorch tensor on the GPU
            embeddings = self.embedding_model.encode(
                request.input, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=False,
            ).to(self.torch_device)

            if truncate_dim is not None:
                # Truncate and re-normalize the embeddings
                embeddings = embeddings[:, :truncate_dim]
                embeddings = embeddings / torch.norm(embeddings, dim=1, keepdim=True)

            # Move all embeddings to CPU at once before conversion
            embeddings = embeddings.cpu().tolist()

            # Convert embeddings to list format for response
            response_data = [
                {"index": idx, "embedding": emb}
                for idx, emb in enumerate(embeddings)
            ]
            return EmbeddingResponse(object="list", data=response_data, model=request.model)

        except Exception as e:
            self.logger.error(e)
            raise HTTPException(status_code=500, detail=str(e))

    @web_api.get("/v1/models")
    async def list_models(self):
        """Returns the list of available models in OpenAI-compatible format."""
        return {"object": "list", "data": self.available_models}



