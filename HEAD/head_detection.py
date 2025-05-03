"""Object Detection Module using ONNX model.

This module provides a class `HeadDetector` that performs object detection on images
using a pre-trained ONNX model with a fixed path.

Usage:
    from object_detector import HeadDetector

    detector = HeadDetector()
    labels, boxes, scores = detector.detect('path/to/image.jpg', output_image_path='output.jpg')
"""

import torch
import torchvision.transforms as T
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFilter

class HeadDetector:
    """A class for performing object detection using an ONNX model."""

    # Fixed path to the ONNX model (adjust as needed)
    DEFAULT_MODEL_PATH = 'head_model_640.onnx'

    def __init__(self, onnx_model_path=DEFAULT_MODEL_PATH, confidence_threshold=0.4):
        """
        Initialize the HeadDetector with a model path and detection threshold.

        Args:
            onnx_model_path (str): Path to the ONNX model file. Defaults to 'model.onnx'.
            confidence_threshold (float): Detection confidence threshold. Defaults to 0.4.
        """
        self.sess = ort.InferenceSession(onnx_model_path)
        self.confidence_threshold = confidence_threshold
        self.transforms = T.Compose([
            T.Resize((640, 640)),
            T.ToTensor(),
        ])


    def detect(self, image, confidence_threshold=None, output_image_path=None):
        """
        Perform object detection on the specified image.

        Args:
            image (str or PIL.Image.Image): Path to the input image file or a PIL Image object.
            confidence_threshold (float, optional): Detection confidence threshold. Takes self.confidence_theshold if not given.
            output_image_path (str, optional): Path to save the output image with bounding boxes.
                                              If None, no image is saved.

        Returns:
            tuple: (labels, boxes, scores)
                - labels: Tensor of detected class labels.
                - boxes: Tensor of bounding box coordinates.
                - scores: Tensor of confidence scores.
        """
       # Handle the input based on its type
        if isinstance(image, str):
            im_pil = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            im_pil = image.convert('RGB')
        else:
            raise TypeError("image must be a string (path to image) or a PIL Image object")
        w, h = im_pil.size
        orig_size = torch.tensor([w, h])[None]
        im_data = self.transforms(im_pil)[None]

        # Run inference
        output = self.sess.run(
            output_names=None,
            input_feed={'images': im_data.data.numpy(), "orig_target_sizes": orig_size.data.numpy()}
        )

        labels, boxes, scores = output

        # Filter detections based on threshold
        scr = scores[0]  # Single image, so take the first batch
        mask = scr > (confidence_threshold if confidence_threshold else self.confidence_threshold)
        lab = labels[0][mask]
        box = boxes[0][mask]
        scr = scr[mask]

        # Draw bounding boxes and save if output path is provided
        if output_image_path:
            drawn_image = self.draw_image(im_pil, lab, box)
            drawn_image.save(output_image_path)

        return lab, box, scr

    def draw_image(self, image, labels, boxes):
        """
        Draw bounding boxes and labels on the image.

        Args:
            image (PIL.Image): The input image to draw on.
            labels (Tensor): Detected class labels.
            boxes (Tensor): Bounding box coordinates.

        Returns:
            PIL.Image: The image with bounding boxes and labels drawn.
        """
        draw = ImageDraw.Draw(image)
        for b, l in zip(boxes, labels):
            draw.rectangle(list(b), outline='red')
            draw.text((b[0], b[1]), text=str(l.item()), fill='blue')
        return image

    def blur_heads(self, image, boxes, padding_factor=0.1, blur_factor=15):
        """
        Blur the head regions in the image with added padding around each bounding box.

        Args:
            image (PIL.Image): The input image.
            boxes (list or Tensor): Bounding box coordinates as [x1, y1, x2, y2].
            padding_factor (float): Factor to expand the bounding box (e.g., 0.1 = 10%).

        Returns:
            PIL.Image: The image with blurred head regions including padding.
        """
        for box in boxes:
            # Extract original coordinates
            x1, y1, x2, y2 = box

            # Calculate width and height
            width = x2 - x1
            height = y2 - y1

            # Calculate padding based on box size
            pad_width = padding_factor * width
            pad_height = padding_factor * height

            # Expand the bounding box
            x1_new = max(0, x1 - pad_width)
            y1_new = max(0, y1 - pad_height)
            x2_new = min(image.width, x2 + pad_width)
            y2_new = min(image.height, y2 + pad_height)

            # Convert to integers for cropping
            left = int(x1_new)
            upper = int(y1_new)
            right = int(x2_new)
            lower = int(y2_new)

            # Skip invalid regions
            if left >= right or upper >= lower:
                continue

            # Crop the expanded region
            region = image.crop((left, upper, right, lower))

            # Apply Gaussian blur
            blurred_region = region.filter(ImageFilter.GaussianBlur(radius=blur_factor))

            # Paste the blurred region back
            image.paste(blurred_region, (left, upper))

        return image
    
if __name__ == '__main__':
    detector = HeadDetector()
    image = Image.open("people.jpg").convert('RGB')
    labels, boxes, scores = detector.detect(image)
    blurred_image = detector.blur_heads(image, boxes, padding_factor=0.2, blur_factor=20)
    blurred_image.save("output_blurred.jpg")