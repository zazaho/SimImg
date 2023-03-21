""" Some some utililty for reading and dealing with pillow images"""
from PIL import Image, ImageTk, ImageChops

pillowplus_table16 = [i/256 for i in range(65536)]


def imageOpen(fn):
    try:
        img = Image.open(fn)
        if (
                img.format == "PNG" and
                img.mode == "I" and
                max(img.getdata()) > 255
        ):
            img = img.point(pillowplus_table16, "L")
    except:
        return None
    return img


def imageResize(img, w, h):
    try:
        res = img.resize((w, h), Image.ANTIALIAS)
    except:
        res = None
    return res


def imageResizeToFit(img, w, h):
    ratio = max(img.size[0]/w, img.size[1]/h)
    return imageResize(img, int(img.size[0]/ratio), int(img.size[1]/ratio))


def imageOpenAndResize(fn, w, h):
    return imageResize(imageOpen(fn), w, h)


def imageOpenAndResizeToFit(fn, w, h):
    return imageResizeToFit(imageOpen(fn), w, h)

def TkPhotoImage(img):
    try:
        return ImageTk.PhotoImage(img)
    except:
        return None

def photoImageOpen(fn):
    img = imageOpen(fn)
    if not img:
        return None
    return TkPhotoImage(img)


def photoImageOpenAndResize(fn, w, h):
    img = imageResize(imageOpen(fn), w, h)
    if not img:
        return None
    return TkPhotoImage(img)


def photoImageOpenAndResizeToFit(fn, w, h):
    img = imageResizeToFit(imageOpen(fn), w, h)
    if not img:
        return None
    return TkPhotoImage(img)


def thumbnailOpen(fn, w, h, channel=None, upscale=False):
    img = imageOpen(fn)
    if not img:
        return None

    try:
        # this is needed because thumbnail does not check that the file can
        # be actually loaded
        img.load()
        # if upscale is true and image is smaller than requested
        if upscale and img.size[0] < w and img.size[1] < h:
            # scale up
            img = imageResizeToFit(img, w, h)
        else:
            # scale down
            img.thumbnail((w, h))
    except:
        return None

    if (
            not channel or
            channel == "Default" or
            len(img.getbands()) == 1
    ):
        return img

    try:
        hsv = img.split() if img.getbands() == ("H", "S", "V") else img.convert("HSV").split()
    except:
        return img

    if channel == "Hue":
        img = Image.merge(
            "HSV",
            (
                hsv[0],
                ImageChops.constant(hsv[0], 255),
                ImageChops.constant(hsv[0], 255),
            )
            )
    if channel == "Saturation":
        img = hsv[1]
    if channel == "Value":
        img = hsv[2]
    return img


def photoThumbnailOpen(fn, w, h, channel=None, upscale=False):
    img = thumbnailOpen(fn, w, h, channel=channel, upscale=upscale)
    if not img:
        return None
    return TkPhotoImage(img)
