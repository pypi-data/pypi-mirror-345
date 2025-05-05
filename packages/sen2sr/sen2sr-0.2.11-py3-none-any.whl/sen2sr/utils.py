import torch
import itertools
import pathlib
from typing import Optional, Literal



def define_iteration(dimension: tuple, chunk_size: int, overlap: int = 0):
    """
    Define the iteration strategy to walk through the image with an overlap.

    Args:
        dimension (tuple): Dimension of the S2 image.
        chunk_size (int): Size of the chunks.
        overlap (int): Size of the overlap between chunks.

    Returns:
        list: List of chunk coordinates.
    """
    dimy, dimx = dimension

    if chunk_size > max(dimx, dimy):
        return [(0, 0)]

    # Adjust step to create overlap
    y_step = chunk_size - overlap
    x_step = chunk_size - overlap

    # Generate initial chunk positions
    iterchunks = list(itertools.product(range(0, dimy, y_step), range(0, dimx, x_step)))

    # Fix chunks at the edges to stay within bounds
    iterchunks_fixed = fix_lastchunk(
        iterchunks=iterchunks, s2dim=dimension, chunk_size=chunk_size
    )

    return iterchunks_fixed


def fix_lastchunk(iterchunks, s2dim, chunk_size):
    """
    Fix the last chunk of the overlay to ensure it aligns with image boundaries.

    Args:
        iterchunks (list): List of chunks created by itertools.product.
        s2dim (tuple): Dimension of the S2 images.
        chunk_size (int): Size of the chunks.

    Returns:
        list: List of adjusted chunk coordinates.
    """
    itercontainer = []

    for index_i, index_j in iterchunks:
        # Adjust if the chunk extends beyond bounds
        if index_i + chunk_size > s2dim[0]:
            index_i = max(s2dim[0] - chunk_size, 0)
        if index_j + chunk_size > s2dim[1]:
            index_j = max(s2dim[1] - chunk_size, 0)

        itercontainer.append((index_i, index_j))

    return itercontainer


def predict_large(
    image_fullname: str | pathlib.Path,
    output_fullname: str | pathlib.Path,
    resolution: Literal["2.5m", "5m", "10m"] = "2.5m",
    overlap: int = 32,
    models: Optional[dict] = None,
    device: str = "cpu",
) -> pathlib.Path:
    """Generate a new S2 tensor with all the bands on the same resolution

    Args:
        image_fullname (Union[str, pathlib.Path]): The input image with the S2 bands
        output_fullname (Union[str, pathlib.Path]): The output image with the S2 bands
        resolution (Literal["2.5m", "5m", "10m"], optional): The final resolution of the
            tensor. Defaults to "2.5m".
        models (Optional[dict], optional): The dictionary with the loaded models. Defaults
            to None.

    Returns:
        pathlib.Path: The path to the output image
    """

    # Define the resolution factor
    if resolution == "2.5m":
        res_n = 4
    elif resolution == "5m":
        res_n = 2
    elif resolution == "10m":
        res_n = 1
    else:
        raise ValueError("The resolution is not valid")

    # Get the image metadata and check if the image is tiled
    with rio.open(image_fullname) as src:
        metadata = src.profile
        if metadata["tiled"] == False:
            raise ValueError("The image is not tiled")
        if metadata["blockxsize"] != 128 or metadata["blockysize"] != 128:
            raise ValueError("The image does not have 128x128 blocks")

    # Run always in patches of 128x128 with 32 of overlap
    nruns = define_iteration(
        dimension=(metadata["height"], metadata["width"]),
        chunk_size=128,
        overlap=overlap,
    )

    # Define the output metadata
    output_metadata = metadata.copy()
    output_metadata["width"] = metadata["width"] * res_n
    output_metadata["height"] = metadata["height"] * res_n
    output_metadata["transform"] = rio.transform.Affine(
        metadata["transform"].a / res_n,
        metadata["transform"].b,
        metadata["transform"].c,
        metadata["transform"].d,
        metadata["transform"].e / res_n,
        metadata["transform"].f,
    )
    output_metadata["blockxsize"] = 128 * res_n
    output_metadata["blockysize"] = 128 * res_n    
    
    # Create the output image
    with rio.open(output_fullname, "w", **output_metadata) as dst:
        data_np = np.zeros(
            (metadata["count"], metadata["height"] * res_n, metadata["width"] * res_n),
            dtype=np.uint16,
        )
        dst.write(data_np)
    
    # Check if the models are loaded
    if models is None:
        models = setmodel(resolution=resolution, device=device)

    # Iterate over the image
    with rio.open(output_fullname, "r+") as dst:
        with rio.open(image_fullname) as src:
            for index, point in enumerate(tqdm.tqdm(nruns)):

                # Read a block of the image
                window = rio.windows.Window(point[1], point[0], 128, 128)
                X = torch.from_numpy(src.read(window=window)).float().to(device)
                
                # Predict the super-resolution
                result = predict(X=X / 10_000, models=models, resolution=resolution) * 10_000
                result[result < 0] = 0
                result = result.cpu().numpy().astype(np.uint16)
            
                # Define the offset in the output space
                # If the point is at the border, the offset is 0 
                # otherwise consider the overlap
                if point[1] == 0:
                    offset_x = 0
                else:
                    offset_x = point[1] * res_n + overlap * res_n // 2

                if point[0] == 0:
                    offset_y = 0
                else:
                    offset_y = point[0] * res_n + overlap * res_n // 2
    
                # Define the length of the patch
                # The patch is always 224x224
                # There is three conditions:
                #  - The patch is at the corner begining (0, *) or (*, 0)
                #  - The patch is at the corner ending (width, *) or (*, height)
                #  - The patch is in the middle of the image
                if offset_x == 0:
                    skip = overlap * res_n // 2
                    length_x = 128 * res_n - skip
                    result = result[:, :, :length_x]
                elif (offset_x + 128) == metadata["width"]:
                    length_x = 128 * res_n
                    result = result[:, :, :length_x]                
                else:
                    skip = overlap * res_n // 2
                    length_x = 128 * res_n - skip
                    result = result[:, :, skip:(128 * res_n)]

                # Do the same for the Y axis
                if offset_y == 0:
                    skip = overlap * res_n // 2
                    length_y = 128 * res_n - skip
                    result = result[:, :length_y, :]
                elif (offset_y + 128) == metadata["height"]:
                    length_y = 128 * res_n
                    result = result[:, :length_y, :]                
                else:
                    skip = overlap * res_n // 2
                    length_y = 128 * res_n - overlap * res_n // 2
                    result = result[:, skip:(128 * res_n), :]
                    
                # Write the result in the output image
                window = rio.windows.Window(offset_x, offset_y, length_x, length_y)
                dst.write(result, window=window)

    return pathlib.Path(output_fullname)
