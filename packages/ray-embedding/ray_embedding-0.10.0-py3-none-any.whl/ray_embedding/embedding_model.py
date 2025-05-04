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
    },
    user_config={
        "max_batch_size": 8,
        "batch_wait_timeout_s": 0.25,
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

    async def reconfigure(self, user_config: Dict):
        assert "max_batch_size" in user_config and "batch_wait_timeout_s" in user_config, "Invalid user config"
        self.logger.info(f"Reconfiguring dynamic batching parameters: {user_config}")
        self.__create_embeddings_batch.set_max_batch_size(user_config["max_batch_size"])
        self.__create_embeddings_batch.set_batch_wait_timeout_s(user_config["batch_wait_timeout_s"])

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
                request.input, convert_to_tensor=True, normalize_embeddings=True
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

    @serve.batch(max_batch_size=8, batch_wait_timeout_s=0.25)
    async def __create_embeddings_batch(self, requests_batch: List[EmbeddingRequest]) -> List[EmbeddingResponse]:
        self_0 = self[0] if isinstance(self, list) else self  # Ray also passes an array of self refs; just take the first one
        embedding_model, matryoshka_dim, torch_device = self_0.embedding_model, self_0.matryoshka_dim, self_0.torch_device

        inputs, truncate_dims, num_inputs_list = [], [], []
        for request in requests_batch:
            input_text = request.input if isinstance(request.input, list) else [request.input] # Can be a list of texts
            inputs.extend(input_text)
            num_inputs_list.append(len(input_text))
            truncate_dims.append(request.dimensions or matryoshka_dim)

        embeddings = embedding_model.encode(
            inputs, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=False,
        ).to(torch_device)

        model_name = requests_batch[0].model
        truncate_needed = any(dim is not None for dim in truncate_dims)
        results_batch, ix = [], 0

        if truncate_needed:
            for truncate_dim, num_inputs in zip(truncate_dims, num_inputs_list):
                batch_embeddings = embeddings[ix: ix + num_inputs]
                ix += num_inputs

                if truncate_dim is not None:
                    # Truncate and normalize using pytorch (faster)
                    batch_embeddings = batch_embeddings[:, :truncate_dim]
                    batch_embeddings = batch_embeddings / torch.norm(batch_embeddings, dim=1, keepdim=True)

                batch_embeddings = batch_embeddings.cpu().tolist()
                response_data = [
                    {"index": emb_ix, "embedding": emb} for emb_ix, emb in enumerate(batch_embeddings)
                ]
                results_batch.append(EmbeddingResponse(object="list", data=response_data, model=model_name))
        else:
            embeddings_list = embeddings.cpu().tolist() # Move everything to CPU
            for num_inputs in num_inputs_list:
                batch_embeddings = embeddings_list[ix: ix + num_inputs]
                ix += num_inputs

                response_data = [
                    {"index": emb_ix, "embedding": emb} for emb_ix, emb in enumerate(batch_embeddings)
                ]
                results_batch.append(EmbeddingResponse(object="list", data=response_data, model=model_name))

        return results_batch

    @web_api.get("/v1/models")
    async def list_models(self):
        """Returns the list of available models in OpenAI-compatible format."""
        return {"object": "list", "data": self.available_models}



