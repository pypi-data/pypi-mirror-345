import os
import cv2
import numpy as np

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import calibration
from random import randrange
from define import *


FIRST_BAR_FAIL_FOLDER = 'first_bar_failed'

class Target():
        
    def channel_increase(self, c, value):
        if value >0:
            #print('increase', value)
            lim = 255 - value
            c[c > lim] = 255          
            c[c <= lim] += value
        else:
            #print('decrease', value)
            lim = abs(value)
            c[c < lim] = 0
            c[c >= lim] -= lim            
        return c
        
    def bright(self,img, value):
        b, g, r = cv2.split(img)
        b = self.channel_increase(b, value)
        g = self.channel_increase(g, value)
        r = self.channel_increase(r, value)
        final_img = cv2.merge((b, g, r))
        return final_img

    def balance(self,img, average):
        mean, stdev =cv2.meanStdDev(img)
        mn_list = [int(mean[0][0]), int(mean[1][0]), int(mean[2][0])]
        #average = int(sum(mn_list)/len(mn_list))
        #average = 230
        b, g, r = cv2.split(img)
        b = self.channel_increase(b, average - mn_list[0]+8)
        g = self.channel_increase(g, average - mn_list[1]-5)
        r = self.channel_increase(r, average - mn_list[2]-1)
        final_img = cv2.merge((b, g, r))
        return final_img

    def clahe_md(self, image, para1, para2, para3):
        b, g, r = cv2.split(image)
        clahe = cv2.createCLAHE(clipLimit=para1, tileGridSize=(para2,para3))
        b1 = clahe.apply(b)
        g1 = clahe.apply(g)
        r1 = clahe.apply(r)
        result = cv2.merge([b1,g1,r1])
        return result

    def areaFilter(self, img, area, target_size):  #target_size [height, width], return area list
        #print('areaFilter')
        h_f_result = self.h_f(img, area, target_size[1])
        #print (h_f_result)
        v_f_result = self.v_f(img, h_f_result, target_size[0])
        #print (v_f_result)
        return v_f_result

    def red_color_filter_mask(self, image, low_min, low_max, high_min, high_max):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask_1 = cv2.inRange(hsv, np.array([low_min,   40, 40]), np.array([low_max,  255, 255]) )
        mask_2 = cv2.inRange(hsv, np.array([high_min, 40, 40]),  np.array([high_max, 255, 255]) )
        mask  = cv2.bitwise_or(mask_1, mask_2)
        return mask        

    def firstBar(self,image):
        mask =self.red_color_filter_mask(image, 0, 10, 140, 180)
        kernel = np.ones((3,3), np.uint8)
        dilation = cv2.erode(mask, kernel, iterations=1)
        dilation = cv2.dilate(dilation, kernel, iterations=1)
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        final_x=0
        final_y=0
        if len(contours) != 0:
            for each in contours:
                x,y,w,h = cv2.boundingRect(each)
                if h >30:
                    if final_x == 0 or final_x > x:
                        final_x = x
                    if final_y == 0 or final_y > y:
                        final_y = y
