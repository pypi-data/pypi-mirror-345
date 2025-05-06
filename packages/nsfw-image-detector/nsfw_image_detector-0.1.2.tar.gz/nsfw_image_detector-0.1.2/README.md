# NSFW Image Detector

A Python library that provides easy-to-use interfaces for NSFW (Not Safe For Work) image detection using an EVA-based vision transformer model published on Hugging Face: See the model details in [Model card](https://huggingface.co/Freepik/nsfw_image_detector).

## Installation

You can install this library via pip. The package is available in [PyPI](https://pypi.org/project/nsfw-image-detector/)

```bash
pip install nsfw_image_detector
```

## Quick Usage

```python
from PIL import Image
from nsfw_image_detector import NSFWDetector

# Initialize the detector
detector = NSFWDetector()

# Load and classify an image
image = Image.open("path/to/your/image.jpg")

# Check if the image contains NSFW content
is_nsfw = detector.is_nsfw(image)
print(f"Is NSFW: {is_nsfw}")

# Get probability scores for all categories
probabilities = detector.predict_proba(image)
print(probabilities)
```

## License

Apache License 2.0
