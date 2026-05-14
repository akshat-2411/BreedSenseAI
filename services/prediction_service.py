"""
prediction_service.py — ResNet-18 Prediction Service
=============================================================
Loads a single ResNet-18 model from best_model.pth.
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision.models import resnet18
from PIL import Image

# Limit CPU threads to prevent memory bloat on Render's free tier.
# PyTorch by default spawns as many OpenMP threads as CPU cores,
# which can exhaust RAM on constrained environments.
torch.set_num_threads(1)
torch.set_num_interop_threads(1)


class PredictionService:
    """ResNet-18 single-model prediction service."""

    def __init__(self,
                 num_classes: int = 50,
                 model_path: str = "models/weights/best_model.pth"):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.classes = self._load_classes()
        self.num_classes = len(self.classes) if self.classes else num_classes
        self.model = self._load_model(model_path)
        self.transform = self._build_transform()

    # ------------------------------------------------------------------

    def _load_model(self, path: str) -> nn.Module:
        """Build ResNet18 with custom head and load weights."""
        model = resnet18(weights=None)

        # Replace final layer
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, self.num_classes)

        # Disable inplace ReLUs to prevent recursion errors with backward hooks
        for m in model.modules():
            if isinstance(m, nn.ReLU):
                m.inplace = False

        if os.path.exists(path):
            sd = torch.load(path, map_location=torch.device('cpu'), weights_only=True)
            # Unwrap common checkpoint wrappers
            if isinstance(sd, dict):
                for key in ("state_dict", "model_state_dict", "model"):
                    if key in sd:
                        sd = sd[key]
                        break
            # Strip backbone. prefix if it exists
            if any(k.startswith("backbone.") for k in sd.keys()):
                sd = {k.replace("backbone.", "", 1): v for k, v in sd.items()}
            model.load_state_dict(sd, strict=True)
        else:
            print(f"[WARNING] Weight file not found: {path}. Using random init.")

        return model.to(self.device).eval()

    @staticmethod
    def _build_transform() -> transforms.Compose:
        """Validation transform — matches training val_transform."""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

    def _load_classes(self) -> list[str]:
        """Load class labels."""
        path = os.path.join("models", "classes.txt")
        names: list[str] = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                names = [line.strip() for line in f if line.strip()]
        return names

    # ------------------------------------------------------------------

    def predict(self, image_path: str) -> dict:
        """Run inference on a single image file."""
        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            probs = F.softmax(logits, dim=1)
            confidence, predicted_idx = torch.max(probs, dim=1)

        return {
            "breed": self.classes[predicted_idx.item()],
            "confidence": round(confidence.item() * 100, 2),
        }
