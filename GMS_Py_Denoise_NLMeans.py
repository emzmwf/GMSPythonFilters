'''
Run denoising NonLocalMeans filter on front most image
VERY SLOW

'''

import DigitalMicrograph as DM
import numpy as np

import skimage
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage.metrics import peak_signal_noise_ratio

if (DM.IsScriptOnMainThread() == False):
	print( ' MatplotLib and scipy scripts require to be run on the main thread.',
		'\n Uncheck the "Execute on Background Thread"',
		'checkbox at the bottom of the Script Window' )
	exit()

dmImg = DM.GetFrontImage() # Get reference to front most image
dmImgData = dmImg.GetNumArray() # Get NumpyArray to image data

print("Please be patient, this is slow")

# Process the data
#sigma_est = np.mean(estimate_sigma(dmImgData, multichannel=False))      ##deprecated from 1.0 on
sigma_est = np.mean(estimate_sigma(dmImgData, channel_axis=-1))        ##channel_axis replaces multichannel

patch_kw = dict(patch_size=5,      # 5x5 patches
                patch_distance=6,  # 13x13 search area
                multichannel=False)    # deprecated in future, change to channel_axis=-1

# slow algorithm
proc = denoise_nl_means(dmImgData, h=1.15 * sigma_est, fast_mode=False,
                           **patch_kw)
                                                     


# Show as separate DM image
# We can not create images from VIEWS so we need to copy first

# Note, does no calibrations
DM.CreateImage(proc.copy()).ShowImage()

DMImg2 = DM.GetFrontImage() # Get reference to the new image which is now in front
DMImg2.SetName("DenoisedNLMeans" + dmImg.GetName())

#Followup - copy calibrations from DM image to new image

#Copy calibrations - use defs
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
 


Calibration_Copy(dmImg, DMImg2)
Tag_Copy(dmImg, DMImg2 )#, 'Tags copied over' )
print("Calibrations and Tags Copied")

# Always explicitly delete Py_Image variables when no longer needed
del dmImg	
del DMImg2
