from rembg import remove
import asyncio
import cv2


async def remove_background(input_path: str, output_path: str, progress_callback):
    """Removes background from an image and sends progress updates."""
    loop = asyncio.get_event_loop()

    with open(input_path, "rb") as file:
        input_image = file.read()

    # Send progress update
    await progress_callback(10, "Loading image...")

    result = await loop.run_in_executor(None, remove, input_image)

    # Send progress update
    await progress_callback(80, "Processing image...")

    with open(output_path, "wb") as out_file:
        out_file.write(result)

    await progress_callback(100, "Background removed successfully!")

    return output_path


async def enhance_image(input_path: str, output_path: str, progress_callback):
    """Enhances brightness and contrast of an image with progress updates."""
    loop = asyncio.get_event_loop()

    async def process_image():
        image = cv2.imread(input_path)
        if image is None:
            raise ValueError("Invalid image file.")

        await progress_callback(10, "Applying contrast and brightness...")

        # Apply contrast and brightness adjustments
        alpha = 1.2  # Contrast control
        beta = 30  # Brightness control
        enhanced = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

        await progress_callback(50, "Enhancing image...")

        cv2.imwrite(output_path, enhanced)

        await progress_callback(100, "Enhancement complete!")

    await loop.run_in_executor(None, process_image)

    return output_path
