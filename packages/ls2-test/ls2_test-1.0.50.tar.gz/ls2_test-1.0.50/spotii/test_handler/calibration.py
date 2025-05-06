import cv2
import os
import random
import ntpath

from PIL import Image
import piexif


ROW = 0
COL = 1





IDEAL_BAR_WIDTH = 26
IDEAL_BAR_HEIGHT = 92



MAX_HEIGHT = 1600  ## after 90 degree rotation,
MAX_WIDTH  = 1200

#FIRST_CROP_COL = 80
FIRST_CROP_COL = 215
FIRST_CROP_HEIGHT = IDEAL_BAR_HEIGHT*(min([int(MAX_HEIGHT/IDEAL_BAR_HEIGHT), 8]))
FIRST_CROP_WIDTH  = IDEAL_BAR_WIDTH *(min([int((MAX_WIDTH-FIRST_CROP_COL)/IDEAL_BAR_WIDTH),  30]))
FIRST_CROP_ROW = int((MAX_HEIGHT - FIRST_CROP_HEIGHT)/2) #657



IDEAL_BAR_ROW_OFFSET  = int((FIRST_CROP_HEIGHT - IDEAL_BAR_HEIGHT)/2)
#IDEAL_BAR_COL_OFFSET  = 280
IDEAL_BAR_COL_OFFSET  = 380

CROP_TOP    =[FIRST_CROP_ROW, FIRST_CROP_COL]
CROP_BOTTOM =[FIRST_CROP_ROW+FIRST_CROP_HEIGHT, FIRST_CROP_COL+FIRST_CROP_WIDTH]
FINAL_HEIGHT = 320
FINAL_WIDTH  = 780
FINAL_ROW = int((MAX_HEIGHT - FINAL_HEIGHT)/2)
FINAL_COL = FIRST_CROP_COL

FINAL_BAR_ROW = int((FINAL_HEIGHT -IDEAL_BAR_HEIGHT)/2)
FINAL_BAR_COL = IDEAL_BAR_COL_OFFSET

NEGATIVE = 'NEGATIVE'
POSITIVE = 'POSITIVE'
INVALID  = 'INVALID'
def cr_size():
    return FIRST_CROP_HEIGHT, FIRST_CROP_WIDTH

def cr(img):
    newImg=cv2.rotate(img,cv2.ROTATE_90_COUNTERCLOCKWISE)
    cropImg=newImg[FIRST_CROP_ROW:FIRST_CROP_ROW+FIRST_CROP_HEIGHT, FIRST_CROP_COL:FIRST_CROP_COL+FIRST_CROP_WIDTH]
    return cropImg 

def crop_rotate(original_img):
    img = original_img
    if original_img.shape[:2] > cr_size():
        img = cr(original_img)
    return img


_WIDTH_EXTRA  = 360
_HEIGHT_EXTRA = 500
_FIRST_WIDTH  = FINAL_WIDTH  + _WIDTH_EXTRA
_FIRST_HEIGHT = FINAL_HEIGHT + _HEIGHT_EXTRA

_FIRST_ROW = int((MAX_HEIGHT - _FIRST_HEIGHT)/2)
_FIRST_COL = 0
def first_crop_rotate(original_img):
    if original_img.shape[:2] > cr_size():
        newImg=cv2.rotate(original_img,cv2.ROTATE_90_COUNTERCLOCKWISE)
        img=newImg[_FIRST_ROW:_FIRST_ROW+_FIRST_HEIGHT, _FIRST_COL:_FIRST_COL+_FIRST_WIDTH]
    else:
        img = original_img
    return img


def final_save(finalImg, imageFile):
    height, width = finalImg.shape[:2]
    print(height, width)
    if height !=FINAL_HEIGHT or width!=FINAL_WIDTH:
        print('wrong picture size')
        return False
    
    cv2.imwrite(imageFile, finalImg)
    
    if os.path.splitext(imageFile)[1] == '.jpg':
        my_exif_ifd = {
                    piexif.ExifIFD.CameraOwnerName: u"Spot II",
                    }
        exif_dict = {"Exif":my_exif_ifd}
        exif_bytes = piexif.dump(exif_dict)
        im = Image.open(imageFile)
        im.save(imageFile, exif=exif_bytes)
        im.close()
    else :
        print('png')
    return True


def cr_modified(img, m_y, m_x):
    newImg=cv2.rotate(img,cv2.ROTATE_90_COUNTERCLOCKWISE)
    final_row =FINAL_ROW + m_y
    final_col =FINAL_COL + m_x
    cropImg=newImg[final_row:final_row+FINAL_HEIGHT, final_col:final_col+FINAL_WIDTH]
    return cropImg 

#    print("Save image to ",imageFile)
    return True
