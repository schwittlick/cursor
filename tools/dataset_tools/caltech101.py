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
        export_img = np.ones((90, 126), dtype=np.uint8) * 255

        ann_file = os.path.join(self.base_ann_path, f"annotation_{self.current_index:04d}.mat")
        data = loadmat(ann_file)
        box_coord = data['box_coord'].flatten()
        obj_contour = data['obj_contour']

        img = np.array(PILImage.open(os.path.join(self.base_img_path, f"image_{self.current_index:04d}.jpg")))
        scale_x = 126 / img.shape[1]
        scale_y = 90 / img.shape[0]

        num_points = obj_contour.shape[1]
        contour_points = np.zeros((num_points, 2), dtype=np.int32)
        for i in range(num_points):
            x = int((obj_contour[0, i] + box_coord[2]) * scale_x)
            y = int((obj_contour[1, i] + box_coord[0]) * scale_y)
            contour_points[i] = [x, y]

        cv2.polylines(export_img,
                      [contour_points],
                      isClosed=True,
                      color=0,
                      thickness=1)

        category = self.selected_category.get().split(" (")[0]  # Get category name without count
        folder = DataDirHandler().png("datasets")
        output_path = folder / f"{category}_contour_{self.current_index:04d}.png"
        cv2.imwrite(str(output_path), export_img)
        print(f"Exported contour to: {output_path}")

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
        self.ax.imshow(img)

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
