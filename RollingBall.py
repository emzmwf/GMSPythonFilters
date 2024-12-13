# sci-kit image rolling ball script

import DigitalMicrograph as DM
import cv2
import numpy as np
from skimage import data, restoration, util


# defs to copy the calibration data from the original to the new dm file
def Calibration_Copy(image_source, image_dest):

 '''
 Copy dimension and intensity calibration between source and destination.
 On mismatch of number of dimension, prompt user and return.
 '''
 #Count and check that number of dimensions match
 num_dim_s = image_source.GetNumDimensions()
 num_dim_d = image_dest.GetNumDimensions()
 if num_dim_d != num_dim_s:
         DM.OkDialog('Images do not have same number of dimensions!')
         return 
         
 #Copy Dimension Calibrations
 origin = [0 for _ in range(num_dim_s)]
 scale = origin
 power = origin
 unit = ["" for _ in range(num_dim_s)]
 unit2 = unit
 for i in range(num_dim_s):
         origin[i], scale[i], unit[i] =  image_source.GetDimensionCalibration(i, 0)
         image_dest.SetDimensionCalibration(i,origin[i],scale[i],unit[i],0)
         unit2[i], power[i] = image_source.GetDimensionUnitInfo(i)
         image_dest.SetDimensionUnitInfo(i,unit2[i],power[i])
 
 #Copy Intensity Calibrations
 i_scale = image_source.GetIntensityScale()
 i_unit = image_source.GetIntensityUnitString()
 i_origin = image_source.GetIntensityOrigin()
 image_dest.SetIntensityScale(i_scale)
 image_dest.SetIntensityUnitString(i_unit)
 image_dest.SetIntensityOrigin(i_origin)

#
# 
 
def Tag_Copy(image_source, image_dest, subPath = None ):

### Main body of script ###

 '''
 Copy all tags between source and destination.
 If no destination subPath is provided, the destination tags will be replaced.
 '''

 #Copy Tags
 tg_source = image_source.GetTagGroup()
 tg_dest = image_dest.GetTagGroup()
 if ( subPath != None ):
         tg_dest.SetTagAsTagGroup(subPath,tg_source.Clone())
 else:
         tg_dest.DeleteAllTags()
         tg_dest.CopyTagsFrom(tg_source.Clone())


def DoFilter(d):
# Process the front image
    dmImg = DM.GetFrontImage() # Get reference to front most image
    dmImgData = dmImg.GetNumArray() # Get NumpyArray to image data
    
    #Get the image document and its window
    imageDoc = DM.GetFrontImageDocument()
    imDocWin = imageDoc.GetWindow()
    
    #DEVICE = "UNKNOWN"
    DEVICE = "STEM"
    
    #Identify if it is TEM or STEM
    tagPath = 'Microscope Info:Illumination Mode'
    frontImageTags = DM.GetFrontImage().GetTagGroup()
    success, val = frontImageTags.GetTagAsString(tagPath)

    if ( success ):
     DEVICE = val

    else:
     print( 'The tag [',tagPath,'] was not found or not of valid type.', sep="" )

 
    # Check if the front image is a stack
    nDim = dmImg.GetNumDimensions()
    # get the visible slice if so
    if (nDim==3):
        print("three dimensions found")
        DM.OkDialog("Script not currently compatible with stacks")
        exit()
     
    
    
    print(dmImgData.dtype)
    #DM4 file is wrong format for cv2 so need to convert to float32
    result = dmImgData.astype("float32")

    #Aplly rolling ball to STEM image
    if (DEVICE == "STEM"):
        background = restoration.rolling_ball(result, radius = d)
        rbout = result-background

    if (DEVICE == "TEM"):
        #Apply rolling ball to TEM image
        image_inverted = util.invert(result)
        background_inverted = restoration.rolling_ball(image_inverted, radius=d)
        filtered_image_inverted = image_inverted - background_inverted
        rbout = util.invert(filtered_image_inverted)
        background = util.invert(background_inverted)
        

    DM.CreateImage(rbout.copy()).ShowImage()
    del rbout
    DMImgRB = DM.GetFrontImage() # Get reference to the new image which is now in front
    DMImgRB.SetName("BGSub " + dmImg.GetName())
    Calibration_Copy(dmImg, DMImgRB)
    Tag_Copy(dmImg, DMImgRB )#, 'Copied over' )
    
    DM.CreateImage(background.copy()).ShowImage()
    del background
    DMImgRBb = DM.GetFrontImage() # Get reference to the new image which is now in front
    DMImgRBb.SetName("Background " + dmImg.GetName())
    

# Define pixel diamater of filter
bVal, d = DM.GetNumber( 'Please enter radius of rolling ball in pixels', 25 )  
DoFilter(d)
DM.OkDialog("Filtered images in the workspace Filtered")
