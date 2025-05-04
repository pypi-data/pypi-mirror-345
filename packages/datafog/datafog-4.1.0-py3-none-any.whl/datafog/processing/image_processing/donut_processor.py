"""
Provides functionality for processing images using the Donut model.

This module implements a DonutProcessor class that uses the Donut model
for document understanding tasks, particularly OCR and information extraction
from images of documents.
"""

import importlib
import json
import re
import subprocess
import sys
from io import BytesIO

import numpy as np
import requests
from PIL import Image

from .image_downloader import ImageDownloader


class DonutProcessor:
    """
    Handles image processing using the Donut model.

    Provides methods for loading models, preprocessing images, parsing images
    for text extraction, and managing dependencies. Supports processing both
    local images and images from URLs.
    """

    def __init__(self, model_path="naver-clova-ix/donut-base-finetuned-cord-v2"):
        self.ensure_installed("torch")
        self.ensure_installed("transformers")

        import torch
        from transformers import DonutProcessor as TransformersDonutProcessor
        from transformers import VisionEncoderDecoderModel

        self.processor = TransformersDonutProcessor.from_pretrained(model_path)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        self.downloader = ImageDownloader()

    def ensure_installed(self, package_name):
        try:
            importlib.import_module(package_name)
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )

    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        # Convert to RGB if the image is not already in RGB mode
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert to numpy array
        image_np = np.array(image)

        # Ensure the image is 3D (height, width, channels)
        if image_np.ndim == 2:
            image_np = np.expand_dims(image_np, axis=-1)
            image_np = np.repeat(image_np, 3, axis=-1)

        return image_np

    async def parse_image(self, image: Image.Image) -> str:
        """Process w/ DonutProcessor and VisionEncoderDecoderModel"""
        # Preprocess the image
        image_np = self.preprocess_image(image)

        task_prompt = "<s_cord-v2>"
        decoder_input_ids = self.processor.tokenizer(
            task_prompt, add_special_tokens=False, return_tensors="pt"
        ).input_ids
        pixel_values = self.processor(images=image_np, return_tensors="pt").pixel_values

        outputs = self.model.generate(
            pixel_values.to(self.device),
            decoder_input_ids=decoder_input_ids.to(self.device),
            max_length=self.model.decoder.config.max_position_embeddings,
            early_stopping=True,
            pad_token_id=self.processor.tokenizer.pad_token_id,
            eos_token_id=self.processor.tokenizer.eos_token_id,
            use_cache=True,
            num_beams=1,
            bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )

        sequence = self.processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(
            self.processor.tokenizer.pad_token, ""
        )
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()

        result = self.processor.token2json(sequence)
        return json.dumps(result)

    def process_url(self, url: str) -> str:
        """Download an image from URL and process it to extract text."""
        image = self.downloader.download_image(url)
        return self.parse_image(image)

    def download_image(self, url: str) -> Image.Image:
        """Download an image from URL."""
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        return image
