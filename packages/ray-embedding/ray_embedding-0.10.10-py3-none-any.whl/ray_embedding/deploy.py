from typing import Dict, Any, Optional
from ray.serve import Application
from ray_embedding.embedding_model import EmbeddingModel
import torch


def deploy_model(args: Dict[str, Any]) -> Application:
    """Builds and deploys a SentenceTransformer embedding model.
    :arg args: arguments for initializing a SentenceTransformer model
    :returns: a Ray Serve Application
    """
    assert args
    deployment_name: str = args.pop("deployment", "")
    assert deployment_name

    model: str = args.pop("model", "")
    assert model

    device: Optional[str] = args.pop("device", None)
    backend: Optional[str] = args.pop("backend", "torch")
    matryoshka_dim: Optional[int] = args.pop("matryoshka_dim", None)
    trust_remote_code: Optional[bool] = args.pop("trust_remote_code", False)
    model_kwargs: Dict[str, Any] = args.pop("model_kwargs", {})
    if "torch_dtype" in model_kwargs:
        torch_dtype = model_kwargs["torch_dtype"].strip()
        if torch_dtype == "float16":
            model_kwargs["torch_dtype"] = torch.float16
        elif torch_dtype == "bfloat16":
            model_kwargs["torch_dtype"] = torch.bfloat16
        elif torch_dtype == "float32":
            model_kwargs["torch_dtype"] = torch.float32
        else:
            raise ValueError(f"Invalid torch_dtype: '{torch_dtype}'")

    deployment = EmbeddingModel.options(name=deployment_name).bind(model=model,
                                                                   device=device,
                                                                   backend=backend,
                                                                   matryoshka_dim=matryoshka_dim,
                                                                   trust_remote_code=trust_remote_code,
                                                                   model_kwargs=model_kwargs
                                                                   )
    return deployment