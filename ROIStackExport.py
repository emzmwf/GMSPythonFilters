# Python script to run within GMS
# Export selected ROI of a stack as a numpy array

# 2023 04 26 MWF - initial version
# 2023 05 02 MWF - change file selection UI to GMS via DM script, change export to uint32

import DigitalMicrograph as DM
import numpy as np

print("\n numpy array extract from ROI stack script v 20230426\n")

# Select front image
dmImg = DM.GetFrontImage() # Get reference to front most image
dmImgName = dmImg.GetName() 

# Check format of dmImg - Integer 4 unsigned is dm4 default
# If so convert to unsigned integer 8 for processing
type = dmImg.GetDataType() 
## 11 is integer 4

dmImgData = dmImg.GetNumArray() # Get NumpyArray of image data
# numpy array is of shape (Z,Y,X)

'''
if (int(type) == 11):
    dmImgData = dmImgData.astype("float32")
    
   
'''

if (int(type) == 11):
    dmImgData = dmImgData.astype("uint32")

    
# get image display of image
dmImgDisp = dmImg.GetImageDisplay(0)
noOfROI = dmImgDisp.CountROIs()
print("\n number of ROIs found: ")
print(noOfROI)
if(noOfROI<1):
    DM.OkDialog( 'No ROI found' )  
    exit()



# Confirm it is a stack
dimSize = dmImg.GetDimensionSize(2)
if (dimSize<2):
	print("Not a stack")
	exit(0)
	


# Check if ROI present, prompt to draw in and rerun if not
try:
    roi = dmImgDisp.GetROI(0) 
except:
    raise Exception("No ROI found")
    print("No ROI found")

Rect = roi.IsRectangle()
if (Rect == 1):
    print("Rectangle ROI found")

# get coordinates of roi
val, val2, val3, val4= roi.GetRectangle() 

# Crop stack to ROI, creating new stack
print("\n "+str(val))   #//y start
print("\n "+str(val2))  #//x start
print("\n "+str(val3))  #//y end
print("\n "+str(val4))  #//x end


#DMimg2 = DM.CreateImage(np.copy(roi))
#DMimg2 = DM.CreateImage(np.copy(dmImgData))
SliceData = dmImgData[:,int(val2):int(val4),int(val):int(val3)]
DMimg2 = DM.CreateImage(np.copy(SliceData))

DMimg2.SetName(dmImgName+' ROIExtract') 
DMimg2.ShowImage()


# Copy calibrations from old stack to new stack
## defs for calibration and tag copy
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

 
 
def Tag_Copy(image_source, image_dest, subPath = None ):

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

 

Calibration_Copy(dmImg, DMimg2)
Tag_Copy(dmImg, DMimg2 )#, 'Copied over' )

# Prompt to get filename for saving numpy stack

##If no UI selection, hardcode as 
#filename = "C:/Users/emzmwf/Temp/pyarr.npy"


#####
# Use DM script:

dmScript = 'string folder , outputFolder' + '\n'
dmScript += 'if ( !GetDirectoryDialog( "Select folder to save array in" , "" , folder ) ) ' + '\n'
dmScript += '     Result(folder)' + '\n'
dmScript += '     string Dir = folder' + '\n'
dmScript += '     TagGroup tg = GetPersistentTagGroup( ) ' + '\n'
dmScript += '     tg.TagGroupSetTagAsString( "DM2Python String", folder )' + '\n'

#Execute the script
DM.ExecuteScriptString( dmScript )

#Get the selection data into python
TGp = DM.GetPersistentTagGroup()
returnVal, val = TGp.GetTagAsText('DM2Python String')
filename = str(val)+'ROIArray.npy'


'''
## Or use tkinter? When we're already in a UI?
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
file_path = filedialog.askdirectory()

filename = file_path+'/ROIArray.npy'

# HERE!
'''


# Export the numpy array SliceData
np.save(filename, SliceData)

#Delete temp python data
del(dmImgData)
del(SliceData)

DM.OkDialog("File saved to "+filename)
print("File saved to "+filename)