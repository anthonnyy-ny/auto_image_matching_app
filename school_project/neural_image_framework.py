# -*- coding: utf-8 -*-

import os
import threading
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from app_paths import PROJECT_ROOT
from embedding_cache import embedding_cache
from image_embedding import image_embedding as classical_embedding


AI_ALLOW_DOWNLOAD_ENV = "AI_ALLOW_DOWNLOAD"
AI_HF_MODEL_ENV = "AI_HF_MODEL"
AI_LOCAL_MODEL_ENV = "AI_MATCH_MODEL"
DEFAULT_HF_MODEL = "facebook/dinov2-base"
TRAINED_MODEL_PATH = PROJECT_ROOT / "models" / "ai_matcher.pt"


@dataclass(frozen=True)
class EncoderInfo:
    backend: str
    model_id: str
    embedding_dim: int
    status: str
    device: str = "cpu"
    neural_framework: str = "none"
    source: str = "fallback"
    ready: bool = False
    allow_download: bool = False
    last_error: str | None = None


class BaseImageEncoder:
    info = EncoderInfo(
        backend="classical-fallback",
        model_id="classical-fallback",
        embedding_dim=131,
        status="Using deterministic classical feature fallback.",
    )

    def encode(self, image, image_path=None, hash_str=None):
        return classical_embedding(image, hash_str)


class HuggingFaceVisionEncoder(BaseImageEncoder):
    def __init__(self, model_id=None, allow_download=False):
        self.model_id = model_id or DEFAULT_HF_MODEL
        self.allow_download = allow_download
        self._torch = None
        self._processor = None
        self._model = None
        self._device = "cpu"
        self._lock = threading.Lock()
        self.info = self._load()

    def _load(self):
        try:
            import torch
            from transformers import AutoImageProcessor, AutoModel

            self._torch = torch
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            local_only = not self.allow_download
            self._processor = AutoImageProcessor.from_pretrained(self.model_id, local_files_only=local_only)
            self._model = AutoModel.from_pretrained(self.model_id, local_files_only=local_only)
            self._model.to(self._device)
            self._model.eval()
            dim = int(getattr(getattr(self._model, "config", None), "hidden_size", 0) or 0)
            if dim <= 0:
                dim = 768
            return EncoderInfo(
                backend="huggingface",
                model_id=self.model_id,
                embedding_dim=dim,
                status="Loaded Hugging Face vision encoder.",
                device=self._device,
                neural_framework="pytorch+transformers",
                source="huggingface",
                ready=True,
                allow_download=self.allow_download,
            )
        except Exception as exc:
            return EncoderInfo(
                backend="huggingface-unavailable",
                model_id=self.model_id,
                embedding_dim=131,
                status="Hugging Face model unavailable; falling back.",
                neural_framework="pytorch+transformers",
                source="huggingface",
                ready=False,
                allow_download=self.allow_download,
                last_error=str(exc),
            )

    def encode(self, image, image_path=None, hash_str=None):
        if not self.info.ready:
            return classical_embedding(image, hash_str)
        pil_image = _to_pil(image)
        with self._lock:
            with self._torch.no_grad():
                inputs = self._processor(images=pil_image, return_tensors="pt")
                inputs = {key: value.to(self._device) for key, value in inputs.items()}
                outputs = self._model(**inputs)
                vector = self._pool_outputs(outputs)
        return _normalize(vector)

    def _pool_outputs(self, outputs):
        if getattr(outputs, "pooler_output", None) is not None:
            return outputs.pooler_output[0].detach().cpu().numpy()
        hidden = outputs.last_hidden_state
        if hidden.ndim == 3 and hidden.shape[1] > 0:
            return hidden[:, 0, :][0].detach().cpu().numpy()
        return hidden.mean(dim=1)[0].detach().cpu().numpy()


