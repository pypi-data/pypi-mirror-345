"""
Core module for NSFW image detection.
"""

import torch
import torch.nn.functional as F
from enum import Enum
from typing import List, Dict, Union, Optional
from PIL import Image
from transformers import AutoModelForImageClassification
from timm.data.transforms_factory import create_transform
from torchvision.transforms import Compose
from timm.data import resolve_data_config
from timm.models import get_pretrained_cfg


class NSFWLevel(str, Enum):
    """Enum for NSFW content levels."""
    NEUTRAL = "neutral"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NSFWDetector:
    """
    A class for detecting NSFW content in images using the EVA-based vision transformer.
    """

    def __init__(
        self, 
        model_name: str = "Freepik/nsfw_image_detector", 
        device: Optional[str] = None,
        dtype: torch.dtype = torch.bfloat16
    ):
        """
        Initialize the NSFW detector.

        Args:
            model_name: The name of the model to use from Hugging Face.
            device: The device to use for inference ('cuda', 'cpu', or None for auto-detection).
            use_bf16: Whether to use bfloat16 precision for inference.
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.device = device
        self.dtype = dtype
        
        # Load model
        self.model = AutoModelForImageClassification.from_pretrained(
            model_name, 
            torch_dtype=self.dtype
        ).to(device)
        
        # Load processor
        cfg = get_pretrained_cfg("eva02_base_patch14_448.mim_in22k_ft_in22k_in1k")
        self.processor: Compose = create_transform(**resolve_data_config(cfg.__dict__))
        
        # Define label mapping
        self.idx_to_label = {0: NSFWLevel.NEUTRAL, 1: NSFWLevel.LOW, 
                            2: NSFWLevel.MEDIUM, 3: NSFWLevel.HIGH}
    
    def _prepare_inputs(self, images: Union[Image.Image, List[Image.Image]]) -> torch.Tensor:
        """Prepare inputs for the model."""
        if isinstance(images, Image.Image):
            images = [images]
        
        return torch.stack([self.processor(img) for img in images]).to(self.device)
    
    def predict_proba(self, images: Union[Image.Image, List[Image.Image]]) -> List[Dict[str, float]]:
        """
        Predict probability scores for each NSFW category.
        
        Args:
            images: A single PIL Image or a list of PIL Images.
            
        Returns:
            A list of dictionaries with probability scores for each category.
        """
        inputs = self._prepare_inputs(images)
        
        with torch.inference_mode():
            logits = self.model(inputs).logits
            batch_probs = F.log_softmax(logits, dim=-1)
            batch_probs = torch.exp(batch_probs).cpu()
            
            output = []
            for i in range(len(batch_probs)):
                element_probs = batch_probs[i]
                output_img = {}
                danger_cum_sum = 0
                
                for j in range(len(element_probs) - 1, -1, -1):
                    danger_cum_sum += element_probs[j]
                    if j == 0:
                        danger_cum_sum = element_probs[j]
                    output_img[self.idx_to_label[j]] = danger_cum_sum.item()
                output.append(output_img)
        
        return output
    
    def is_nsfw(
        self, 
        images: Union[Image.Image, List[Image.Image]], 
        threshold_level: NSFWLevel = NSFWLevel.MEDIUM,
        threshold: float = 0.5
    ) -> Union[bool, List[bool]]:
        """
        Check if images contain NSFW content at or above the specified level.
        
        Args:
            images: A single PIL Image or a list of PIL Images.
            threshold_level: The NSFW level to check against (LOW, MEDIUM, HIGH).
            threshold: The probability threshold for classification.
            
        Returns:
            A boolean or list of booleans indicating if the image(s) contain NSFW content.
        """
        if threshold_level == NSFWLevel.NEUTRAL:
            raise ValueError("threshold_level cannot be NEUTRAL")
        
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        
        predictions = self.predict_proba(images)
        
        if isinstance(images, Image.Image):
            return predictions[0][threshold_level] >= threshold
        
        return [pred[threshold_level] >= threshold for pred in predictions]
    
    def __call__(
        self, 
        images: Union[Image.Image, List[Image.Image]], 
        threshold_level: NSFWLevel = NSFWLevel.MEDIUM,
        threshold: float = 0.5
    ) -> Union[bool, List[bool]]:
        """
        Alias for is_nsfw method for easier usage.
        """
        return self.is_nsfw(images, threshold_level, threshold) 