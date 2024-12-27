import math
import random

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image as PILImage
import cv2
import tkinter as tk
import json
import os
import numpy as np
from scipy.io import loadmat

from skimage.util import img_as_ubyte
from skimage.morphology import skeletonize as sk_skeletonize

from cursor.algorithm.color.copic import Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorGroup
from cursor.algorithm.color.lib import sort_collection_by_copic_color_group
from cursor import Collection
from cursor import Path

from cursor.data import DataDirHandler
from cursor.device import PlotterType, MinmaxMapping
from cursor.export import ExportWrapper
from cursor.timer import Timer

from skeletonize_lib import skeleton_to_vectors
from skeletonize_qt5 import skeletonize


class ImageAnnotationViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CALTECH-101 Image Annotation Viewer")

        # Get all categories
        self.base_path = "/home/marcel/38c3/caltech-101/"
        categories = self._get_categories()
        self.categories_with_counts = self._count_images(categories)

        # Create dropdown
        self.selected_category = tk.StringVar()
        self.dropdown = tk.OptionMenu(self.root, self.selected_category, *self.categories_with_counts.keys())
        self.dropdown.pack()

        # Create button to load viewer
        tk.Button(self.root, text="Load Category", command=self._load_viewer).pack()
        tk.Button(self.root, text="Save Category Contours", command=self._save_contours).pack()
        tk.Button(self.root, text="Export overview", command=self._save_overview).pack()
        tk.Button(self.root, text="Export skeleton overview", command=self._save_skeleton_overview).pack()
        tk.Button(self.root, text="Export Normalized Contours", command=self._export_normalized_contours).pack()
        tk.Button(self.root, text="Export Skeleton Grid", command=self._export_skeleton_grid).pack()
        self.root.mainloop()

    def _export_skeleton_grid(self):
        category_info = self.categories_with_counts[self.selected_category.get()]
        category, count = category_info

        # Calculate grid dimensions
        grid_size = math.ceil(math.sqrt(count))

        # Create a large canvas for the grid
        canvas_size = 126  # Size of each image in the grid
        canvas = np.zeros((canvas_size * grid_size, canvas_size * grid_size)) * 255

        # Compute contours for the category
        all_contours = self._compute_contours(category, count, rotate_90=False, target_width=canvas_size,
                                              target_height=canvas_size)

        for i, contour in enumerate(all_contours):
            # Create a blank image for the contour
            img = np.zeros((canvas_size, canvas_size), dtype=np.uint8)

            # Draw the filled contour
            cv2.drawContours(img, [contour], 0, 255, -1)

            # Create skeleton
            skeleton = sk_skeletonize(img > 0)

            # Resize skeleton to fit in the grid
            resized_skeleton = cv2.resize(skeleton.astype(np.uint8) * 255, (canvas_size, canvas_size),
                                          interpolation=cv2.INTER_NEAREST)

            # Calculate position in the grid
            row = i // grid_size
            col = i % grid_size

            # Place the skeleton in the canvas
            canvas[row * canvas_size:(row + 1) * canvas_size,
            col * canvas_size:(col + 1) * canvas_size] = resized_skeleton
            print(f"Skeleton saved to grid position ({row}, {col})")

        # Save the grid image
        output_dir = DataDirHandler().png("datasets")
        output_file = os.path.join(output_dir, f"{category}_skeleton_grid_{Timer.timestamp()}.png")
        cv2.imwrite(output_file, canvas)
        print(f"Skeleton grid saved to: {output_file}")

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

    def _compute_contours(self, category, count, rotate_90=True, target_width=1440, target_height=2560):
        img_path = os.path.join(self.base_path, "101_ObjectCategories", category)
        ann_path = os.path.join(self.base_path, "Annotations", category)
        all_contours = []

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

            # Find contour bounds
            x_min, y_min = np.min(obj_contour, axis=1)
            x_max, y_max = np.max(obj_contour, axis=1)

            contour_width = x_max - x_min
            contour_height = y_max - y_min

            # Add padding (8% of the larger dimension)
            random_padding = random.uniform(0.04, 0.08)
            padding = int(random_padding * max(contour_width, contour_height))
            padded_width = contour_width + 2 * padding
            padded_height = contour_height + 2 * padding

            # Calculate scale to fit contour while maintaining aspect ratio
            scale_x = target_width / padded_width
            scale_y = target_height / padded_height
            scale = min(scale_x, scale_y)

            # Calculate padding to center the contour
            pad_x = int((target_width - padded_width * scale) / 2)
            pad_y = int((target_height - padded_height * scale) / 2)

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

            # Flip the contour horizontally (left/right axis)
            interpolated_contour[:, 0] = target_width - interpolated_contour[:, 0]

            all_contours.append(interpolated_contour)

        return all_contours

    def _export_normalized_contours(self):
        """
        Exports all contours from the selected category in a normalized format (coordinates between 0.0 and 1.0).
        Maintains original aspect ratio and saves contours without padding.
        Saves the results as JSON files containing normalized coordinates and metadata.
        """

        category_info = self.categories_with_counts[self.selected_category.get()]
        category, count = category_info

        # Create output directory
        output_dir = os.path.join(self.base_path, "NormalizedContours", category)
        os.makedirs(output_dir, exist_ok=True)

        all_contours = []

        for i in range(1, count + 1):
            # Load annotation file
            ann_file = os.path.join(self.base_ann_path, f"annotation_{i:04d}.mat")
            if not os.path.exists(ann_file):
                print(f"Skipping image {i} due to missing annotation file.")
                continue

            try:
                # Load contour data
                data = loadmat(ann_file)
                obj_contour = data['obj_contour']

                # Convert to numpy array of points
                points = np.array([obj_contour[0], obj_contour[1]]).T

                # Find min and max values for normalization
                min_vals = np.min(points, axis=0)
                max_vals = np.max(points, axis=0)

                # Calculate ranges
                ranges = max_vals - min_vals

                # Normalize points to 0-1 range while preserving aspect ratio
                max_range = np.max(ranges)
                normalized_points = (points - min_vals) / max_range

                # Convert to list of [x, y] coordinates
                contour_data = {
                    'points': normalized_points.tolist(),
                    'original_width': float(ranges[0]),
                    'original_height': float(ranges[1]),
                    'aspect_ratio': float(ranges[1] / ranges[0]),
                    'index': i
                }

                # Save individual contour file
                output_file = os.path.join(output_dir, f"normalized_contour_{i:04d}.json")
                with open(output_file, 'w') as f:
                    json.dump(contour_data, f, indent=2)

                all_contours.append(contour_data)

            except Exception as e:
                print(f"Error processing image {i}: {str(e)}")
                continue

        # Save collection file with all contours
        collection_file = os.path.join(output_dir, f"{category}_normalized_contours.json")
        collection_data = {
            'category': category,
            'count': len(all_contours),
            'contours': all_contours
        }

        with open(collection_file, 'w') as f:
            json.dump(collection_data, f, indent=2)

        print(f"Exported {len(all_contours)} normalized contours for category '{category}'")
        print(f"Collection file saved to: {collection_file}")

        return collection_data

    def _save_contours(self, rotate_90=True):
        category_info = self.categories_with_counts[self.selected_category.get()]
        category, count = category_info

        output_dir = os.path.join(self.base_path, "Contours", category)
        output_dir_png = os.path.join(self.base_path, "Contours", f"{category}_png")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(output_dir_png, exist_ok=True)

        if category == "flamingo":
            rotate_90 = False

        all_contours = self._compute_contours(category, count, rotate_90)

        for i, contour in enumerate(all_contours, 1):
            contour_img = np.ones((2560, 1440), dtype=np.uint8) * 255
            cv2.drawContours(contour_img, [contour], 0, 0, 1)

            output_file = os.path.join(output_dir, f"contour_{i:04d}.bmp")
            cv2.imwrite(output_file, contour_img)

            # Export CSV with absolute pixel coordinates
            csv_file = os.path.join(output_dir, f"contour_{i:04d}.csv")
            with open(csv_file, 'w') as f:
                for point in contour:
                    f.write(f"{point[0]};{point[1]}\n")

            output_file_png = os.path.join(output_dir_png, f"contour_{i:04d}.png")
            cv2.imwrite(output_file_png, contour_img)

            # Export CSV with absolute pixel coordinates
            csv_file = os.path.join(output_dir_png, f"contour_{i:04d}.csv")
            with open(csv_file, 'w') as f:
                for point in contour:
                    f.write(f"{point[0]};{point[1]}\n")

        print(f"Saved {count} contour images and CSV files for category '{category}' in {output_dir}")

    def _save_overview(self, rotate_90=True):
        category_info = self.categories_with_counts[self.selected_category.get()]
        category, count = category_info

        output_dir = os.path.join(self.base_path, "Contours", category)
        os.makedirs(output_dir, exist_ok=True)

        all_contours = self._compute_contours(category, count, rotate_90)

        overview_collection = Collection()
        for idx, contour in enumerate(all_contours):
            pa = Path.from_array(contour)
            pa.pen_select = 1  # idx + 1
            pa.velocity = 20
            color_group = Copic().get_colors_by_group(CopicColorGroup.Y)
            color = color_group[idx % len(color_group)]  # pick color from the color group for each contour
            pa.properties["copic_color"] = Copic().color_by_code(color)
            overview_collection.add(pa)
        overview_collection.rot(math.radians(90))
        # overview_collection = sort_collection_by_copic_color_group(overview_collection, legende_scale=1)

        wrapper2 = ExportWrapper(
            overview_collection,
            PlotterType.HP_7550A_A3,
            20,  # 25mm - 11mm
            "datasets",
            f"overview_contours_{category}",
            keep_aspect_ratio=True,
            export_jpg_preview=True)
        wrapper2.fit()
        wrapper2.ex()

    def _save_skeleton_overview(self, rotate_90=True):
        category_info = self.categories_with_counts[self.selected_category.get()]
        category, count = category_info

        output_dir = os.path.join(self.base_path, "Skeletons", category)
        os.makedirs(output_dir, exist_ok=True)

        all_skeletons = Collection()

        for i in range(1, count - 1):
            # Load image
            img_path = os.path.join(self.base_img_path, f"image_{i:04d}.jpg")
            img = cv2.imread(img_path)

            # Rotate image if needed
            if rotate_90:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

            # Get contour
            ann_file = os.path.join(self.base_ann_path, f"annotation_{i:04d}.mat")
            data = loadmat(ann_file)
            obj_contour = data['obj_contour']

            # Create scaled contour
            height, width = img.shape[:2]
            orig_contour = np.zeros((obj_contour.shape[1], 2), dtype=np.int32)
            for j in range(obj_contour.shape[1]):
                orig_contour[j] = [obj_contour[0, j], obj_contour[1, j]]

            # Get bounds for the contour
            xmin, ymin = np.min(orig_contour, axis=0)
            xmax, ymax = np.max(orig_contour, axis=0)

            # Calculate scale to fit contour
            scale_x = width / (xmax - xmin)
            scale_y = height / (ymax - ymin)
            scale = min(scale_x, scale_y)

            # Calculate offsets to center the contour
            x_offset = int((width - (xmax - xmin) * scale) / 2)
            y_offset = int((height - (ymax - ymin) * scale) / 2)

            # Create scaled contour
            scaled_contour = self.construct_scaled_contour(orig_contour, xmin, ymin, scale, x_offset, y_offset)

            # Create filled outline image
            filled_outline = self.generate_filled_outline(scaled_contour, width, height)
            filled_outline_resized = cv2.resize(filled_outline, (width * 2, height * 2),
                                                interpolation=cv2.INTER_NEAREST)

            # Skeletonize
            skeleton = skeletonize(255 - filled_outline_resized)

            # Convert skeleton to uint8
            skeleton_uint8 = img_as_ubyte(skeleton)

            # Convert skeleton to vectors
            skeleton_vectors = skeleton_to_vectors(skeleton_uint8)

            # Create paths from vectors and add to collection
            group = Collection()
            for vector in skeleton_vectors:
                path = Path()
                for point in vector:
                    path.add(float(point[1]), float(point[0]))  # Swap x and y coordinates

                group.add(path)

            random_placement = False
            if random_placement:
                bb = MinmaxMapping.maps[PlotterType.HP_DM_RX_PLUS_A1]
                padding = 200
                max_x = bb.x2 - group.bb().w - padding
                max_y = bb.y2 - group.bb().h - padding
                random_x = random.uniform(bb.x + padding, max_x)
                random_y = random.uniform(bb.y + padding, max_y)
                group.move_to_origin()
                group.translate(-group.bb().w / 2, -group.bb().h / 2)
                group.scale(10, 10)
                group.translate(random_x, random_y)
            else:
                bb = MinmaxMapping.maps[PlotterType.HP_DM_RX_PLUS_A1]
                group.transform(bb)  # Fit to unit bounding box

            for path in group:
                path.pen_select = (i % 8) + 1  # Use image index as pen selection
                path.velocity = 20
                all_skeletons.add(path)

            # Save individual skeleton image (optional)
            skeleton_img_path = os.path.join(output_dir, f"skeleton_{i:04d}.png")
            cv2.imwrite(skeleton_img_path, skeleton_uint8)

        # Process the collection of all skeletons
        # all_skeletons.rot(math.radians(90))  # Rotate 90 degrees
        # all_skeletons.fit(BoundingBox(0, 0, 1, 1))  # Fit to unit bounding box

        # Export the collection
        wrapper = ExportWrapper(
            all_skeletons,
            PlotterType.HP_DM_RX_PLUS_A1,
            10,  # 25mm - 11mm
            "datasets",
            f"overview_skeletons_{category}",
            keep_aspect_ratio=True
        )
        wrapper.fit()
        wrapper.ex()

        print(f"Saved skeleton overview for category '{category}' with {count} images")

        return all_skeletons

    def construct_scaled_contour(self, orig_contour, xmin, ymin, scale, x_offset, y_offset):
        scaled_contour = np.zeros((orig_contour.shape[0], 2), dtype=np.int32)
        for i in range(orig_contour.shape[0]):
            x = orig_contour[i][0] - xmin
            y = orig_contour[i][1] - ymin
            scaled_contour[i] = [
                int(x * scale) + x_offset,
                int(y * scale) + y_offset
            ]
        return scaled_contour

    def generate_filled_outline(self, scaled_contour, width, height):
        export_img_filled = np.ones((height, width), dtype=np.uint8) * 255
        cv2.fillPoly(export_img_filled, [scaled_contour], color=0)
        return export_img_filled

    def convert_contour_to_path(self, contour):
        path = []
        for point in contour:
            path.append((float(point[0]), float(point[1])))
        return path

    def calc_should_rotate(self, contours):
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

    def export_contour(self):
        OUTLINE_WIDTH, OUTLINE_HEIGHT = 126, 84  # 126, 174
        # change outline manually here
        OUTLINE_MARGIN = 4

        A6_MULT = 0.5
        A5_MULT = 1
        A4_MULT = 2
        A3_MULT = 4
        format_multiplier = A5_MULT

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
        should_rotate = self.calc_should_rotate(obj_contour)
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

        # Use the new function to construct the scaled contour
        scaled_contour = self.construct_scaled_contour(orig_contour, xmin, ymin, scale, x_offset, y_offset)

        cv2.polylines(export_img_outline, [scaled_contour], isClosed=True, color=0, thickness=1)
        export_img_filled = self.generate_filled_outline(scaled_contour, OUTLINE_WIDTH, OUTLINE_HEIGHT)

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

        path = self.convert_contour_to_path(orig_contour)
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

        # assuming there is only one contour in the collection
        self.export_parallel_lines(coll[0], category)

        print(f"Exported contours to:")
        print(f"  Outline: {output_path_outline}")
        print(f"  Filled: {output_path_filled}")
        print(f"  Original: {output_path_original}")
        print(f"  Skeleton: {output_path_skeleton}")
        print(f"  Grog outline: {fname}")
        print(f"  HPGL outline: {fname2}")

    def export_parallel_lines(self, pa: Path, category: str) -> None:
        parallel_lines = Collection()
        for i in range(1, 600):
            new_parallel_path = pa.parallel_offset(i * 10)
            parallel_lines.add(new_parallel_path)

        for pa in parallel_lines:
            pa.velocity = 10

        fname = f"{category}_parallel_lines_{Timer.timestamp()}"
        wrapper = ExportWrapper(
            parallel_lines,
            PlotterType.HP_7550A_A3,
            10,  # 25mm - 11mm
            "datasets",
            fname,
            keep_aspect_ratio=True)
        wrapper.fit()
        wrapper.ex()

    def on_key_press(self, event):
        print(event.key)
        if event.key == 'e':
            self.export_contour()
        if event.key == 'left':
            self.current_index = max(self.current_index - 1, 1)
            self.update_display()
        if event.key == 'right':
            self.current_index = min(self.current_index + 1, self.max_index)
            self.update_display()

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

        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.axis('off')

        self.ax.axis('image')
        self.fig.canvas.draw_idle()

        self.root.title(f'{self.selected_category.get()}')


if __name__ == '__main__':
    viewer = ImageAnnotationViewer()
    