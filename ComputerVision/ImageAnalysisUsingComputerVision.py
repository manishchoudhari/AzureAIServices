#Image Analysis using Azure Computer Vision and Gradio UI  

import gradio as gr
import io
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image

# -------------------------
# Azure Authentication
# -------------------------
subscription_key = "<Type your Azure Computer Vision Key Here>"
endpoint = "<Type your Azure Computer Vision End Point Here>"

computervision_client = ComputerVisionClient(
    endpoint,
    CognitiveServicesCredentials(subscription_key)
)

# -------------------------
# Image analysis function
# -------------------------
def analyze_image(image):
    """
    image: PIL Image from Gradio
    returns: formatted text with image tags
    """
    if image is None:
        return "No image provided."

    # Convert PIL image to byte stream
    image_stream = io.BytesIO()
    image.save(image_stream, format="JPEG")
    image_stream.seek(0)

    # Call Azure Vision API
    tags_result = computervision_client.tag_image_in_stream(image_stream)

    if not tags_result.tags:
        return "No tags detected."

    # Format output text
    result_text = "Image Characteristics (Tags):\n\n"
    for tag in tags_result.tags:
        result_text += f"- {tag.name} ({tag.confidence*100:.2f}%)\n"

    return result_text


# -------------------------
# Gradio UI
# -------------------------
interface = gr.Interface(
    fn=analyze_image,
    inputs=gr.Image(type="pil", label="Upload an Image"),
    outputs=gr.Textbox(label="Image Characteristics"),
    title="Azure AI Vision – Image Tagging",
    description="Upload an image to analyze its characteristics using Azure Computer Vision."
)

# Launch the app
interface.launch()
