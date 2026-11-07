
import os
import time
import numpy as np
import matplotlib

# Use a non-GUI backend for Flask
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from PIL import Image


def compress_image(input_path, output_path, k):

    # Start measuring compression time
    start_time = time.perf_counter()

    # Open the original image
    image = Image.open(input_path).convert("RGB")

    # Store original dimensions
    original_width, original_height = image.size

    # Resize large images for faster processing
    max_dimension = 300

    if max(image.size) > max_dimension:
        image.thumbnail((max_dimension, max_dimension))

    # Store processed dimensions
    width, height = image.size

    print("\nOriginal Dimensions:", original_width, "x", original_height)
    print("Processed Dimensions:", width, "x", height)

    # Convert image into a NumPy matrix
    # float32 reduces memory usage compared to float64
    image_array = np.array(image, dtype=np.float32)

    height, width, channels = image_array.shape

    # Validate compression rank
    max_rank = min(height, width)

    if k < 1 or k > max_rank:
        raise ValueError(
            f"Rank k must be between 1 and {max_rank} for this image."
        )

    compressed_channels = []
    singular_values_list = []

    # Apply SVD separately to each RGB channel
    for channel in range(channels):

        print(f"\nCompressing channel {channel + 1}...")

        matrix = image_array[:, :, channel]

        U, S, VT = np.linalg.svd(
            matrix,
            full_matrices=False
        )

        singular_values_list.append(S)

        # Keep only the first k singular values
        U_k = U[:, :k]
        S_k = S[:k]
        VT_k = VT[:k, :]

        # Reconstruct the channel using rank-k approximation
        reconstructed = (U_k * S_k) @ VT_k

        compressed_channels.append(reconstructed)

    # Combine the three RGB channels
    compressed_array = np.stack(
        compressed_channels,
        axis=2
    )

    # Keep pixel values between 0 and 255
    compressed_array = np.clip(
        compressed_array,
        0,
        255
    ).astype(np.uint8)

    # Create and save compressed image
    compressed_image = Image.fromarray(compressed_array)

    compressed_image.save(output_path)

    # Calculate Mean Squared Error
    original_array = np.array(image, dtype=np.float32)

    difference = (
        original_array - compressed_array.astype(np.float32)
    )

    mse = np.mean(difference ** 2)

    # Calculate theoretical storage requirements
    original_values = 3 * height * width

    compressed_values = 3 * k * (height + width + 1)

    compression_ratio = (
        original_values / compressed_values
    )

    storage_saving = (
        1 - compressed_values / original_values
    ) * 100

    # Calculate actual file sizes
    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    # ----------------------------------
    # GENERATE RANK VS QUALITY GRAPH
    # ----------------------------------

    max_rank = min(height, width)

    ranks = np.unique(
        np.linspace(
            1,
            max_rank,
            min(20, max_rank),
            dtype=int
        )
    )

    # Include selected rank in the graph
    ranks = np.unique(np.append(ranks, k))

    mse_values = []

    # Calculate theoretical reconstruction error
    for rank in ranks:

        total_error = 0

        for singular_values in singular_values_list:

            total_error += np.sum(
                singular_values[rank:] ** 2
            )

        graph_mse = total_error / (
            height * width * channels
        )

        mse_values.append(graph_mse)

    # Create the graph
    plt.figure(figsize=(8, 5))

    plt.plot(
        ranks,
        mse_values,
        marker="o",
        linewidth=2
    )

    plt.title("Rank vs Reconstruction Error")
    plt.xlabel("Compression Rank (k)")
    plt.ylabel("Theoretical Mean Squared Error")

    plt.grid(True)
    plt.tight_layout()

    # Save the graph
    graph_directory = os.path.dirname(output_path) or "."

    graph_path = os.path.join(
        graph_directory,
        "quality_graph.png"
    )

    plt.savefig(graph_path, dpi=150)
    plt.close()

    # Calculate total processing time
    processing_time = time.perf_counter() - start_time

    # Display results in terminal
    print("\n========== COMPRESSION RESULTS ==========")

    print("Selected Rank:", k)
    print("Mean Squared Error:", round(float(mse), 2))

    print(
        "Theoretical Compression Ratio:",
        round(compression_ratio, 2),
        ":1"
    )

    print(
        "Theoretical Storage Saving:",
        round(storage_saving, 2),
        "%"
    )

    print("Processing Time:", round(processing_time, 3), "seconds")

    print(
        "Original File Size:",
        round(original_size / 1024, 2),
        "KB"
    )

    print(
        "Compressed File Size:",
        round(compressed_size / 1024, 2),
        "KB"
    )

    print("=========================================")

    # Return all results to Flask
    return {
        "mse": round(float(mse), 2),
        "compression_ratio": round(compression_ratio, 2),
        "storage_saving": round(storage_saving, 2),
        "original_size": round(original_size / 1024, 2),
        "compressed_size": round(compressed_size / 1024, 2),
        "processing_time": round(processing_time, 3),
        "original_width": original_width,
        "original_height": original_height,
        "processed_width": width,
        "processed_height": height
    }


# Run this file independently if required
if __name__ == "__main__":

    print("================================")
    print("       SVD IMAGE COMPRESSOR")
    print("================================")

    input_path = input(
        "\nEnter the path of your image: "
    ).strip().strip('"')

    if not os.path.isfile(input_path):

        print("Error: Image file not found!")

    else:

        try:

            k = int(input("Enter compression rank k: "))

            output_path = "compressed_image.png"

            compress_image(
                input_path,
                output_path,
                k
            )

        except ValueError as error:

            print("Error:", error)

        except Exception as error:

            print("Something went wrong:", error)
