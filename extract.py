from easyocr import Reader
from PIL import Image
import io
import numpy as np
reader = Reader(['en'])
def extract_text_from_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    result = reader.readtext(np.array(img))
    extracted_text = " ".join(entry[1] for entry in result)
    return extracted_text