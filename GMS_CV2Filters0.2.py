'''

# Demo of OpenCV scripts
# last updated 28th April 2023 - MWF
# Note Feb 2024 - confirmed to work with GMS v 3.60
# Convolution, Blur, Median Blur, Gaussian Blur, Bilateral
#
#Filtered images have the same tags and calibration as the original
#file

# Note - workspace management, show and arrange files in new 
# workspace - appears to be not currently supported via Python only
# so requires a hybrid script. 
'''

import DigitalMicrograph as DM
import cv2
import numpy as np

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

 


# Process the front image
dmImg = DM.GetFrontImage() # Get reference to front most image
dmImgData = dmImg.GetNumArray() # Get NumpyArray to image data

#Get the image document and its window
imageDoc = DM.GetFrontImageDocument()
imDocWin = imageDoc.GetWindow()

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

# Apply Convolution
kernel = np.ones((5,5),np.float32)/25
Conv = cv2.filter2D(result,-1,kernel)

# Apply Blur
blur = cv2.blur(result,(5,5))

#Apply Median Blur
median_blur= cv2.medianBlur(result, 3)

# Apply Gaussian
Gaus = cv2.GaussianBlur(result,(5,5),0)

# Apply Bilateral
bil = cv2.bilateralFilter(result,9,75,75)

# from python we can get the original workspace 
# that has the front image document
# find out what workspace that is in
wsID = imageDoc.GetWorkspace() 

# Make new workspace - the dm script version of this would be
#number wsID_src = WorkSpaceGetActive()
#number wsID_Filter = WorkSpaceAdd( WorkSpaceGetIndex(wsID_src) + 1 )
#WorkSpaceSetActive( wsID_Filter )
#WorkspaceSetName( wsID_Filter , "Filered" )
# and use a temporary tag to pass the id number to python

dmscript = 'number wsID_src = WorkSpaceGetActive()' + '\n'
dmscript += 'number wsID_Filter = WorkSpaceAdd( WorkSpaceGetIndex(wsID_src) + 1 )' + '\n'
dmscript += 'WorkspaceSetName( wsID_Filter , "Filtered" )' + '\n'
dmscript += 'TagGroup tg = GetPersistentTagGroup( ) ' + '\n'
dmscript += 'tg.TagGroupSetTagAsString( "DM2Python CV2", ""+wsID_Filter )' + '\n'

DM.ExecuteScriptString( dmscript ) 
# Now get the wsID_Filter value from the temporary tag
TGp = DM.GetPersistentTagGroup()
returnVal, val = TGp.GetTagAsText('DM2Python CV2')

wsIDF = wsID
print("\n ReturnVal is "+str(returnVal))

if (returnVal == 1):
    wsIDF = val
    print(wsIDF)
    
# And now remove the temporary tag
DM.GetPersistentTagGroup().DeleteTagWithLabel("DM2Python CV2")

print("\n wsIDF is "+str(wsIDF))

### def to move the newly displayed image to wsIDF
def CV2ImgMove(wsFilt):
    imageDocA = DM.GetFrontImageDocument()
    imageDocA.MoveToWorkspace(int(wsFilt))

# Show as separate DM image
DM.CreateImage(Conv.copy()).ShowImage()
del Conv    # Remove data from memory no longer needed
DMImgC = DM.GetFrontImage() # Get reference to the new image which is now in front
DMImgC.SetName("Convolution " + dmImg.GetName())
Calibration_Copy(dmImg, DMImgC)
Tag_Copy(dmImg, DMImgC )#, 'Copied over' )
#Move to new workspace
#imageDocA = DM.GetFrontImageDocument()
#imageDocA.MoveToWorkspace(int(wsIDF))
CV2ImgMove(wsIDF)


DM.CreateImage(blur.copy()).ShowImage()
del blur    # Remove data from memory no longer needed
DMImgBlu = DM.GetFrontImage() # Get reference to the new image which is now in front
DMImgBlu.SetName("Blur " + dmImg.GetName())
Calibration_Copy(dmImg, DMImgBlu)
Tag_Copy(dmImg, DMImgBlu )#, 'Copied over' )
CV2ImgMove(wsIDF)


DM.CreateImage(median_blur.copy()).ShowImage()
del median_blur    # Remove data from memory no longer needed
DMImgMB = DM.GetFrontImage() # Get reference to the new image which is now in front
DMImgMB.SetName("Median Blur " + dmImg.GetName())
Calibration_Copy(dmImg, DMImgMB)
Tag_Copy(dmImg, DMImgMB )#, 'Copied over' )
CV2ImgMove(wsIDF)

DM.CreateImage(Gaus.copy()).ShowImage()
del Gaus    # Remove data from memory no longer needed
DMImgGaus = DM.GetFrontImage() # Get reference to the new image which is now in front
DMImgGaus.SetName("Gaussian " + dmImg.GetName())
Calibration_Copy(dmImg, DMImgGaus)
Tag_Copy(dmImg, DMImgGaus )#, 'Copied over' )
CV2ImgMove(wsIDF)

DM.CreateImage(bil.copy()).ShowImage()
del bil    # Remove data from memory no longer needed
DMImgBil = DM.GetFrontImage() # Get reference to the new image which is now in front
DMImgBil.SetName("Bilateral " + dmImg.GetName())
Calibration_Copy(dmImg, DMImgBil)
Tag_Copy(dmImg, DMImgBil )#, 'Copied over' )
CV2ImgMove(wsIDF)


# Rearrange the filtered workspace so all images are visible
dmscript = 'WorkspaceArrange('+str(wsIDF)+',1,1)'
#print(dmscript)
DM.ExecuteScriptString(dmscript)

# now remove python variables, as they exist as images in GMS space now
del DMImgC
del DMImgBlu
del DMImgMB
del DMImgGaus
del DMImgBil


DM.OkDialog("Filtered images in the workspace Filtered")
