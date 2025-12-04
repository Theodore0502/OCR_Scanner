import cv2
import numpy as np

def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255,
                           cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 10:
        return image  # too small to deskew

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = 90 + angle

    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    return rotated


def preprocess_image(img_or_path):
    """
    Preprocess image for OCR.
    
    Args:
        img_or_path: Either a file path (str) or an already-loaded image (numpy array)
        
    Returns:
        Preprocessed image as uint8 numpy array
    """
    # Load image if path is provided
    if isinstance(img_or_path, str):
        img = cv2.imread(img_or_path)
    else:
        img = img_or_path

    # 1. Deskew
    img = deskew(img)

    # 2. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Remove noise + enhance contrast
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # 4. Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        35, 10
    )

    # Return as uint8 (not normalized) for compatibility with cv2.imwrite
    return thresh
