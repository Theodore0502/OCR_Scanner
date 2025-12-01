import cv2

def preprocess_image(path):
    img = cv2.imread(path)
    h, w = img.shape[:2]

    scale = 1800 / max(h, w)   # ảnh max-dimension = 1800px
    img = cv2.resize(img, (int(w*scale), int(h*scale)))
    
    temp_path = path.replace(".jpg", "_resized.jpg")
    cv2.imwrite(temp_path, img)
    return temp_path
