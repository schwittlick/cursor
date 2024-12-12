import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.io import loadmat
from PIL import Image as PILImage
import os
import cv2
import tkinter as tk

from collection import Collection
from data import DataDirHandler
from device import PlotterType
from export import ExportWrapper
from path import Path
from timer import Timer

from dataset_tools.skeletonize_qt5 import skeletonize


class ImageAnnotationViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CALTECH-101 Image Annotation Viewer")

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
        tk.Button(self.root, text="Save Category Contours", command=self._save_contours).pack()

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

    def _save_contours(self, rotate_90=True):
        """
        These are the contours saved for e paper
        """
        category_info = self.categories_with_counts[self.selected_category.get()]
        category, count = category_info

        img_path = os.path.join(self.base_path, "101_ObjectCategories", category)
        ann_path = os.path.join(self.base_path, "Annotations", category)

        output_dir = os.path.join(self.base_path, "Contours", category)
        os.makedirs(output_dir, exist_ok=True)

        for i in range(1, count + 1):
            img_file = os.path.join(img_path, f"image_{i:04d}.jpg")
            ann_file = os.path.join(ann_path, f"annotation_{i:04d}.mat")

            if not os.path.exists(img_file) or not os.path.exists(ann_file):
                print(f"Skipping image {i} due to missing files.")
                continue

            data = loadmat(ann_file)
            obj_contour = data['obj_contour']

            if rotate_90:
                obj_contour = np.array([obj_contour[1], -obj_contour[0]])

            contour_img = np.ones((2560, 1440), dtype=np.uint8) * 255

            # Find contour bounds
            x_min, y_min = np.min(obj_contour, axis=1)
            x_max, y_max = np.max(obj_contour, axis=1)
            contour_width = x_max - x_min
            contour_height = y_max - y_min

            # Add padding (8% of the larger dimension)
            padding = int(0.08 * max(contour_width, contour_height))
            contour_width += 2 * padding
            contour_height += 2 * padding

            # Calculate scale to fit contour while maintaining aspect ratio
            scale_x = 1440 / contour_width
            scale_y = 2560 / contour_height
            scale = min(scale_x, scale_y)

            # Calculate padding to center the contour
            pad_x = int((1440 - contour_width * scale) / 2)
            pad_y = int((2560 - contour_height * scale) / 2)

            scaled_contour = np.zeros((obj_contour.shape[1], 2), dtype=np.int32)
            for j in range(obj_contour.shape[1]):
                scaled_contour[j] = [
                    int((obj_contour[0, j] - x_min + padding) * scale) + pad_x,
                    int((obj_contour[1, j] - y_min + padding) * scale) + pad_y
                ]

            # Interpolate points to ensure maximum distance of 400 pixels
            interpolated_contour = []
            for j in range(len(scaled_contour)):
                p1 = scaled_contour[j]
                p2 = scaled_contour[(j + 1) % len(scaled_contour)]
                interpolated_contour.append(p1)

                distance = np.linalg.norm(np.array(p2) - np.array(p1))
                if distance > 400:
                    num_points = int(np.ceil(distance / 400))
                    for k in range(1, num_points):
                        t = k / num_points
                        interp_point = (1 - t) * np.array(p1) + t * np.array(p2)
                        interpolated_contour.append(interp_point.astype(np.int32))

            interpolated_contour = np.array(interpolated_contour)

            cv2.drawContours(contour_img, [interpolated_contour], 0, 0, 1)

            output_file = os.path.join(output_dir, f"contour_{i:04d}.bmp")
            cv2.imwrite(output_file, contour_img)

            # Export CSV with absolute pixel coordinates
            csv_file = os.path.join(output_dir, f"contour_{i:04d}.csv")
            with open(csv_file, 'w') as f:
                for point in interpolated_contour:
                    f.write(f"{point[0]};{point[1]}\n")

        print(f"Saved {count} contour images and CSV files for category '{category}' in {output_dir}")

    def export_contour(self):
        def convert_contour_to_path(contour):
            path = []
            for point in contour:
                path.append((float(point[0]), float(point[1])))
            return path

        def calc_should_rotate(contours):
            path = Path()
            for i in range(contours.shape[1]):
                x = contours[0, i]
                y = contours[1, i]
                path.add(float(x), float(y))

            path_bb = path.bb()
            # we change the rotation depending on format grml
            if path_bb.w < path_bb.h:
                return True
            return False

        OUTLINE_WIDTH, OUTLINE_HEIGHT = 126, 84#126, 174
        # change outline manually here
        OUTLINE_MARGIN = 4

        A6_MULT = 0.5
        A5_MULT = 1
        A4_MULT = 2
        A3_MULT = 4
        format_multiplier = A4_MULT

        OUTPUT_WIDTH = int(OUTLINE_WIDTH * format_multiplier)
        OUTPUT_HEIGHT = int(OUTLINE_HEIGHT * format_multiplier)
        MARGIN = int(OUTLINE_MARGIN * format_multiplier)

        export_img_outline = np.ones((OUTLINE_HEIGHT, OUTLINE_WIDTH), dtype=np.uint8) * 255
        export_img_filled = np.ones((OUTLINE_HEIGHT, OUTLINE_WIDTH), dtype=np.uint8) * 255
        export_img_original = np.ones((OUTPUT_HEIGHT, OUTPUT_WIDTH, 3), dtype=np.uint8) * 255

        # Load and rotate image
        img = np.array(PILImage.open(os.path.join(self.base_img_path, f"image_{self.current_index:04d}.jpg")))
        img = cv2.rotate(img, cv2.ROTATE_180)  # Initial 180-degree rotation from original code

        ann_file = os.path.join(self.base_ann_path, f"annotation_{self.current_index:04d}.mat")
        data = loadmat(ann_file)
        box_coord = data['box_coord'].flatten()
        obj_contour = data['obj_contour']

        # Check if height > width and rotate if needed
        # should_rotate = img.shape[0] > img.shape[1]
        should_rotate = calc_should_rotate(obj_contour)
        if should_rotate:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

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

        # Scale contour for outline and filled versions (126x84)
        scale_x = (OUTLINE_WIDTH - 2 * OUTLINE_MARGIN) / (xmax - xmin)
        scale_y = (OUTLINE_HEIGHT - 2 * OUTLINE_MARGIN) / (ymax - ymin)
        scale = min(scale_x, scale_y)

        scaled_width = int((xmax - xmin) * scale)
        scaled_height = int((ymax - ymin) * scale)
        x_offset = int((OUTLINE_WIDTH - scaled_width) / 2)
        y_offset = int((OUTLINE_HEIGHT - scaled_height) / 2)

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

        # Scale for original image (OUTPUT_WIDTH x OUTPUT_HEIGHT)
        scale_x_orig = (OUTPUT_WIDTH - 2 * MARGIN) / (xmax - xmin)
        scale_y_orig = (OUTPUT_HEIGHT - 2 * MARGIN) / (ymax - ymin)
        scale_orig = min(scale_x_orig, scale_y_orig)

        scaled_width_orig = int((xmax - xmin) * scale_orig)
        scaled_height_orig = int((ymax - ymin) * scale_orig)
        x_offset_orig = int((OUTPUT_WIDTH - scaled_width_orig) / 2)
        y_offset_orig = int((OUTPUT_HEIGHT - scaled_height_orig) / 2)

        # Scale masked region and mask for final image
        masked_region_resized = cv2.resize(masked_region, (scaled_width_orig, scaled_height_orig))
        mask_resized = cv2.resize(mask_region, (scaled_width_orig, scaled_height_orig))

        # Apply mask to maintain white background
        region_slice = export_img_original[y_offset_orig:y_offset_orig + scaled_height_orig,
                       x_offset_orig:x_offset_orig + scaled_width_orig]
        region_slice[mask_resized > 0] = masked_region_resized[mask_resized > 0]
        export_img_original[y_offset_orig:y_offset_orig + scaled_height_orig,
        x_offset_orig:x_offset_orig + scaled_width_orig] = region_slice

        category = self.selected_category.get().split(" (")[0]
        folder = DataDirHandler().png("datasets")

        output_path_outline = folder / f"{category}_contour_outline_{self.current_index:04d}_{Timer.timestamp()}.png"
        output_path_filled = folder / f"{category}_contour_filled_{self.current_index:04d}_{Timer.timestamp()}.png"
        output_path_original = folder / f"{category}_contour_original_{self.current_index:04d}_{Timer.timestamp()}.png"

        cv2.imwrite(str(output_path_outline), export_img_outline)
        cv2.imwrite(str(output_path_filled), export_img_filled)
        cv2.imwrite(str(output_path_original), cv2.cvtColor(export_img_original, cv2.COLOR_RGB2BGR))

        # Apply skeletonization to the filled outline image
        skeleton = skeletonize(255 - export_img_filled)

        # Create a colored skeleton image for visualization
        skeleton_color = cv2.cvtColor(skeleton.astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)

        inverted_skeleton = cv2.bitwise_not(skeleton_color)

        # Save the inverted skeletonized image
        output_path_skeleton = folder / f"{category}_contour_skeleton_{self.current_index:04d}_{Timer.timestamp()}.png"
        cv2.imwrite(str(output_path_skeleton), inverted_skeleton)

        # Create a side-by-side comparison image with the inverted skeleton
        comparison_image = np.hstack((cv2.cvtColor(export_img_filled, cv2.COLOR_GRAY2BGR), inverted_skeleton))
        output_path_comparison = folder / f"{category}_contour_comparison_{self.current_index:04d}_{Timer.timestamp()}.png"
        cv2.imwrite(str(output_path_comparison), comparison_image)
        print(f"  Comparison: {output_path_comparison}")

        path = convert_contour_to_path(orig_contour)
        coll = Collection.from_tuples([path])

        fname = f"{category}_grog_outline_{Timer.timestamp()}"
        wrapper = ExportWrapper(
            coll,
            PlotterType.DIY_PLOTTER_60x60,
            10,  # 25mm - 11mm
            "datasets",
            fname,
            keep_aspect_ratio=True)
        wrapper.fit()
        wrapper.ex()

        fname2 = f"{category}_grog_outline_{Timer.timestamp()}"
        wrapper2 = ExportWrapper(
            coll,
            PlotterType.ROLAND_DXY1200_A3,
            10,  # 25mm - 11mm
            "datasets",
            fname2,
            keep_aspect_ratio=True)
        wrapper2.fit()
        wrapper2.ex()

        print(f"Exported contours to:")
        print(f"  Outline: {output_path_outline}")
        print(f"  Filled: {output_path_filled}")
        print(f"  Original: {output_path_original}")
        print(f"  Skeleton: {output_path_skeleton}")
        print(f"  Grog outline: {fname}")
        print(f"  HPGL outline: {fname2}")

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
