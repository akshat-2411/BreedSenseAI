import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image


class PredictionService:
    """Handles model loading and image classification."""

    def __init__(self, model_path: str, num_classes: int = 5):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_classes = num_classes
        self.model = self._load_model(model_path)      # may update num_classes
        self.classes = self._load_classes()              # uses final num_classes
        self.transform = self._build_transform()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_classes(self) -> list[str]:
        """Load class names from models/classes.txt.

        If the file has fewer entries than ``self.num_classes`` (which is
        auto-detected from the checkpoint), the list is padded with generic
        names so that indexing never fails.
        """
        classes_path = os.path.join("models", "classes.txt")
        names: list[str] = []
        if os.path.exists(classes_path):
            with open(classes_path, "r") as f:
                names = [line.strip() for line in f if line.strip()]

        # Pad or generate generic labels if needed
        while len(names) < self.num_classes:
            names.append(f"Class_{len(names)}")

        return names[: self.num_classes]

    def _load_model(self, model_path: str):
        """Load the PyTorch model weights.

        Handles checkpoints saved from a custom wrapper class where keys
        are prefixed with ``backbone.`` and the classifier is a custom
        multi-layer Sequential head instead of EfficientNet's default.
        """
        from torchvision.models import efficientnet_v2_s

        model = efficientnet_v2_s(weights=None)

        if not os.path.exists(model_path):
            # No weights → just swap the default head
            model.classifier[1] = nn.Linear(
                model.classifier[1].in_features, self.num_classes
            )
            model.to(self.device)
            model.eval()
            return model

        # --- Load checkpoint -------------------------------------------------
        state_dict = torch.load(model_path, map_location=self.device)

        # Strip "backbone." prefix if the model was saved inside a wrapper
        if any(k.startswith("backbone.") for k in state_dict):
            state_dict = {
                k.replace("backbone.", "", 1): v
                for k, v in state_dict.items()
            }

        # --- Detect custom classifier head ------------------------------------
        classifier_keys = [k for k in state_dict if k.startswith("classifier.")]
        max_layer_idx = max(
            (int(k.split(".")[1]) for k in classifier_keys), default=1
        )

        if max_layer_idx > 1:
            # Custom multi-layer classifier detected — rebuild it from the
            # weight shapes so the state_dict loads cleanly.
            fc1_weight = state_dict["classifier.1.weight"]
            fc1_in, fc1_out = fc1_weight.shape[1], fc1_weight.shape[0]

            fc2_weight = state_dict["classifier.5.weight"]
            fc2_out = fc2_weight.shape[0]

            fc3_weight = state_dict["classifier.9.weight"]
            fc3_out = fc3_weight.shape[0]

            model.classifier = nn.Sequential(
                nn.Dropout(p=0.3),                          # 0
                nn.Linear(fc1_in, fc1_out),                 # 1
                nn.BatchNorm1d(fc1_out),                    # 2
                nn.ReLU(),                                  # 3
                nn.Dropout(p=0.3),                          # 4
                nn.Linear(fc1_out, fc2_out),                # 5
                nn.BatchNorm1d(fc2_out),                    # 6
                nn.ReLU(),                                  # 7
                nn.Dropout(p=0.2),                          # 8
                nn.Linear(fc2_out, fc3_out),                # 9
            )
            self.num_classes = fc3_out

        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()
        return model

    @staticmethod
    def _build_transform():
        """Image preprocessing pipeline matching training transforms."""
        return transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, image_path: str) -> dict:
        """Run inference on a single image and return the top prediction."""
        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

        breed = self.classes[predicted.item()]
        return {
            "breed": breed,
            "confidence": round(confidence.item() * 100, 2),
        }
