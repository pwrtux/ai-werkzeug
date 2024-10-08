import base64
import requests
import json
import os
import shutil
import click
from pathlib import Path
import rawpy
from PIL import Image
import cv2
from typing import List, Tuple
import config

def rename_files(directory: Path, prefix: str, start: int = 1, order: str = 'asc', image_formats: str = '.jpg,.png,.jpeg,.cr2', dry_run: bool = False) -> List[Tuple[Path, Path]]:
    """
    Rename image and text files in a directory with a specified prefix and numbering order.
    """
    image_exts = tuple(image_formats.split(','))

    # Get all image and text files
    image_files = [f for f in directory.iterdir() if f.suffix.lower() in image_exts]
    text_files = [f for f in directory.iterdir() if f.suffix.lower() == '.txt']

    # Sort files
    image_files.sort()
    text_files.sort()

    if order == 'desc':
        image_files.reverse()
        text_files.reverse()
        start = start + len(image_files) - 1

    # Rename files
    renamed_files = []
    for i, (img_file, txt_file) in enumerate(zip(image_files, text_files)):
        new_number = start + i if order == 'asc' else start - i
        new_img_name = f"{prefix}_{new_number:04d}{img_file.suffix}"
        new_txt_name = f"{prefix}_{new_number:04d}.txt"

        renamed_files.append((img_file, directory / new_img_name))
        renamed_files.append((txt_file, directory / new_txt_name))

    # Perform renaming or dry run
    for old_file, new_file in renamed_files:
        if dry_run:
            click.echo(f"Would rename '{old_file.name}' to '{new_file.name}'")
        else:
            old_file.rename(new_file)
            click.echo(f"Renamed '{old_file.name}' to '{new_file.name}'")

    if dry_run:
        click.echo("Dry run completed. No files were actually renamed.")
    else:
        click.echo(f"Renamed {len(renamed_files)} files successfully.")

    return renamed_files


def ensure_output_folder(output_folder):
    """
    Ensure that the output folder exists, creating it if necessary.
    
    Args:
    output_folder (Path): Path to the desired output folder.
    """
    output_folder.mkdir(parents=True, exist_ok=True)
    click.echo(f"Output folder ensured: {output_folder}")

def generate_caption_from_image(image_path, model="minicpm-v", api_url="http://localhost:11434/api/generate"):
    headers = {
        "Content-Type": "application/json"
    }
    
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    data = {
        "model": model,
        "prompt": "Give a concise caption of this image.",
        "images": [encoded_image],
        "stream": False,
        "system": config.SYSTEM_PROMPT,
        "options": {
            "temperature": 0.0,
            "num_predict": 160,
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        return result['response'].strip()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"An error occurred while parsing the response: {e}")
        return None

def check_existing_files(output_folder, prefix):
    """Check if there are existing files in the output folder that would be overwritten."""
    output_path = Path(output_folder)
    existing_files = [f for f in output_path.iterdir() if f.name.startswith(prefix) and (f.suffix.lower() in ['.txt', '.png', '.jpg', '.jpeg'])]
    return len(existing_files) > 0

def convert_cr2_to_jpg(input_file, output_file, dry_run=False):
    """
    Convert a .cr2 file to .jpg format using OpenCV.
    """
    if dry_run:
        click.echo(f"Would convert {input_file.name} to {output_file.name}")
        return

    try:
        with rawpy.imread(str(input_file)) as raw:
            rgb = raw.postprocess()
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_file), bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
        img = cv2.imread(str(output_file))
        if img is None:
            raise Exception("Failed to read the saved JPEG file.")
        click.echo(f"Converted {input_file.name} to {output_file.name}")
    except Exception as e:
        click.echo(f"Error converting {input_file.name}: {str(e)}")


