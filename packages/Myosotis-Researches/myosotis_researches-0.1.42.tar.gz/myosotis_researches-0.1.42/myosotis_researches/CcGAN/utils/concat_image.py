from PIL import Image


def _concat_image_horizontal(img_list: list[Image], gap=2) -> Image:
    N = len(img_list)

    # Error 1: no images
    if N == 0:
        raise ValueError("The length of the image list is 0.")

    # Error 2: Size differs
    width = img_list[0].width
    height = img_list[0].height
    for i in range(1, N):
        if img_list[i].width != width:
            raise ValueError("All images should have the same width.")
        if img_list[i].height != height:
            raise ValueError("All images should have the same height.")

    # Create concated image
    concated_width = width * N + gap * (N + 1)
    concated_height = height + gap * 2
    concated_image = Image.new("RGB", (concated_width, concated_height))

    # Copy ans paste
    for i in range(N):
        concated_image.paste(img_list[i], (width * i + gap * (i + 1), gap))

    # return
    return concated_image


def _concat_image_vertical(img_list: list[Image], gap=2) -> Image:
    N = len(img_list)

    # Error 1: no images
    if N == 0:
        raise ValueError("The length of the image list is 0.")

    # Error 2: Size differs
    width = img_list[0].width
    height = img_list[0].height
    for i in range(1, N):
        if img_list[i].width != width:
            raise ValueError("All images should have the same width.")
        if img_list[i].height != height:
            raise ValueError("All images should have the same height.")

    # Create concated image
    concated_width = width + gap * 2
    concated_height = height * N + gap * (N + 1)
    concated_image = Image.new("RGB", (concated_width, concated_height))

    # Copy ans paste
    for i in range(N):
        concated_image.paste(img_list[i], (gap, height * i + gap * (i + 1)))

    # return
    return concated_image


def concat_image(img_list: list[Image], gap=2, direction="vertical"):

    if direction == "vertical":
        return _concat_image_vertical(img_list, gap=gap)
    elif direction == "horizontal":
        return _concat_image_horizontal(img_list, gap=gap)
    else:
        raise ValueError("Direction should be 'vertical' or 'horizontal'.")


__all__ = ["concat_image"]
