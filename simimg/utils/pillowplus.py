''' Some some utililty for reading and dealing with pillow images'''
from PIL import Image, ImageTk

def imageOpen(fn):
    try:
        img = Image.open(fn)
        if (
                img.format == 'PNG' and
                img.mode == 'I' and
                max(img.getdata()) > 255
        ):
            img = img.point(table16bit, 'L')
        return img
    except OSError:
        return None

def photoImageOpen(fn):
    img = imageOpen(fn)
    if img:
        return ImageTk.PhotoImage(img)
    else:
        print('here')

def imageResizeToFit(img, w, h):
    ratio = max(img.size[0]/w, img.size[1]/h)
    return img.resize(
        (int(img.size[0]/ratio), int(img.size[1]/ratio)),
        Image.ANTIALIAS
    )
