import os
import torch
from services.prediction_service import PredictionService
from services.gradcam_service import generate_gradcam

def test():
    print("Testing PredictionService & GradCAM...")
    service = PredictionService(num_classes=50)
    
    # Create a dummy image
    from PIL import Image
    import numpy as np
    dummy_img = Image.fromarray(np.uint8(np.random.rand(224, 224, 3) * 255))
    dummy_img.save("dummy.jpg")
    
    print("Running predict...")
    res = service.predict("dummy.jpg")
    print("Prediction:", res)
    
    print("Running gradcam...")
    os.makedirs("static/heatmaps", exist_ok=True)
    heatmap = generate_gradcam(
        model=service.model,
        image_path="dummy.jpg",
        transform=service.transform,
        device=service.device,
        save_dir="static/heatmaps",
    )
    print("Heatmap generated:", heatmap)

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        import traceback
        traceback.print_exc()