##        print(x,y,w,h)
##        cv2.imshow("mask", mask)
##        cv2.imshow("dilation", dilation)
##        cv2.waitKey(0)
        if final_x==0 and final_y==0:
            final_x=280
            final_y=280
        print("first bar:",final_x, final_y)
        return final_x, final_y


    def findArea(self,image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
        kernel = np.ones((9,9), np.uint8)
        dilation = cv2.erode(thresh, kernel, iterations=1)
        dilation = cv2.dilate(dilation, kernel, iterations=1)
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        x=0
        y=0
        if len(contours) != 0:
            c = max(contours, key = cv2.contourArea)
            x,y,w,h = cv2.boundingRect(c)
            print(x,y,w,h)
            if x!=0 or y!=0:
                x = x+3
                if h > calibration.FINAL_HEIGHT:
                    y = y+ int((h - calibration.FINAL_HEIGHT)/2)
        else:
            x =90
            y = calibration._HEIGHT_EXTRA/2
#        cv2.imshow("dilation", dilation)
#        cv2.waitKey(0)            
        return x,y



    def target_cut(self,original_img):  #if identifier is not str(define.Invalid_image_identifier), will do first stage detection for 'invalid' confirm again.
        image = calibration.crop_rotate(original_img)
        height,width = image.shape[:2]
        if(height == calibration.FINAL_HEIGHT and width == calibration.FINAL_WIDTH): ## Return 1: For those pictures from server or dash board
            return NEGATIVE, image,
        
        blc = self.balance(image,198)
        x,y= self.firstBar(blc)
#         print(x,y)
#         cv2.imshow("blc", blc)
#         cv2.waitKey(0)
        if(x== 0 and y ==0):                                                         ## Return 2: For NO FIRST BAR DETECTION
            return INVALID, blc 
        m_x = x - calibration.IDEAL_BAR_COL_OFFSET
        m_y = y - calibration.IDEAL_BAR_ROW_OFFSET
        cal = calibration.cr_modified(original_img, m_y, m_x)
        cal_h, cal_w = cal.shape[:2]
        #print(cal_h,cal_w)
        if cal_h != calibration.FINAL_HEIGHT or cal_w != calibration.FINAL_WIDTH:    ## Return 3:out of range, wrong bar position detection
            print('wrong bar position',x,y)
#             cv2.imshow("cal", cal)
#             cv2.waitKey(0)
 
            cal = calibration.cr_modified(original_img, 0, 0)
            final = self.balance(cal,198)
            return NEGATIVE, final 
        final = self.balance(cal,198)
#         cv2.imshow("final", final)
#         cv2.waitKey(0)
        return NEGATIVE,final                                                      ## Return 4: Normal return

        
    def second_bar_block_cut(self, image, x, y, reduce = 15):
        secondBarToFirst = 160
        #secondBarWidth = calibration.IDEAL_BAR_WIDTH+4

#        reduce = 15
#        reduce = 30
        weak_height = 92 -reduce*2
        weak_row_start = y + (reduce)        

        block_offset =130
        block_width  = 100
        block = image[ weak_row_start: weak_row_start+weak_height,
                              x + block_offset : x + block_offset + block_width]
        return block
################################# old one, change name to crop to use
    def crop_old(self, original_img, bar_x, bar_y):
        if bar_x ==None:
            return self.target_cut(original_img)

        crop_x = bar_x+105   ##fixed detection area offset base on testing
        crop_y = bar_y+70
        cropImg = original_img[crop_y:crop_y+calibration.FINAL_WIDTH, crop_x:crop_x+calibration.FINAL_HEIGHT]
        newImg=cv2.rotate(cropImg,cv2.ROTATE_90_COUNTERCLOCKWISE)

        final = self.balance(newImg,198)
#         cv2.imshow("final", final)
#         cv2.waitKey(0)
        return NEGATIVE, final
        
################################# 20240704 new one, for new caset
    def crop(self, original_img, bar_x, bar_y):
        image = calibration.first_crop_rotate(original_img)
#        cv2.imshow("image", image)
#        cv2.waitKey(0)
        height,width = image.shape[:2]
        if(height == calibration.FINAL_HEIGHT and width == calibration.FINAL_WIDTH): ## Return 1: For those pictures from server or dash board
            print("-- small size image")
            return NEGATIVE, image,

        
        x,y = self.findArea(image);
        if x!=0 or y!=0:
            final = image[y:y+calibration.FINAL_HEIGHT, x:x+calibration.FINAL_WIDTH]
#            cv2.imshow("final", final)
#            cv2.waitKey(0)
        else:
            return self.crop_old(original_img, bar_x, bar_y);

        return NEGATIVE, final

    def calculation(self, image):
        result,img = self.target_cut(image)
        return [result,img]

class FirstBarDetection(Target):
    def first_bar_cut(self,image):
        md = 0
        x,y=self.firstBar(image)
        bar = image[ y+md: y+md+100, x+md: x+md + 80]
        return bar
        
    
    def calculation(self, image):
        image = calibration.crop_rotate(image)
        height,width = image.shape[:2]
        if(height == calibration.FINAL_HEIGHT and width == calibration.FINAL_WIDTH):
            blc=image
        else:
            blc = self.balance(image,200)
        bar = self.first_bar_cut(blc)
        return [UNKNOWN,bar]

class ColorFilterCut(Target):
    def filt_width(self, original_list, number, min_mean):
        sort_list=original_list.copy()
        sort_list.sort()
        average = sort_list[number-1]
        #average = sum(original_list)/len(original_list)
        maxim=sort_list[-1]
        minium =sort_list[0]

        print(sort_list)
        print('number', number, 'min_mean', min_mean)
        rtn_list = []
        for each in original_list:
            if each<average:
                if each <min_mean:
                    rtn_list.append(minium)
                else:
                    pass
            else:
                rtn_list.append(maxim)
        #print('rtn_list', rtn_list)
        i =0
        for each in rtn_list:
            if each == maxim:
                break;
            rtn_list[i] =maxim
            i+=1
        #print('fix head', rtn_list)
        i=len(rtn_list)
        for each in reversed(rtn_list):
            i -=1
            if each == maxim:
                break;            
            rtn_list[i]=maxim
        #print('fix tail', rtn_list)
        return rtn_list

    def filt_width_new(self, original_list, min_mean):
        average = sum(original_list)/len(original_list)
        minium= min(original_list)
        maxim= max(original_list)
##        print(original_list)
##
##        print('average', average)
        rtn_list = []
        for each in original_list:
            if each<average:
                if each <min_mean:
                    rtn_list.append(minium)
                else:
                    pass
            else:
                rtn_list.append(maxim)
##        print('rtn_list', rtn_list)
        i =0
        for each in rtn_list:
            if each == maxim:
                break;
            rtn_list[i] =maxim
            i+=1
##        print('fix head', rtn_list)
        i=len(rtn_list)
        for each in reversed(rtn_list):
            i -=1
            if each == maxim:
                break;            
            rtn_list[i]=maxim
##        print('fix tail', rtn_list)
        return rtn_list

    def block_mean_std(self, image):
        mean, stdev =cv2.meanStdDev(image)
        return int(mean[0]), int(stdev[0])

    def mean_std(self, image, ch):
        num =1
        height, width = image.shape[:2]
        step= int(height/num)
        start =0
        mn_list=[]
        std_list =[]
        for i in range(num):
            block = image[start:start+step, 0:width]
            mn, std = self.block_mean_std(block)
            mn_list.append(mn)
            std_list.append(std)
            start+=step
        
        max_mn = max(mn_list)
        m_index = mn_list.index(max_mn)
        max_mn_std = std_list[m_index]
        return max_mn, max_mn_std

        
        
    def av_mean_draw(self, image, barWidth, ch):
        height,width =image.shape[:2]
        
        mn_list  = []
        std_list = []
        x=0
        while width > 0:
            bar = image[0:height, x:x+barWidth]
            mn, std = self.mean_std(bar, ch)
            mn_list.append(mn)
            std_list.append(std)
            x+=barWidth
            width -=barWidth
        #print(mn_list)
#        print(std_list)
        return mn_list, std_list
    def lightBarConfirm(self, mn_list, deep, width):
        #print(mn_list)
        value = min(mn_list)
        print('min value',value)
        print('max value',max(mn_list))
        if value == max(mn_list):
            #print('Negative')
            return NEGATIVE
        length = []
        count = 0
        for each in mn_list:
            if each == value:
                count+=1
            else:
                if count!=0:
                    length.append(count)
                count=0
        if count!=0:
            length.append(count)
        
        max_width = max(length)
        print(max_width, length)
#        if value > deep and max_width > width:
        if max_width > width:
            #print('Positive')
            return POSITIVE
        #print('Negative')
        return NEGATIVE

    
    
        
    def first_detection(self, image):
        #print('in first_detection')
        try:
            idf,blc =self.target_cut(image)

#            blc = self.clahe_md(blc, 1,8,8)
             
            mask =self.red_color_filter_mask(blc, 0, 10, 140, 180)
            
            kernel = np.ones((8,8), np.uint8)
            dilation = cv2.erode(mask, kernel, iterations=1)
            dilation = cv2.dilate(dilation, kernel, iterations=1)

            
            contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            idf = INVALID
            final_x=0
            final_y=0
            if len(contours) != 0:
                for each in contours:
                    x,y,w,h = cv2.boundingRect(each)
##                    print(x,y,w,h)
                    if final_x == 0 or final_x > x:
                        final_x = x
                    if final_y == 0 or final_y > y:
                        final_y = y
                idf = NEGATIVE
##                print('final:',final_x,final_y)
##                if len(contours)>1:
##                    cv2.imshow("blc", blc)
##                    cv2.imshow("dilation", dilation)
##                    cv2.waitKey(0)
                 

##            if len(contours) != 0:
##                # draw in blue the contours that were founded
##                cv2.drawContours(blc, contours, -1, 255, 3)
##
##                # find the biggest countour (c) by the area
##                c = max(contours, key = cv2.contourArea)
##                x,y,w,h = cv2.boundingRect(c)
##
##                # draw the biggest contour (c) in green
##                cv2.rectangle(blc,(x,y),(x+w,y+h),(0,255,0),2)
##            else:
##                print('invalid')

                                    
            return idf, blc, final_x, final_y
        except Exception as e:
            print(e)

 

    def second_detection(self, blc, x, y):
        #print('in second detection')
        try:
            idf = NEGATIVE
            blc = self.balance(blc,200)
            mask_1 = self.red_color_filter_mask(blc,0,10,140,180)        
            clh = self.clahe_md(blc, 13,7,15)
            mask_2 = self.red_color_filter_mask(clh,0,20,140,180)
            
            mask  = cv2.bitwise_or(mask_1, mask_2)


##            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (8,4))
            n =1
##            kernel = np.ones((3,3), np.uint8)
##            final    = cv2.dilate(mask, kernel, iterations=n)

            kernel = np.ones((4,4), np.uint8)
            final  = cv2.erode(mask, kernel, iterations=n)

            kernel = np.ones((4,4), np.uint8)
            final    = cv2.dilate(final, kernel, iterations=n)
 



            kernel = np.ones((4,4), np.uint8)
            final    = cv2.dilate(final, kernel, iterations=n)
            kernel = np.ones((4,4), np.uint8)
            final  = cv2.erode(final, kernel, iterations=n)



##            kernel = np.ones((15,4), np.uint8)
##            final    = cv2.dilate(final, kernel, iterations=n)

##            kernel = np.ones((3,3), np.uint8)
##            opening = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
##
##            kernel = np.ones((5,5), np.uint8)
##            opening = cv2.morphologyEx(opening, cv2.MORPH_OPEN, kernel)
##
##            kernel = np.ones((60,4), np.uint8)
##            opening = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
            

            
            block = self.second_bar_block_cut(final, x, y)        
            contours, hierarchy = cv2.findContours(block, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if len(contours) != 0:
                c = max(contours, key = cv2.contourArea)
                x,y,w,h = cv2.boundingRect(c)

                #print("x : %d, y : %d, w : %d, h : %d" % ( x,y,w,h))
                if h >60:
                    idf = POSITIVE
                
            return idf, clh, block
        except Exception as e:
            print(e)
            
    def detection(self, image):
        #print('in Val')
        try:
            idf, blc, x, y = self.first_detection(image)
            if idf == INVALID:
                return [INVALID, blc, None, None]
            idf, clh, block_gray = self.second_detection(blc, x, y)
            return [idf, blc, clh, block_gray]
        except Exception as e:
            print(e)

    
    def calculation(self, image):
        idf, blc, clh, block = self.detection(image)
        return [blc, block]
        

class Val(ColorFilterCut):    
    def calculation(self, image):
        idf, blc, clh, block = self.detection(image)
        block = cv2.bitwise_not(block)

        b = 0
        g = 1
        r = 2
        av =3
        sample_width = 1
        mn_list, std_list = self. av_mean_draw(block, sample_width, g)

        mn_filter  = 185#235
        width_filter = 6
#        number_of_low_mn = 36
        number_of_low_mn = 36
        
#        filt_width_list = self.filt_width(mn_list, number_of_low_mn, mn_filter)
        filt_width_list = self.filt_width_new(mn_list, mn_filter)

        rtn = self.lightBarConfirm(filt_width_list, mn_filter, width_filter)        
        final = blc
        #blur = cv2.blur(mph, (15, 15))
        return [rtn, blc, clh, block]
            
val = Val()
clf_cut = ColorFilterCut()
alg = Target()

firstBar = FirstBarDetection()
