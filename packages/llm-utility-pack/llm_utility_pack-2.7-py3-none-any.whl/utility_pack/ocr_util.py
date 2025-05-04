import pytesseract, os, cv2, numpy as np, os
from tempfile import NamedTemporaryFile
from deskew import determine_skew
from PIL import Image, ImageOps
from pytesseract import Output
from skimage import filters

from utility_pack.logger import log_exception

os.environ['OMP_THREAD_LIMIT'] = "1"

def detect_if_darkmode_image(image, threshold=0.5):
    try:
        # Convert Pillow image to NumPy array
        np_image = np.array(image)

        # Convert to grayscale using OpenCV
        gray_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
        
        if gray_image is None:
            raise ValueError("Could not open the image file.")

        # Normalize pixel values between 0 and 1
        normalized = gray_image / 255.0

        # Calculate the mean pixel intensity
        mean_intensity = np.mean(normalized)

        # If the mean intensity is lower than threshold, assume black background
        return mean_intensity < threshold
    except Exception:
        log_exception()

    return False

def invert_image(input_pil_image):
    return ImageOps.invert(input_pil_image.convert("RGB"))

def array_img(img, denoise=True):
    pil_image_rgb = img.convert('RGB')
    img = np.array(pil_image_rgb)

    if len(img.shape) == 3:
        if img.shape[2] > 1:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if denoise:
        img = cv2.fastNlMeansDenoising(img, None)

    return img

def rotate_image(pil_image, angle):
    return pil_image.rotate(angle, expand=True)

def sauvola_binarization(pil_image, window_size=15, k=0.2):
    # Open the image using Pillow
    pil_image = pil_image.convert('L')
    
    # Convert Pillow image to numpy array
    img_array = np.array(pil_image)
    
    # Perform Sauvola thresholding
    threshold = filters.threshold_sauvola(img_array, window_size=window_size, k=k)
    
    # Apply the threshold to create a binary image
    binary = img_array > threshold
    
    # Convert back to Pillow Image
    result = Image.fromarray((binary * 255).astype(np.uint8))
    
    return result

def raw_ocr_with_topbottom_leftright(image, lang='por'):
    # Raw extraction
    data = pytesseract.image_to_data(image, lang=lang, output_type=Output.DATAFRAME)
    
    # Clean the data
    data = data.dropna(subset=['text'])
    data['text'] = data['text'].str.strip()

    # Sort by top position, then left position
    data_sorted = data.sort_values(['top', 'left'])

    # Group by top position (approximately) to get lines
    data_sorted['line_num'] = (data_sorted['top'] / 10).astype(int)

    # Concatenate text for each line
    result = data_sorted.groupby('line_num')['text'].apply(' '.join).reset_index()

    # Final text output
    text = '\n'.join(result['text'])

    return text

def ocr_image_pipeline(pil_image):
    try:
        text = ""

        if detect_if_darkmode_image(pil_image):
            pil_image = invert_image(pil_image)

        # Binarize by default
        image_sauvola = sauvola_binarization(pil_image, window_size=15, k=0.08)

        # Detect rotation
        angle = determine_skew(array_img(image_sauvola, denoise=False)) * 0.85

        if angle != 0:
            image_sauvola = rotate_image(image_sauvola, angle)

        text = raw_ocr_with_topbottom_leftright(image_sauvola)
        text = text.replace('\x0c', '').strip()

        if text == "":
            text = raw_ocr_with_topbottom_leftright(pil_image)
            text = text.replace('\x0c', '').strip()

        while '  ' in text:
            text = text.replace('  ', ' ')
        
        while '\n ' in text:
            text = text.replace('\n ', '\n')
        
        while '\n\n' in text:
            text = text.replace('\n\n', '\n')

        return text
    except Exception as e:
        print(e, flush=True)

    return ""

def is_photo(pix_image, threshold=0.6):
    # Convert to PIL image
    with NamedTemporaryFile(delete=False, suffix='.png') as temp_image:
        pix_image.save(temp_image)

        # Open the image
        img = Image.open(temp_image.name)
        
        # Convert to grayscale
        img_gray = img.convert('L')
        
        # Convert to numpy array
        img_array = np.array(img_gray)

        # Calculate the percentage of white pixels
        white_pixels = np.sum(img_array > 200)

        # Calculate the percentage of white pixels
        total_pixels = img_array.size

        # Calculate the percentage of white pixels
        white_pixel_ratio = white_pixels / total_pixels

        return not (white_pixel_ratio > threshold)

def ocr_page(pix_image):
    # Convert to PIL image
    with NamedTemporaryFile(delete=False, suffix='.png') as temp_image:
        pix_image.save(temp_image)
        image = Image.open(temp_image.name)
        return ocr_image_pipeline(image)
