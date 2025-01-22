import numpy as np
from PIL import Image
from easyocr import Reader

def ocr_image(picture: Image, reader: Reader, separator=' '):
    ocr_result = reader.readtext(np.array(picture))
    return separator.join(t[1] for t in ocr_result)