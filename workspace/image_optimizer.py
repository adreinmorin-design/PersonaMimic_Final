import os
from PIL import Image


def optimize_images(directory, quality=85):
    """
    Industrial Image Optimizer: Reduces file size to improve SEO and PageSpeed.
    """
    for filename in os.listdir(directory):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            filepath = os.path.join(directory, filename)
            img = Image.open(filepath)
            img.save(filepath, optimize=True, quality=quality)
            print(f"[OK] Optimized: {filename}")


if __name__ == "__main__":
    print("Neural Image Optimizer Active - Ready to boost your Core Web Vitals.")


def process_image(directory):
    if not os.path.isdir(directory):
        raise ValueError("Invalid directory path")
    directory = os.path.abspath(directory)
    # Continue with the rest of the function
