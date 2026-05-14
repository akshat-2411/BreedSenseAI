import os
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from services.prediction_service import PredictionService
from services.gradcam_service import generate_gradcam
from services.report_service import generate_breed_report
from utils.helpers import load_breed_info

predict_bp = Blueprint("predict", __name__)

# Lazy-loaded singleton
_prediction_service: PredictionService | None = None


def _get_prediction_service() -> PredictionService:
    """Return (and lazily create) the prediction service."""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService(
            num_classes=current_app.config["NUM_CLASSES"],
            model_path=current_app.config["MODEL_PATH"],
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

        # --- Generate Grad-CAM heatmap (optional — fails gracefully) ---
        heatmap_dir = os.path.join("static", "heatmaps")
        heatmap_url = None
        heatmap_filename = None
        try:
            heatmap_filename = generate_gradcam(
                model=service.model,
                image_path=filepath,
                transform=service.transform,
                device=service.device,
                save_dir=heatmap_dir,
                class_idx=None,          # use predicted class
            )
            heatmap_url = url_for("static", filename=f"heatmaps/{heatmap_filename}")
        except Exception as heatmap_err:
            current_app.logger.warning(f"Grad-CAM failed (non-critical): {heatmap_err}")

        # --- Fetch breed info ---
        breed_info_data = load_breed_info()
        breed_details = breed_info_data.get(result["breed"], {})

        info = {
            "origin": breed_details.get("origin", "Unknown"),
            "milk_yield": breed_details.get("milk_yield", "Unknown"),
            "purpose": breed_details.get("purpose", "Unknown"),
            "physical_characteristics": breed_details.get("physical_characteristics", "Unknown")
        }

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
        inserted = current_app.db.predictions.insert_one(record)

        return jsonify({**result, "heatmap_url": heatmap_url, "info": info, "prediction_id": str(inserted.inserted_id)}), 200

    except Exception as e:
        current_app.logger.error(f"Prediction failed: {e}")
        return jsonify({"error": "Prediction failed. Please try again."}), 500


@predict_bp.route("/prediction/download/<prediction_id>", methods=["GET"])
@login_required
def download_report(prediction_id):
    """Download a PDF report for a specific prediction."""
    try:
        pred_id = ObjectId(prediction_id)
    except Exception:
        return jsonify({"error": "Invalid prediction ID format."}), 400

    record = current_app.db.predictions.find_one({"_id": pred_id})
    if not record:
        return jsonify({"error": "Prediction not found."}), 404

    # Ensure the user owns the prediction or is an admin
    if record.get("user_id") != current_user.id and current_user.role != "admin":
        return jsonify({"error": "Access denied."}), 403

    heatmap_filename = record.get("heatmap_filename")
    heatmap_path = os.path.join("static", "heatmaps", heatmap_filename) if heatmap_filename else None

    # Format the data for the report generator
    prediction_data = {
        "breed_name": record.get("predicted_breed", "Unknown"),
        "confidence": record.get("confidence_score", 0),
        "original_image_path": record.get("image_path"),
        "heatmap_image_path": heatmap_path
    }

    try:
        pdf_buffer = generate_breed_report(prediction_data)
        
        return send_file(
            pdf_buffer,
            download_name=f"BreedSense_Report_{prediction_id}.pdf",
            as_attachment=True,
            mimetype="application/pdf"
        )
    except Exception as e:
        current_app.logger.error(f"Report generation failed: {e}")
        return jsonify({"error": "Failed to generate report."}), 500
