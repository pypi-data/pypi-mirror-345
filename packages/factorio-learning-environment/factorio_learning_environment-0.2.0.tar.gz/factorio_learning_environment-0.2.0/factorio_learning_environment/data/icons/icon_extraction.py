import os
from PIL import Image
import shutil


def extract_first_tile(source_path, output_dir):
    """
    Extract the first (largest) tile from a Factorio icon sprite map.
    The first tile is a square with sides equal to the image height.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process all PNG files in the source directory
    for filename in os.listdir(source_path):
        if not filename.lower().endswith('.png'):
            continue

        input_path = os.path.join(source_path, filename)
        output_path = os.path.join(output_dir, filename)

        try:
            # Open the image
            with Image.open(input_path) as img:
                # The height of the image determines the tile size
                tile_size = img.height

                # Crop the first tile (from top-left)
                first_tile = img.crop((0, 0, tile_size, tile_size))

                # Save the cropped tile
                first_tile.save(output_path)
                print(f"Processed: {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")


if __name__ == "__main__":
    # Source directory (Factorio icons)
    source_dir = "/Users/jackhopkins/Library/Application Support/Steam/steamapps/common/Factorio/factorio.app/Contents/data/base/graphics/technology"

    # Output directory (where to save the extracted tiles)
    output_dir = "./factorio_technologies_extracted"

    # Process the icons
    print(f"Starting icon extraction...")
    extract_first_tile(source_dir, output_dir)
    print(f"Icon extraction complete. Files saved to: {output_dir}")