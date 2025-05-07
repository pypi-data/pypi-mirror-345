# fluix/animate.py

import os
import imageio.v2 as imageio
from typing import Optional
from fluix.core.utils import msg, resize_images_to_max_dim, resize_images_to_min_dim, natural_sort

def images_to_video(
    input_dir: str,
    output_path: str,
    fps: int = 30,
    extensions: tuple = ('.png', '.jpg', '.jpeg', '.gif'),
    codec: str = 'libx264',
    quality: int = 10,
    frame_range: tuple = None,
    resize: str = "none"
):

    # Handle file extension for OUTPUT
    try:
        file_ext = output_path.lower().split(".")[1]
    except IndexError:
        msg.error("No extensions given to the output file")
        exit(0)

    image_files = [f for f in os.listdir(input_dir) if f.endswith(extensions)]
    image_files = natural_sort(image_files)

    if frame_range:
        start, end = frame_range
        image_files = image_files[start:end]

    images = [imageio.imread(os.path.join(input_dir, fname)) for fname in image_files]

    # Handle resize flag

    match resize:
        case "min":
            resize_images_to_min_dim(images) # TODO: Implement the resize to max method
        case "max":
            resize_images_to_min_dim(images) # TODO: Implement the resize to min method

    match file_ext:
        case "gif":
            imageio.mimsave(output_path, images, fps=fps)
        case "mp4":
            writer = imageio.get_writer(
                output_path,
                fps=fps,
                codec=codec,
                quality=quality,
                ffmpeg_log_level='error',
                pixelformat='yuv420p'
            )
            for image in images:
                writer.append_data(image)
            writer.close()
        case _:
            msg.error("The output format should be either gif or mp4")
            exit(0)

    print(f"[FluiX] Saved animation to {output_path}")
