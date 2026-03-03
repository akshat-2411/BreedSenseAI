import os
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from services.prediction_service import PredictionService
from services.gradcam_service import generate_gradcam

predict_bp = Blueprint("predict", __name__)

# Lazy-loaded singleton
_prediction_service: PredictionService | None = None


def _get_prediction_service() -> PredictionService:
    """Return (and lazily create) the prediction service."""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService(
            model_path=current_app.config["MODEL_PATH"],
            num_classes=current_app.config["NUM_CLASSES"],
        )
    return _prediction_service


def _allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@predict_bp.route("/predict", methods=["POST"])
@login_required
def predict():
    """Accept an image and return breed prediction + Grad-CAM heatmap."""

    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]
    if file.filename == "" or not _allowed_file(file.filename):
        return jsonify({"error": "Invalid or unsupported file type."}), 400

    # --- Save image with a unique name to avoid overwrites ---
    original_name = secure_filename(file.filename)
    ext = original_name.rsplit(".", 1)[1].lower() if "." in original_name else "jpg"
    unique_filename = f"{uuid.uuid4().hex}_{original_name}"
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)
    file.save(filepath)

    try:
        service = _get_prediction_service()
        result = service.predict(filepath)

        # --- Generate Grad-CAM heatmap ---
        heatmap_dir = os.path.join("static", "heatmaps")
        heatmap_filename = generate_gradcam(
            model=service.model,
            image_path=filepath,
            transform=service.transform,
            device=service.device,
            save_dir=heatmap_dir,
            class_idx=None,          # use predicted class
        )
        heatmap_url = url_for("static", filename=f"heatmaps/{heatmap_filename}")

        # --- Store prediction record in MongoDB ---
        record = {
            "user_id": current_user.id,
            "filename": unique_filename,
            "original_filename": original_name,
            "predicted_breed": result["breed"],
            "confidence_score": result["confidence"],
            "image_path": filepath.replace("\\", "/"),
            "heatmap_filename": heatmap_filename,
            "timestamp": datetime.now(timezone.utc),
        }
        current_app.db.predictions.insert_one(record)

        return jsonify({**result, "heatmap_url": heatmap_url}), 200

    except Exception as e:
        current_app.logger.error(f"Prediction failed: {e}")
        return jsonify({"error": "Prediction failed. Please try again."}), 500



