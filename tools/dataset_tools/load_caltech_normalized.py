import json
import pathlib

import numpy as np
import matplotlib.pyplot as plt
import cv2


class ContourLoader:
    def __init__(self, json_path):
        """
        Initialize with path to the JSON file containing normalized contour data
        """
        with open(json_path, 'r') as f:
            self.data = json.load(f)

        # Extract basic information
        self.points = np.array(self.data['points'])
        self.original_width = self.data['original_width']
        self.original_height = self.data['original_height']

    def get_denormalized_points(self):
        """
        Convert normalized points back to original scale
        """
        max_dim = max(self.original_width, self.original_height)
        denorm_points = self.points * max_dim

        # Ensure points are correctly formatted for OpenCV
        return denorm_points.astype(np.int32).reshape((-1, 1, 2))

    def draw_matplotlib(self, block=False):
        """
        Draw the contour using matplotlib
        Parameters:
            block (bool): If True, blocks execution until window is closed
        """
        points = self.get_denormalized_points().reshape(-1, 2)

        # Create figure with original aspect ratio
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw the contour
        ax.plot(points[:, 0], points[:, 1], 'b-', linewidth=2)
        ax.fill(points[:, 0], points[:, 1], alpha=0.3)  # Optional: fill the contour

        # Set limits and aspect ratio
        ax.set_xlim(0, self.original_width)
        ax.set_ylim(0, self.original_height)
        ax.set_aspect('equal')

        # Set title and labels
        ax.set_title(f'Contour (Original dimensions: {self.original_width:.1f} x {self.original_height:.1f})')
        ax.grid(True)

        plt.show(block=block)
        return fig, ax

    def draw_opencv(self, background_color=(255, 255, 255), line_color=(0, 0, 255)):
        """
        Draw the contour using OpenCV
        Returns the image for further processing if needed
        """
        # Create image with original dimensions (ensure integers)
        height = int(np.ceil(self.original_height))
        width = int(np.ceil(self.original_width))
        img = np.ones((height, width, 3), dtype=np.uint8)
        img[:] = background_color

        # Get denormalized points (already in correct format for OpenCV)
        points = self.get_denormalized_points()

        # Draw the contour
        cv2.polylines(img, [points], True, line_color, 2)
        cv2.fillPoly(img, [points], (255, 240, 240))  # Light fill

        return img

    @classmethod
    def load_collection(cls, collection_path):
        """
        Load all contours from a collection file
        Returns list of ContourLoader instances
        """
        with open(collection_path, 'r') as f:
            collection = json.load(f)

        contours = []
        for contour_data in collection['contours']:
            # Create a temporary file-like object in memory
            loader = cls.__new__(cls)
            loader.data = contour_data
            loader.points = np.array(contour_data['points'])
            loader.original_width = contour_data['original_width']
            loader.original_height = contour_data['original_height']
            contours.append(loader)

        return contours

    @classmethod
    def draw_collection_grid(cls, contours, figsize=(20, 20), cols=4, block=False):
        """
        Draw all contours in a grid layout
        Parameters:
            contours: List of ContourLoader instances
            figsize: Figure size (width, height) in inches
            cols: Number of columns in the grid
            block: If True, blocks execution until window is closed
        """
        # Calculate number of rows needed
        rows = int(np.ceil(len(contours) / cols))

        # Create figure and axes grid
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        if rows == 1:
            axes = axes.reshape(1, -1)
        axes = axes.flatten()

        # Plot each contour
        for i, contour in enumerate(contours):
            if i < len(axes):
                points = contour.get_denormalized_points().reshape(-1, 2)
                axes[i].plot(points[:, 0], points[:, 1], 'b-', linewidth=1)
                axes[i].fill(points[:, 0], points[:, 1], alpha=0.1)
                axes[i].set_aspect('equal')
                axes[i].set_title(f'Contour {contour.data["index"]}')
                axes[i].grid(True, linestyle='--', alpha=0.3)

        # Hide empty subplots
        for i in range(len(contours), len(axes)):
            axes[i].axis('off')

        plt.tight_layout()
        plt.show(block=block)
        return fig, axes

    @classmethod
    def draw_collection_overlay(cls, contours, figsize=(10, 10), block=False, colors=None):
        """
        Draw all contours overlaid on the same canvas
        Parameters:
            contours: List of ContourLoader instances
            figsize: Figure size (width, height) in inches
            block: If True, blocks execution until window is closed
            colors: List of colors for contours (if None, uses default colormap)
        """
        fig, ax = plt.subplots(figsize=figsize)

        # If no colors specified, use a colormap
        if colors is None:
            colors = plt.cm.rainbow(np.linspace(0, 1, len(contours)))

        # Find the maximum dimensions to scale all contours
        max_width = max(c.original_width for c in contours)
        max_height = max(c.original_height for c in contours)

        # Plot each contour
        for i, contour in enumerate(contours):
            points = contour.get_denormalized_points().reshape(-1, 2)
            ax.plot(points[:, 0], points[:, 1], '-', color=colors[i], linewidth=1, alpha=0.7,
                    label=f'Contour {contour.data["index"]}')
            ax.fill(points[:, 0], points[:, 1], color=colors[i], alpha=0.1)

        ax.set_xlim(-0.05 * max_width, 1.05 * max_width)
        ax.set_ylim(-0.05 * max_height, 1.05 * max_height)
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.show(block=block)
        return fig, ax

    @classmethod
    def draw_collection_opencv(cls, contours, background_color=(255, 255, 255)):
        """
        Draw all contours using OpenCV
        Parameters:
            contours: List of ContourLoader instances
            background_color: Background color for the image
        Returns:
            OpenCV image with all contours drawn
        """
        # Find the maximum dimensions to scale all contours
        max_width = int(np.ceil(max(c.original_width for c in contours)))
        max_height = int(np.ceil(max(c.original_height for c in contours)))

        # Create image
        img = np.ones((max_height, max_width, 3), dtype=np.uint8)
        img[:] = background_color

        # Generate colors for contours
        colors = []
        for i in range(len(contours)):
            hue = int(180 * i / len(contours))
            color = tuple(int(x) for x in cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2BGR)[0][0])
            colors.append(color)

        # Draw each contour
        for contour, color in zip(contours, colors):
            points = contour.get_denormalized_points()
            cv2.polylines(img, [points], True, color, 2)

            # Create a mask for filling
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [points], 255)

            # Create colored overlay with alpha
            overlay = img.copy()
            overlay[mask > 0] = color

            # Blend with alpha
            alpha = 0.1
            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        return img


# Example usage:
if __name__ == "__main__":
    base_path = pathlib.Path("E:\\Datasets\\caltech-101\\NormalizedContours\\rhino")

    print("Demonstrating single contour visualization...")
    contour_path = base_path / "normalized_contour_0001.json"
    loader = ContourLoader(contour_path)

    # Display using matplotlib
    loader.draw_matplotlib(block=False)
    plt.pause(0.1)

    # Example with collection
    print("\nDemonstrating collection visualization...")
    collection_path = base_path / "rhino_normalized_contours.json"
    contours = ContourLoader.load_collection(collection_path)

    # 1. Grid layout (non-blocking)
    ContourLoader.draw_collection_grid(contours, figsize=(15, 15), cols=4, block=False)
    plt.pause(0.1)

    # 2. Overlay layout (non-blocking)
    ContourLoader.draw_collection_overlay(contours, figsize=(10, 10), block=False)
    plt.pause(0.1)

    # 3. OpenCV visualization
    img = ContourLoader.draw_collection_opencv(contours)
    cv2.namedWindow('Contours Collection', cv2.WINDOW_NORMAL)
    cv2.imshow('Contours Collection', img)

    print("\nPress 'q' to quit OpenCV window")
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    plt.close('all')
