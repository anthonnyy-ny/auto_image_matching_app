# -*- coding: utf-8 -*-

import os
from pathlib import Path

import cv2
import numpy as np

from app_paths import PROJECT_ROOT
from embedding_cache import embedding_cache
from image_embedding import image_embedding as classical_embedding


AI_MODEL_ENV = "AI_MATCH_MODEL"
AI_DOWNLOAD_ENV = "AI_ALLOW_DOWNLOAD"
TRAINED_MODEL_PATH = PROJECT_ROOT / "models" / "ai_matcher.pt"


class AIEmbeddingEngine:
    def __init__(self):
        self.backend = "classical-fallback"
        self.model_key = "classical-fallback"
        self.embedding_dim = 131
        self.status = "AI libraries are not loaded; using classical fallback."
        self._torch = None
        self._model = None
        self._preprocess = None
        self._device = "cpu"
        self._load_error = None
        self._load()

    def metadata(self):
        return {
            "ai_backend": self.backend,
            "ai_model": self.model_key,
            "embedding_dim": self.embedding_dim,
            "ai_status": self.status,
            "ai_cache_hits": embedding_cache.hits,
            "ai_cache_misses": embedding_cache.misses,
            "ai_cache_writes": embedding_cache.writes,
        }

    def encode(self, image, image_path=None, hash_str=None):
        if self.backend == "classical-fallback":
            return classical_embedding(image, hash_str)
        if image_path:
            cached = embedding_cache.load(image_path, self.model_key)
            if cached is not None:
                return cached
        try:
            vector = self._encode_ai(image)
        except Exception as exc:
            self._load_error = str(exc)
            vector = classical_embedding(image, hash_str)
        if image_path:
            embedding_cache.save(image_path, self.model_key, vector)
        return vector

    def _load(self):
        custom_model = Path(os.environ.get(AI_MODEL_ENV, "") or TRAINED_MODEL_PATH)
        if custom_model.exists() and self._try_load_trained(custom_model):
            return
        if self._try_load_open_clip():
            return
        if self._try_load_transformers_dinov2():
            return
        if self._try_load_torchvision():
            return

    def _try_load_trained(self, model_path):
        try:
            import torch
            import torchvision.transforms as transforms
            from PIL import Image

            checkpoint = torch.load(model_path, map_location="cpu")
            arch = checkpoint.get("arch", "resnet50")
            if arch != "resnet50":
                return False
            import torchvision.models as models

            backbone = models.resnet50(weights=None)
            in_features = backbone.fc.in_features
            projection_dim = int(checkpoint.get("projection_dim", 512))
            backbone.fc = torch.nn.Linear(in_features, projection_dim)
            backbone.load_state_dict(checkpoint["model"])
            backbone.eval()
            self._torch = torch
            self._pil_image = Image
            self._model = backbone
            self._preprocess = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            self.backend = "trained-resnet50"
            self.model_key = "trained-resnet50-" + model_path.stem
            self.embedding_dim = projection_dim
            self.status = "Loaded local trained matcher: " + str(model_path)
            return True
        except Exception as exc:
            self._load_error = str(exc)
            return False

    def _try_load_open_clip(self):
        try:
            import torch
            import open_clip
            from PIL import Image

            pretrained = "laion2b_s34b_b79k" if os.environ.get(AI_DOWNLOAD_ENV) == "1" else None
            if pretrained is None:
                return False
            model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained=pretrained)
            model.eval()
            self._torch = torch
            self._pil_image = Image
            self._model = model
            self._preprocess = preprocess
            self.backend = "open_clip"
            self.model_key = "open_clip-ViT-B-32-" + pretrained
            self.embedding_dim = 512
            self.status = "Loaded OpenCLIP ViT-B-32."
            return True
        except Exception as exc:
            self._load_error = str(exc)
            return False

    def _try_load_transformers_dinov2(self):
        try:
            if os.environ.get(AI_DOWNLOAD_ENV) != "1":
                return False
            import torch
            from PIL import Image
            from transformers import AutoImageProcessor, AutoModel

            model_name = "facebook/dinov2-base"
            processor = AutoImageProcessor.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            model.eval()
            self._torch = torch
            self._pil_image = Image
            self._processor = processor
            self._model = model
            self.backend = "dinov2"
            self.model_key = "dinov2-base"
            self.embedding_dim = 768
            self.status = "Loaded DINOv2 base through transformers."
            return True
        except Exception as exc:
            self._load_error = str(exc)
            return False

    def _try_load_torchvision(self):
        try:
            import torch
            import torchvision.models as models
            import torchvision.transforms as transforms
            from PIL import Image

            weights = models.ResNet50_Weights.DEFAULT if os.environ.get(AI_DOWNLOAD_ENV) == "1" else None
            if weights is None:
                return False
            model = models.resnet50(weights=weights)
            model.fc = torch.nn.Identity()
            model.eval()
            self._torch = torch
            self._pil_image = Image
            self._model = model
            self._preprocess = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            self.backend = "torchvision-resnet50"
            self.model_key = "torchvision-resnet50-imagenet"
            self.embedding_dim = 2048
            self.status = "Loaded torchvision ResNet50 ImageNet weights."
            return True
        except Exception as exc:
            self._load_error = str(exc)
            return False

    def _encode_ai(self, image):
        pil_image = self._to_pil(image)
        with self._torch.no_grad():
            if self.backend == "dinov2":
                inputs = self._processor(images=pil_image, return_tensors="pt")
                outputs = self._model(**inputs)
                vector = outputs.last_hidden_state[:, 0, :][0].detach().cpu().numpy()
            elif self.backend == "open_clip":
                tensor = self._preprocess(pil_image).unsqueeze(0)
                vector = self._model.encode_image(tensor)[0].detach().cpu().numpy()
            else:
                tensor = self._preprocess(pil_image).unsqueeze(0)
                vector = self._model(tensor)[0].detach().cpu().numpy()
        vector = np.asarray(vector, dtype=np.float32)
        norm = float(np.linalg.norm(vector))
        if norm > 0:
            vector /= norm
        return vector

    def _to_pil(self, image):
        if image is None or image.size == 0:
            image = np.zeros((224, 224, 3), dtype=np.uint8)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self._pil_image.fromarray(rgb)


_ENGINE = None


def ai_embedding(image, image_path=None, hash_str=None):
    return get_ai_engine().encode(image, image_path, hash_str)


def ai_embedding_metadata():
    return get_ai_engine().metadata()


def get_ai_engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = AIEmbeddingEngine()
    return _ENGINE
