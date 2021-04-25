
import cv2, imutils, pytesseract
import numpy as np


def get_plate_from_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 13, 15, 15)
    gray = cv2.bitwise_not(gray)

    kernel = np.ones((1,1),np.uint8)
    contrast = cv2.dilate(gray,kernel,iterations=2)
    thr,contrast = cv2.threshold(a, 127, 255, cv2.THRESH_OTSU)

    # General algorithim https://medium.com/programming-fever/license-plate-recognition-using-opencv-python-7611f85cdd6c
    cnts = cv2.findContours(contrast.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
    screenCnt = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    mask = np.zeros(gray.shape,np.uint8)
    cv2.drawContours(mask,[screenCnt],0,255,-1,)
    cv2.bitwise_and(img,img,mask=mask)

    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    #topx+=20
    #bottomx-=10
    cropped = contrast[topx:bottomx+1, topy:bottomy+1]

    final = cv2.resize(cropped, (0,0),fx=1,fy=1)

    final = cv2.GaussianBlur(final,(3,3), 0)
    thr,final = cv2.threshold(final,0,255,cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)

    text = pytesseract.image_to_string(final, config='--psm 6', lang='eng')
    return text

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print(f'Usage: {sys.argv[0]} [image]')
        exit()

    img = cv2.imread(sys.argv[1])
    text = get_plate_from_image(cv2.resize(img, (600,400)))
    print(text)
