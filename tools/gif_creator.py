from PIL import Image
import os


def create_gif(image_folder, output_name="output.gif", duration=500, size=(1500, 1500)):
    """
    Create an optimized GIF from all images in a folder.

    Parameters:
    image_folder (str): Path to folder containing images
    output_name (str): Name of output GIF file
    duration (int): Duration for each frame in milliseconds
    size (tuple): Target size for images (width, height)
    """
    # Get list of image files
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    image_files.sort()  # Sort files to ensure consistent order

    # Open and process all images
    images = []
    for image_file in image_files:
        file_path = os.path.join(image_folder, image_file)
        img = Image.open(file_path)

        # Convert to RGB mode if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Resize image
        img = img.resize(size, Image.Resampling.LANCZOS)

        # Convert to P mode (palette) with maximum 256 colors for optimization
        img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)

        images.append(img)

    # Save the optimized GIF
    if images:
        images[0].save(
            output_name,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0,
            optimize=True,  # Enable GIF optimization
            quality=70,  # Lower quality for smaller file size
            disposal=2,  # Clear each frame before rendering next
        )
        print(f"GIF created successfully: {output_name}")

        # Print file size
        file_size = os.path.getsize(output_name) / (1024 * 1024)  # Convert to MB
        print(f"File size: {file_size:.2f} MB")
    else:
        print("No images found in the specified folder")


# Usage example
if __name__ == "__main__":
    create_gif(
        image_folder="C:\\Users\\schwittlick\\Dropbox\\0_MARCELSCHWITTLICK\\2025_C93_SEGMENTATION\\grog\\fin",
        output_name="animation2.gif",
        duration=500,  # 500ms per frame
        size=(1500, 1500),  # Target size for all frames
    )
