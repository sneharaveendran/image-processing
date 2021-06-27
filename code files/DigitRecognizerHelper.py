#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 18:35:53 2021

@author: surajnair
"""
import os
import pandas as pd
from pandas import DataFrame

from PIL import Image,ImageFilter

import numpy as np

import matplotlib.pyplot as plt
#%matplotlib inline

from datetime import datetime

def identifyImageBorder(url):
    # Read Image 
    img= Image.open(url)
    img = img.resize([1000,500])
    image_file = img.convert('L')
    # Convert Image to Numpy as array 
    image_file = np.array(image_file)  
    # Put threshold to make it binary
    binarr = np.where(image_file>100, 255, 0)
    # Covert numpy array back to.image 
    
    #binimg = Image.fromarray(binarr.astype('uint8'))
    #binimg.save('imagetemp_np.jpg')
    
    crop_iter = 0
    start_crop_ls = []
    fn_start_crop_ls = []
    for xy_rows in range(binarr.shape[0]):
        #print(binarr[x])
        continous_count = 0
        vert_distance = xy_rows + 100
        if (vert_distance < binarr.shape[0]):
            for xy_vert in range(vert_distance,(binarr.shape[0])):
                for xy_cols in range (binarr.shape[1]):
                    if (((binarr[xy_rows][xy_cols]) == 255) & (binarr[xy_vert][xy_cols] == 255)):
                        continous_count = continous_count + 1
                        if (continous_count == 1):
                            crop_iter = crop_iter + 1
                            start_crop_ls = []                        
                            start_crop_ls.append(crop_iter)
                            start_crop_ls.append(xy_rows)
                            start_crop_ls.append(xy_cols)
                            start_crop_ls.append(abs(xy_rows - xy_vert))
                        #if(xy_outer < ((binarr.shape[0]) - 1)):
                           #xy_outer = xy_outer + 1
                    else:
                        if (continous_count > 100) :
                            start_crop_ls.append(xy_vert - 1)
                            start_crop_ls.append(xy_cols - 1)
                            start_crop_ls.append(continous_count)
                            fn_start_crop_ls.append(start_crop_ls)
                        continous_count = 0    


    df = DataFrame(fn_start_crop_ls,columns=['Start Record X #','Start X1', 'Start Y1', 'Vertical Gap', 'Start X2', 'Start Y2','Similarity Count'])
    getSimilardf = df[df['Similarity Count'] == df['Similarity Count'].max()]
    getCropdf = getSimilardf[getSimilardf['Vertical Gap'] == getSimilardf['Vertical Gap'].max()]
    print("Cropping Coordinates =",getCropdf)
    return (getCropdf)


def imageBorderCropfn(url,df):
    img_new= Image.open(url)
    img_new = img_new.resize([1000,500])
    img_new = img_new.crop((df['Start Y1'],df['Start X1'],df['Start Y2'],df['Start X2']))
    img_new = img_new.resize([400,100])
    
    #Save the file in an output Directory
    
    #Split the imagename with extension and folder
    img_folder, img_file_ext = os.path.split(url) 
    
    #Traversing to the parent folder
    img_folder = os.path.normpath(img_folder + os.sep + os.pardir)
    img_folder = os.path.normpath(img_folder + os.sep + os.pardir)
    
    #Split the filename without extension
    img_filename = os.path.splitext(img_file_ext)
    new_img_filename = img_filename[0] + '_B01_'+ datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")+'.jpg'
    
    #Check if the ouput directory is already created, if not create one.
    out_dir = 'ProcessedRectangle_Border'
    out_path = os.path.join(img_folder, out_dir)
    
    if not (os.path.isdir(out_path)):
        os.mkdir(out_path)
        
    new_url = os.path.join(out_path,new_img_filename)
    print("Border Image Saved At=",new_url)
    
    img_new.save(new_url, quality = 95) #default quality is 75
    
    return(img_new,new_url)

def imageFirstDigitDetecttion(url):
    img= Image.open(url)
    img.resize([400,100])
    image_file = img.convert('L')
    image_file = np.array(image_file)
    binarr = np.where(image_file>90, 255, 0)
    
    ls_digit_crop_start =[]
    ls_fn_digit_crop = []
    digit_ident_count = 0
    for cols in range(binarr.shape[1]):
        if (cols >= 40):
            digit_ident_count = 0
            for rows in range(binarr.shape[0]):
                if ((rows > 15) & (rows < 75)):
                    if(binarr[rows][cols] == 0):
                        digit_ident_count = digit_ident_count + 1
                        if (digit_ident_count == 1):
                            if not ls_digit_crop_start:
                                ls_digit_crop_start.append(rows)
                                ls_digit_crop_start.append(cols)
            if (digit_ident_count == 0):
                if ls_digit_crop_start:
                    ls_digit_crop_start.append(rows)
                    ls_digit_crop_start.append(cols)
                    ls_fn_digit_crop.append(ls_digit_crop_start)
                    digit_ident_count = 0
                    ls_digit_crop_start = []
                    break
    
    if ls_fn_digit_crop:
       
        X1 = round(ls_fn_digit_crop[0][0]-(ls_fn_digit_crop[0][0]*0.8))
        Y1 = round(ls_fn_digit_crop[0][1]-(ls_fn_digit_crop[0][1]*0.1))
        X2 = round(ls_fn_digit_crop[0][2]-(ls_fn_digit_crop[0][2]*0.2))
        Y2 = round(ls_fn_digit_crop[0][3]+(ls_fn_digit_crop[0][3]*0.02))           
    
        
        #Save the image in a different folder
        #OS operations 
        
        #Split the imagename with extension and folder
        img_folder, img_file_ext = os.path.split(url)

        #Traversing to the parent folder
        img_folder = os.path.normpath(img_folder + os.sep + os.pardir)
        
        #Split the filename without extension
        img_filename = os.path.splitext(img_file_ext)
        #new_img_filename = os.path.join(img_filename,'_01.jpg')
        new_img_filename = img_filename[0][0:img_filename[0].find("_B01")] + '_D01_'+ datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")+'.jpg'
        
        #Check if the ouput directory is already created, if not create one.
        out_dir = 'Processed_1_Digit'
        out_path = os.path.join(img_folder, out_dir)
        
        if not (os.path.isdir(out_path)):
            os.mkdir(out_path)
            
        new_url = os.path.join(out_path,new_img_filename)
        print("Single Digit Image Saved At=",new_url)
        
        firstDigit= Image.open(url)
        
        firstDigit = firstDigit.crop((Y1,X1,Y2,X2))
        firstDigit = firstDigit.resize([50,75])

        image_file1 = firstDigit.convert('L')
        image_file1 = np.array(image_file1)
        binarr1 = np.where(image_file1 > 90, 255, 0)
        binimg1 = Image.fromarray(binarr1.astype('uint8'))        
        binimg1 = binimg1.filter(ImageFilter.MinFilter(3))        

        binimg1.save(new_url,quality = 95) #default quality is 75
        
        #The below is the RGB color, need to save the binary image
        #firstDigit.save(new_url)        
        
        return(binimg1,new_url)    
    else:
        print("Digit Detection did not happen, lot of noise in the border image")
        return (0,'')
