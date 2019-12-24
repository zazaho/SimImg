''' Some some utililty for reading and dealing with pillow images'''
from PIL import Image, ImageTk

pillowplus_table16 = [i/256 for i in range(65536)]

def imageOpen(fn):
    try:
        img = Image.open(fn)
        if (
                img.format == 'PNG' and
                img.mode == 'I' and
                max(img.getdata()) > 255
        ):
            img = img.point(pillowplus_table16, 'L')
        return img
    except OSError:
        return None

def imageResize(img, w, h):
    try:
        res=img.resize((w, h), Image.ANTIALIAS)
    except IOError as e:
        print(e)
        res=None
    return res

def imageResizeToFit(img, w, h):
    ratio = max(img.size[0]/w, img.size[1]/h)
    return imageResize(img, int(img.size[0]/ratio), int(img.size[1]/ratio))

def imageOpenAndResize(fn, w, h):
    img = imageOpen(fn)
    if not img:
        return None
    return imageResize(img, w, h)

def imageOpenAndResizeToFit(fn, w, h):
    img = imageOpen(fn)
    if not img:
        return None
    return imageResizeToFit(img, w, h)

def photoImageOpen(fn):
    img = imageOpen(fn)
    if not img:
        return None
    return ImageTk.PhotoImage(img)

def photoImageOpenAndResize(fn, w, h):
    img = imageOpen(fn)
    if not img:
        return None
    return ImageTk.PhotoImage(imageResize(img, w, h))

def photoImageOpenAndResizeToFit(fn, w, h):
    img = imageOpen(fn)
    if not img:
        return None
    return ImageTk.PhotoImage(imageResizeToFit(img, w, h))
