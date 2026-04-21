from flask import Blueprint, jsonify, current_app, request, render_template
from flask_login import login_required
from bson.objectid import ObjectId
from utils.helpers import admin_required
from services.analytics_service import AnalyticsService

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/")
@login_required
@admin_required
def index():
    """Renders the Admin Panel UI."""
    return render_template("admin/dashboard.html")

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Returns total user count, total predictions made, breed distribution stats, and recent activity."""
    db = current_app.db
    
    total_users = db.users.count_documents({})
    total_predictions = db.predictions.count_documents({})
    
    # Breed distribution using aggregation
    pipeline = [
        {"$group": {"_id": "$predicted_breed", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    breed_stats = list(db.predictions.aggregate(pipeline))
    
    # Recent activity
    recent_cursor = db.predictions.find().sort("timestamp", -1).limit(50)
    recent_activity = []
    for pred in recent_cursor:
        pred["_id"] = str(pred["_id"])
        if "timestamp" in pred and hasattr(pred["timestamp"], "isoformat"):
            pred["timestamp"] = pred["timestamp"].isoformat()
        recent_activity.append(pred)
    
    return jsonify({
        "total_users": total_users,
        "total_predictions": total_predictions,
        "breed_distribution": breed_stats,
        "recent_activity": recent_activity
    })

@admin_bp.route("/users")
@login_required
@admin_required
def users_list():
    """Returns all registered users with their details (excluding sensitive fields)."""
    db = current_app.db
    users_cursor = db.users.find({}, {"password_hash": 0})
    
    users = []
    for user in users_cursor:
        # Convert ObjectId and datetime to string for JSON serialization
        user["_id"] = str(user["_id"])
        if "created_at" in user and hasattr(user["created_at"], "isoformat"):
            user["created_at"] = user["created_at"].isoformat()
        users.append(user)
        
    return jsonify({"users": users})

@admin_bp.route("/predictions/delete/<prediction_id>", methods=["DELETE", "POST"])
@login_required
@admin_required
def delete_prediction(prediction_id):
    """Deletes a specific entry from the predictions collection."""
    db = current_app.db
    
    try:
        obj_id = ObjectId(prediction_id)
    except Exception:
        return jsonify({"error": "Invalid prediction ID format."}), 400
        
    try:
        result = db.predictions.delete_one({"_id": obj_id})
        
        if result.deleted_count > 0:
            return jsonify({"message": f"Prediction {prediction_id} successfully deleted."}), 200
        else:
            return jsonify({"error": "Prediction not found."}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/stats")
@login_required
@admin_required
def api_stats():
    """Returns analytics data formatted for admin dashboard charts."""
    try:
        metrics = AnalyticsService.get_dashboard_metrics(current_app.db)
        return jsonify(metrics), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch analytics: {e}")
        return jsonify({"error": "Failed to fetch analytics data."}), 500
