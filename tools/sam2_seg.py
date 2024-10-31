import os
from cursor.data import DataDirHandler
from cursor.timer import Timer

# if using Apple MPS, fall back to CPU for unsupported ops
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

import numpy as np
import torch
import matplotlib.pyplot as plt
from PIL import Image
import random
from pathlib import Path


def get_gpu_info():
    if not torch.cuda.is_available():
        return None

    props = torch.cuda.get_device_properties(0)
    return {
        'name': props.name,
        'compute_capability': f"{props.major}.{props.minor}",
        'total_memory': props.total_memory / 1024 ** 3  # Convert to GB
    }


# select the device for computation
if torch.cuda.is_available():
    device = torch.device("cuda")
    gpu_info = get_gpu_info()
    print(f"GPU detected: {gpu_info['name']} (Compute Capability: {gpu_info['compute_capability']})")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"Using device: {device}")


# Function to check GPU capabilities
def get_optimal_precision():
    if not torch.cuda.is_available():
        return None, "fp32"

    cc_major = torch.cuda.get_device_properties(0).major

    # Ampere (8.x) or newer - supports BF16
    if cc_major >= 8:
        return torch.bfloat16, "bf16"
    # Pascal (6.x) or newer - good FP16 support
    elif cc_major >= 6:
        return torch.float16, "fp16"
    # Older GPUs - best to stick with FP32
    else:
        return torch.float32, "fp32"


if device.type == "cuda":
    dtype, precision_name = get_optimal_precision()
    print(f"Using {precision_name.upper()} precision based on GPU capabilities")

    if dtype != torch.float32:
        torch.autocast("cuda", dtype=dtype).__enter__()

    # Enable TF32 for Ampere GPUs
    if torch.cuda.get_device_properties(0).major >= 8:
        print("Enabling TF32 for matrix multiplications")
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
elif device.type == "mps":
    print(
        "\nSupport for MPS devices is preliminary. SAM 2 is trained with CUDA and might "
        "give numerically different outputs and sometimes degraded performance on MPS. "
        "See e.g. https://github.com/pytorch/pytorch/issues/84936 for a discussion."
    )

np.random.seed(3)


def show_anns(anns, borders=True):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)
    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:, :, 3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        color_mask = np.concatenate([np.random.random(3), [0.5]])
        img[m] = color_mask
        if borders:
            import cv2
            contours, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours = [cv2.approxPolyDP(contour, epsilon=0.01, closed=True) for contour in contours]
            cv2.drawContours(img, contours, -1, (0, 0, 1, 0.4), thickness=1)
    ax.imshow(img)
    plt.show()


# Your image loading and processing code...
image_folder = Path('/home/marcel/Downloads/sam2/')
jpg_files = list(image_folder.glob('*.jpg'))
if not jpg_files:
    raise ValueError(f"No jpg files found in {image_folder}")

random_image_path = random.choice(jpg_files)
print(f"Selected image: {random_image_path}")
image = Image.open(random_image_path)
image = np.array(image.convert("RGB"))

from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

sam2_checkpoint = DataDirHandler().data_dir / "sam2" / "checkpoints" / "sam2.1_hiera_large.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
sam2 = build_sam2(model_cfg, sam2_checkpoint, device=device, apply_postprocessing=False)

mask_generator_2 = SAM2AutomaticMaskGenerator(
    model=sam2,
    points_per_side=64,
    points_per_batch=128,
    pred_iou_thresh=0.7,
    stability_score_thresh=0.92,
    stability_score_offset=0.7,
    crop_n_layers=1,
    box_nms_thresh=0.7,
    crop_n_points_downscale_factor=2,
    min_mask_region_area=25.0,
    use_m2m=True,
)

masks2 = mask_generator_2.generate(image)

plt.figure(figsize=(20, 20))
plt.imshow(image)
# show_anns(masks2)
plt.axis('off')
# plt.show()
plt.savefig(DataDirHandler().png("sam2") / f'sam2_{Timer.timestamp()}.png')
