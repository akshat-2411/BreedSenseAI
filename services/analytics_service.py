from datetime import datetime, timedelta, timezone

class AnalyticsService:
    """Service to handle statistical analytics for the Admin Dashboard."""

    @staticmethod
    def get_dashboard_metrics(db) -> dict:
        """
        Pulls comprehensive metrics from the MongoDB database.
        Returns a dictionary containing total predictions, top breed, and daily usage.
        """
        # 1. Total Predictions: simple count of all documents
        total_predictions = db.predictions.count_documents({})
        
        # 2. Top Breed & Breed Distribution: Aggregate by predicted_breed
        breed_pipeline = [
            {"$group": {"_id": "$predicted_breed", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        breed_cursor = list(db.predictions.aggregate(breed_pipeline))
        top_breed = breed_cursor[0]["_id"] if breed_cursor else "N/A"
        
        breed_distribution = {
            "labels": [b["_id"] for b in breed_cursor],
            "values": [b["count"] for b in breed_cursor]
        }
        
        # 3. Daily Usage (Last 30 Days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        daily_usage_pipeline = [
            {"$match": {"timestamp": {"$gte": thirty_days_ago}}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}} # Sort chronologically
        ]
        
        daily_results = list(db.predictions.aggregate(daily_usage_pipeline))
        
        # Extract and format for Chart.js
        labels = []
        values = []
        
        # Even if some days have 0 predictions and are skipped inherently by the grouping,
        # we parse exactly what MongoDB matched to hand over to Chart.js
        for day in daily_results:
            try:
                dt_str = day["_id"]
                dt_obj = datetime.strptime(dt_str, "%Y-%m-%d")
                labels.append(dt_obj.strftime("%b %d"))
            except Exception:
                labels.append(day["_id"])
            values.append(day["count"])
            
        daily_usage = {
            "labels": labels,
            "values": values
        }
        
        return {
            "total_predictions": total_predictions,
            "top_breed": top_breed,
            "breed_distribution": breed_distribution,
            "daily_usage": daily_usage
        }