def process_image_folder(input_folder, output_folder, dry_run=False):
    """
    Process all images in the input folder, converting .cr2 to .jpg if necessary.
    """
    if not dry_run:
        output_folder.mkdir(parents=True, exist_ok=True)
    
    processed_images = []
    for file in input_folder.iterdir():
        if file.suffix.lower() == '.cr2':
            output_file = output_folder / (file.stem + '.jpg')
            if dry_run:
                click.echo(f"Would convert {file.name} to {output_file.name}")
            else:
                convert_cr2_to_jpg(file, output_file)
            processed_images.append(output_file)
        elif file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            output_file = output_folder / file.name
            if dry_run:
                click.echo(f"Would copy {file.name} to {output_file.name}")
            else:
                shutil.copy2(file, output_file)
            processed_images.append(output_file)
    
    return processed_images

def create_lora_dataset(input_folder, output_folder, prefix="image", start=1, order='asc', image_formats='.jpg,.png,.jpeg,.cr2', dry_run=False):
    """
    Create a LoRA dataset by generating captions for images and saving them in separate text files with sequential naming.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    ensure_output_folder(output_path)

    image_exts = tuple(image_formats.split(','))

    # Get all image files
    image_files = [f for f in input_path.iterdir() if f.suffix.lower() in image_exts]

    # Sort files
    image_files.sort()
    if order == 'desc':
        image_files.reverse()
        start = start + len(image_files) - 1

    # Process files
    for i, img_file in enumerate(image_files):
        new_number = start + i if order == 'asc' else start - i
        new_img_name = f"{prefix}_{new_number:04d}{img_file.suffix}"
        new_txt_name = f"{prefix}_{new_number:04d}.txt"
        new_img_path = output_path / new_img_name
        new_txt_path = output_path / new_txt_name

        if dry_run:
            click.echo(f"Would process {img_file.name} -> {new_img_name}, {new_txt_name}")
        else:
            # Generate caption
            caption = generate_caption_from_image(str(img_file))
            if caption:
                # Copy and rename the image file
                shutil.copy2(img_file, new_img_path)
                # Write caption to the new text file
                with open(new_txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"[trigger] {caption}")
                click.echo(f"Processed {img_file.name} -> {new_img_name}, {new_txt_name}")
            else:
                click.echo(f"Skipping {img_file.name} due to caption generation failure.")

    if dry_run:
        click.echo("Dry run completed. No files were actually processed or renamed.")
    else:
        click.echo(f"Processed {len(image_files)} files successfully.")



    
@click.command()
@click.option('--input-folder', default='input', help='Path to the input folder containing images')
@click.option('--output-folder', default='output', help='Path to the output folder for the dataset')
@click.option('--prefix', default='xxx_', help='Prefix for output file names')
@click.option('--rename-only', is_flag=True, help='Only rename images without generating captions')
@click.option('--start', default=1, help='Starting number for renaming')
@click.option('--order', type=click.Choice(['asc', 'desc']), default='asc', help='Renaming order (ascending or descending)')
@click.option('--image-formats', default='.jpg,.png,.jpeg,.cr2', help='Comma-separated list of image formats to process')
@click.option('--dry-run', is_flag=True, help='Perform a dry run without actually renaming files or generating captions')
def main(input_folder, output_folder, prefix, rename_only, start, order, image_formats, dry_run):
    """Process images: rename or create a LoRA dataset with captions."""
    input_path = Path(input_folder).resolve()
    output_path = Path(output_folder).resolve()

    click.echo(f"Processing images...")
    click.echo(f"Input folder: {input_path}")
    click.echo(f"Output folder: {output_path}")
    click.echo(f"File prefix: {prefix}")
    click.echo(f"Dry run: {'Yes' if dry_run else 'No'}")

    # Ensure output folder exists
    ensure_output_folder(output_path)

    # Check if there are existing files that would be overwritten
    if not dry_run and check_existing_files(output_path, prefix):
        if not click.confirm("Existing files found in the output folder. Do you want to overwrite them?"):
            click.echo("Operation cancelled.")
            return

    if rename_only:
        click.echo("Renaming images only...")
        rename_files(output_path, prefix, start, order, image_formats, dry_run)
    else:
        click.echo("Creating LoRA dataset with captions...")
        create_lora_dataset(input_path, output_path, prefix, start, order, image_formats, dry_run)

    click.echo("Operation completed.")


if __name__ == "__main__":
    main()