"""Image file format converter using Pillow."""
import os
from PIL import Image


def print_supported_extensions():
    """Prints the list of image file extensions supported by Pillow."""
    print("Supported image file extensions in Pillow:")
    for ext in Image.registered_extensions():
        print(f"{ext}")


def is_supported_file(filename):
    """Checks if the file format is supported by Pillow."""
    _, extension = os.path.splitext(filename)
    return is_supported_file_format(extension)


def is_supported_file_format(file_extension):
    """Checks if the file format is supported by Pillow."""
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension

    return file_extension.lower() in Image.registered_extensions()


def convert_image(input_file, output_extension):
    """Converts a image file to the specified format."""
    
    assert is_supported_file(input_file), f"{input_file} is not supported format."
    assert is_supported_file_format(output_extension), f"{output_extension} is not supported format."

    output_file = os.path.splitext(input_file)[0] + '.' + output_extension
    
    try:
        with Image.open(input_file) as img:
            img.save(output_file, output_extension.upper())
            print(f'Converted {input_file} to {output_file}.')
    except Exception as e:
        print(f'Error occurred during conversion: {e}')
