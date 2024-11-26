import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.io import loadmat
from PIL import Image as PILImage
import os
import cv2
from tkinter import *
import tkinter as tk
from data import DataDirHandler
from timer import Timer


class ImageAnnotationViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Category Selection")

        # Get all categories
        self.base_path = "E:\\Datasets\\caltech-101"
        categories = self._get_categories()
        self.categories_with_counts = self._count_images(categories)

        # Create dropdown
        self.selected_category = tk.StringVar()
        self.dropdown = tk.OptionMenu(self.root, self.selected_category, *self.categories_with_counts.keys())
        self.dropdown.pack()

        # Create button to load viewer
        tk.Button(self.root, text="Load Category", command=self._load_viewer).pack()

        self.root.mainloop()

    def _get_categories(self):
        img_path = os.path.join(self.base_path, "101_ObjectCategories")
        ann_path = os.path.join(self.base_path, "Annotations")
        categories = []
        for folder in os.listdir(img_path):
            if os.path.isdir(os.path.join(img_path, folder)) and os.path.exists(os.path.join(ann_path, folder)):
                categories.append(folder)
        return categories

    def _count_images(self, categories):
        counts = {}
        for category in categories:
            img_path = os.path.join(self.base_path, "101_ObjectCategories", category)
            count = len([f for f in os.listdir(img_path) if f.endswith('.jpg')])
            counts[f"{category} ({count} images)"] = (category, count)
        return counts

    def _load_viewer(self):
        category_info = self.categories_with_counts[self.selected_category.get()]
        category, count = category_info

        self.base_img_path = os.path.join(self.base_path, "101_ObjectCategories", category)
        self.base_ann_path = os.path.join(self.base_path, "Annotations", category)

        self.current_index = 1
        self.max_index = count

        self.fig, self.ax = plt.subplots()
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.update_display()
        plt.show()

    def export_contour(self):
        OUTPUT_WIDTH = 126 * 2
        OUTPUT_HEIGHT = 84 * 2
        MARGIN = 5 * 2

        export_img_outline = np.ones((OUTPUT_HEIGHT, OUTPUT_WIDTH), dtype=np.uint8) * 255
        export_img_filled = np.ones((OUTPUT_HEIGHT, OUTPUT_WIDTH), dtype=np.uint8) * 255
        export_img_original = np.ones((OUTPUT_HEIGHT, OUTPUT_WIDTH, 3), dtype=np.uint8) * 255

        # Load and rotate image
        img = np.array(PILImage.open(os.path.join(self.base_img_path, f"image_{self.current_index:04d}.jpg")))
        img = cv2.rotate(img, cv2.ROTATE_180)  # Initial 180-degree rotation from original code

        # Check if height > width and rotate if needed
        should_rotate = img.shape[0] > img.shape[1]
        if should_rotate:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        ann_file = os.path.join(self.base_ann_path, f"annotation_{self.current_index:04d}.mat")
        data = loadmat(ann_file)
        box_coord = data['box_coord'].flatten()
        obj_contour = data['obj_contour']

        orig_contour = np.zeros((obj_contour.shape[1], 2), dtype=np.int32)
        for i in range(obj_contour.shape[1]):
            if should_rotate:
                # For 90-degree rotation: (x,y) -> (y, height-x)
                orig_contour[i] = [
                    img.shape[1] - (obj_contour[1, i] + box_coord[0]),  # y becomes x
                    obj_contour[0, i] + box_coord[2]  # x becomes y
                ]
            else:
                orig_contour[i] = [
                    img.shape[1] - (obj_contour[0, i] + box_coord[2]),
                    img.shape[0] - (obj_contour[1, i] + box_coord[0])
                ]

        # Create binary mask from original contour
        orig_mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.fillPoly(orig_mask, [orig_contour], color=255)

        # Extract masked region from original image
        masked_img = cv2.bitwise_and(img, img, mask=orig_mask)

        # Get bounds for the non-zero region
        rows = np.any(orig_mask, axis=1)
        cols = np.any(orig_mask, axis=0)
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]

        # Extract the masked regions
        masked_region = masked_img[ymin:ymax + 1, xmin:xmax + 1]
        mask_region = orig_mask[ymin:ymax + 1, xmin:xmax + 1]

        # Scale contour for outline and filled versions
        scale_x = (OUTPUT_WIDTH - 2 * MARGIN) / (xmax - xmin)
        scale_y = (OUTPUT_HEIGHT - 2 * MARGIN) / (ymax - ymin)
        scale = min(scale_x, scale_y)

        scaled_width = int((xmax - xmin) * scale)
        scaled_height = int((ymax - ymin) * scale)
        x_offset = int((OUTPUT_WIDTH - scaled_width) / 2)
        y_offset = int((OUTPUT_HEIGHT - scaled_height) / 2)

        # Create scaled contour points for outline/filled versions
        scaled_contour = np.zeros((obj_contour.shape[1], 2), dtype=np.int32)
        for i in range(obj_contour.shape[1]):
            x = orig_contour[i][0] - xmin
            y = orig_contour[i][1] - ymin
            scaled_contour[i] = [
                int(x * scale) + x_offset,
                int(y * scale) + y_offset
            ]

        cv2.polylines(export_img_outline, [scaled_contour], isClosed=True, color=0, thickness=1)
        cv2.fillPoly(export_img_filled, [scaled_contour], color=0)

        # Scale masked region and mask for final image
        masked_region_resized = cv2.resize(masked_region, (scaled_width, scaled_height))
        mask_resized = cv2.resize(mask_region, (scaled_width, scaled_height))

        # Apply mask to maintain white background
        region_slice = export_img_original[y_offset:y_offset + scaled_height, x_offset:x_offset + scaled_width]
        region_slice[mask_resized > 0] = masked_region_resized[mask_resized > 0]
        export_img_original[y_offset:y_offset + scaled_height, x_offset:x_offset + scaled_width] = region_slice

        category = self.selected_category.get().split(" (")[0]
        folder = DataDirHandler().png("datasets")

        output_path_outline = folder / f"{category}_contour_outline_{self.current_index:04d}_{Timer.timestamp()}.png"
        output_path_filled = folder / f"{category}_contour_filled_{self.current_index:04d}_{Timer.timestamp()}.png"
        output_path_original = folder / f"{category}_contour_original_{self.current_index:04d}_{Timer.timestamp()}.png"

        cv2.imwrite(str(output_path_outline), export_img_outline)
        cv2.imwrite(str(output_path_filled), export_img_filled)
        cv2.imwrite(str(output_path_original), cv2.cvtColor(export_img_original, cv2.COLOR_RGB2BGR))

        print(f"Exported contours to:")
        print(f"  Outline: {output_path_outline}")
        print(f"  Filled: {output_path_filled}")
        print(f"  Original: {output_path_original}")

    def on_key_press(self, event):
        if event.key == 'e':
            self.export_contour()

    def on_scroll(self, event):
        if event.button == 'up':
            self.current_index = min(self.current_index + 1, self.max_index)
        else:
            self.current_index = max(self.current_index - 1, 1)
        self.update_display()

    def update_display(self):
        self.ax.clear()

        img_file = os.path.join(self.base_img_path, f"image_{self.current_index:04d}.jpg")
        ann_file = os.path.join(self.base_ann_path, f"annotation_{self.current_index:04d}.mat")

        if not os.path.exists(img_file) or not os.path.exists(ann_file):
            self.ax.text(0.5, 0.5, f'Files not found for index {self.current_index}',
                         ha='center', va='center')
            self.fig.canvas.draw_idle()
            return

        data = loadmat(ann_file)
        box_coord = data['box_coord'].flatten()
        obj_contour = data['obj_contour']

        img = np.array(PILImage.open(img_file))
        img = np.rot90(img, k=2)
        self.ax.imshow(img, origin='lower')  # Set origin to 'lower' for bottom-left (0,0)

        if len(img.shape) < 3:
            plt.gray()

        box = Rectangle(
            (img.shape[1] - box_coord[3], img.shape[0] - box_coord[1]),
            box_coord[3] - box_coord[2],
            box_coord[1] - box_coord[0],
            edgecolor='yellow',
            linewidth=5,
            fill=False
        )
        self.ax.add_patch(box)

        contour_x = img.shape[1] - (obj_contour[0] + box_coord[2])
        contour_y = img.shape[0] - (obj_contour[1] + box_coord[0])

        for i in range(obj_contour.shape[1] - 1):
            self.ax.plot(
                [contour_x[i], contour_x[i + 1]],
                [contour_y[i], contour_y[i + 1]],
                'r-',
                linewidth=4
            )

        self.ax.plot(
            [contour_x[-1], contour_x[0]],
            [contour_y[-1], contour_y[0]],
            'r-',
            linewidth=4
        )

        self.ax.set_title(f'{self.selected_category.get()} - Image {self.current_index}')
        self.ax.axis('image')
        self.fig.canvas.draw_idle()


if __name__ == '__main__':
    viewer = ImageAnnotationViewer()