class LocalTrainedEncoder(BaseImageEncoder):
    def __init__(self, model_path):
        self.model_path = Path(model_path)
        self._torch = None
        self._model = None
        self._preprocess = None
        self._device = "cpu"
        self._lock = threading.Lock()
        self.info = self._load()

    def _load(self):
        if not self.model_path.exists():
            return EncoderInfo(
                backend="trained-unavailable",
                model_id=str(self.model_path),
                embedding_dim=131,
                status="No local trained matcher was found.",
                neural_framework="pytorch",
                source="local-trained",
                ready=False,
            )
        try:
            import torch
            import torchvision.models as models
            import torchvision.transforms as transforms

            checkpoint = torch.load(self.model_path, map_location="cpu")
            arch = checkpoint.get("arch", "resnet50")
            if arch != "resnet50":
                raise ValueError("Unsupported local matcher architecture: " + str(arch))
            model = models.resnet50(weights=None)
            in_features = model.fc.in_features
            projection_dim = int(checkpoint.get("projection_dim", 512))
            model.fc = torch.nn.Linear(in_features, projection_dim)
            model.load_state_dict(checkpoint["model"])
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            model.to(self._device)
            model.eval()
            self._torch = torch
            self._model = model
            self._preprocess = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            return EncoderInfo(
                backend="local-trained",
                model_id=str(self.model_path),
                embedding_dim=projection_dim,
                status="Loaded local fine-tuned neural matcher.",
                device=self._device,
                neural_framework="pytorch+torchvision",
                source="local-trained",
                ready=True,
            )
        except Exception as exc:
            return EncoderInfo(
                backend="trained-unavailable",
                model_id=str(self.model_path),
                embedding_dim=131,
                status="Local trained matcher failed to load; falling back.",
                neural_framework="pytorch+torchvision",
                source="local-trained",
                ready=False,
                last_error=str(exc),
            )

    def encode(self, image, image_path=None, hash_str=None):
        if not self.info.ready:
            return classical_embedding(image, hash_str)
        pil_image = _to_pil(image)
        with self._lock:
            with self._torch.no_grad():
                tensor = self._preprocess(pil_image).unsqueeze(0).to(self._device)
                vector = self._model(tensor)[0].detach().cpu().numpy()
        return _normalize(vector)


class NeuralImageMatchingFramework:
    def __init__(self):
        self._encoder = None
        self._lock = threading.Lock()
        self._load_encoder()

    def encode(self, image, image_path=None, hash_str=None):
        model_key = self.model_key()
        if image_path:
            cached = embedding_cache.load(image_path, model_key)
            if cached is not None:
                return cached
        vector = self._encoder.encode(image, image_path, hash_str)
        if image_path:
            embedding_cache.save(image_path, model_key, vector)
        return vector

    def metadata(self):
        info = self._encoder.info
        return {
            "ai_backend": info.backend,
            "ai_model": info.model_id,
            "ai_model_source": info.source,
            "ai_status": info.status,
            "ai_ready": info.ready,
            "ai_device": info.device,
            "ai_framework": info.neural_framework,
            "ai_allow_download": info.allow_download,
            "ai_last_error": info.last_error,
            "embedding_dim": info.embedding_dim,
            "ai_cache_hits": embedding_cache.hits,
            "ai_cache_misses": embedding_cache.misses,
            "ai_cache_writes": embedding_cache.writes,
            "available_models": [
                {"id": DEFAULT_HF_MODEL, "source": "huggingface", "recommended": True},
                {"id": "google/vit-base-patch16-224", "source": "huggingface", "recommended": False},
                {"id": "microsoft/resnet-50", "source": "huggingface", "recommended": False},
            ],
        }

    def model_key(self):
        info = self._encoder.info
        return (info.backend + "-" + info.model_id).replace("/", "_").replace("\\", "_").replace(":", "_")

    def reload(self):
        with self._lock:
            self._load_encoder()
        return self.metadata()

    def _load_encoder(self):
        local_model = Path(os.environ.get(AI_LOCAL_MODEL_ENV, "") or TRAINED_MODEL_PATH)
        local_encoder = LocalTrainedEncoder(local_model)
        if local_encoder.info.ready:
            self._encoder = local_encoder
            return

        allow_download = os.environ.get(AI_ALLOW_DOWNLOAD_ENV) == "1"
        hf_model = os.environ.get(AI_HF_MODEL_ENV, DEFAULT_HF_MODEL)
        hf_encoder = HuggingFaceVisionEncoder(hf_model, allow_download)
        if hf_encoder.info.ready:
            self._encoder = hf_encoder
            return

        fallback = BaseImageEncoder()
        fallback.info = EncoderInfo(
            backend="classical-fallback",
            model_id="classical-fallback",
            embedding_dim=131,
            status="Neural encoders are unavailable; using classical fallback.",
            neural_framework="classical",
            source="fallback",
            ready=False,
            allow_download=allow_download,
            last_error=hf_encoder.info.last_error or local_encoder.info.last_error,
        )
        self._encoder = fallback


def _to_pil(image):
    from PIL import Image

    if image is None or image.size == 0:
        image = np.zeros((224, 224, 3), dtype=np.uint8)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def _normalize(vector):
    vector = np.asarray(vector, dtype=np.float32)
    norm = float(np.linalg.norm(vector))
    if norm > 0:
        vector /= norm
    return vector


_FRAMEWORK = None
_FRAMEWORK_LOCK = threading.Lock()


def get_neural_framework():
    global _FRAMEWORK
    if _FRAMEWORK is None:
        with _FRAMEWORK_LOCK:
            if _FRAMEWORK is None:
                _FRAMEWORK = NeuralImageMatchingFramework()
    return _FRAMEWORK
