import cv2

def preprocess_image(path):
    img = cv2.imread(path)
    h, w = img.shape[:2]
    max_dim = max(h, w)

    if max_dim > 1800:
        scale = 1800 / max_dim
        img = cv2.resize(img, (int(w*scale), int(h*scale)))

    img = cv2.bilateralFilter(img, 9, 75, 75)

    temp = path.replace(".jpg", "_resized.jpg")
    cv2.imwrite(temp, img)
    return temp

