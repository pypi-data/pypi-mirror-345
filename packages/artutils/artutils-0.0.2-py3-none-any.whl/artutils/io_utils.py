import cv2, os
import matplotlib.pyplot as plt
from PIL import Image

def load_and_resize_image(image_path, size=(100, 100)):
    """Load an image, convert BGR to RGB, and resize."""
    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        raise ValueError(f"Image at path {image_path} could not be loaded.")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    if size:
        image_rgb = cv2.resize(image_rgb, size)
    return image_rgb

def plot_image(image):
    """Plot an RGB image without axes."""
    plt.imshow(image)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def save_tile(tile, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    Image.fromarray(tile).save(out_path)