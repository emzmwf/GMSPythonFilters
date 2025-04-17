from SimpliPyTEM.Micrograph_class import Micrograph
from SimpliPyTEM.Particle_analysis import Threshold, Find_contours, Collect_particle_data
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io

### Batch particle sizing analysis from dm4 data
### Get optimised values from the JupyterNotebook script
### TEM_Particle_Analysis_(2025).ipynb

#### Define options here ####
#File list TRUE or search dir FALSE
fmode = FALSE
lnormval = 6
Gaussval = 7
useautomated = TRUE
valpick = 1017
PixWd = 50

uservars = {
	'lnormval': lnormval,
	'Gaussval': Gaussval,
	'useautomated': useautomated,
	'valpick': valpick,
	'PixWd': PixWd
}

##############################################
###  DEFs
##############################################
# Optimisation check TO BE DONE:
#Some imports are currently inside functions to restrict visibility / reduce initial startup time
#Although Python's interpreter is optimized to not import the same module multiple times, 
#repeatedly executing an import statement can seriously affect performance in some circumstances.
#

def LoadList():
	#loads in file, returns array
	#Includes - to open file
	import tkinter as tk
	from tkinter import filedialog
	# Ask for folder
	root = tk.Tk()
	root.withdraw()
	file_path = filedialog.askopenfilename()
	f = open(file_path, 'r')
	#       r	Open for reading plain text
	data = f.read()
	files = data.split("\n")  
	#Parse the file names for the titles
	titles = []
	for x in files:
		tfile = files[x].split("kX_",1)[1])
		tfile2 = tfile.split(".dm4",1)[0])
		titles.append(tfile2)
	returns files, titles

def globList():
	import glob
	# Select directory using tkinter
	dir = "//nmrc-nas.nottingham.ac.uk/data/Instrument Data/2100Plus/LowkV/80 60 40 20 at 250kx Ultrascan"
	# All files and directories ending with .dm4 and that don't begin with a dot:
	files = (glob.glob(str(dir+"/*.dm4"))
	titles = []
	# For loop within files to extract and populate array titles
	for x in files:
		tfile = files[x].split("kX_",1)[1])
		tfile2 = tfile.split(".dm4",1)[0])
		titles.append(tfile2)
	returns files, titles

def GetParticles(files, titles, FileNo, uservars):
	#unpack vars
	lnormval = uservars[0]
	Gaussval = uservars[1]
	useautomated = uservars[2]
	valpick = uservars[3]
	PixWd = uservars[4]
	im = Micrograph(files[FileNo])
	imp = im.local_normalisation(lnormval)
	imp_gaussian= imp.gaussian_filter(Gaussval)
	from scipy import ndimage
	histT = ndimage.histogram(imp_gaussian.image, min = 0, max = imp_gaussian.image.max(), bins = int(imp_gaussian.image.max()))
	figHT, ax = plt.subplots()
	ax.set_title(titles[FileNo]+"Histogram")
	ax.set_xlabel("Pixel values")
	ax.set_ylabel("Frequency")
	figHT.savefig(titles[FileNo]+'IntensityHistogram_FromTIF.png', dpi=200)
	outfile = titles[FileNo]+' IntensityHistogram'
	np.save(outfile, histT)
	# identify peaks and valley, use valley to set threshold value if useautomated selected
	from scipy.signal import find_peaks
	peaks, _ = find_peaks(histT, width=20)
	valley, _ = find_peaks(-histT, width=20, prominence = 500)
	if useautomated == True:
		threshold = valley[0]
	else:
		threshold = valpick
	thresh= Threshold(imp_gaussian.image, threshold)
	#Now find particles
	contours_im, mask =Find_contours(thresh, minsize=PixWd)
	data = Collect_particle_data(contours_im, imp_gaussian.pixel_size)
	# save data as a file
	import json
	with open(titles[FileNo]+'data.json', 'w') as fp:
		json.dump(data, fp)
	fig = plt.figure()
	plt.hist(data['Width'], bins=40)
	plt.xlabel('Particle Width ('+imp_gaussian.pixel_unit+')')
	plt.ylabel('Frequency')
	plt.title(titles[FileNo])
	fig.savefig(titles[FileNo]+'ParticleSizing.png', dpi=200)
	#create lists to store data
	masks = []
	alldata = []
	#Save the data to the empty lists we created
	alldata.append(data)
	masks.append(mask)
	#import the function
	from SimpliPyTEM.Particle_analysis import Convert_to_single_dict
	alldata_dict = Convert_to_single_dict(alldata, combine_data=False)
	import pandas as pd
	df = pd.DataFrame(alldata_dict)
	#export to csv file
	df.to_csv(titles[FileNo]+'Particle_data.csv')


##############################################
###  Main body
##############################################


if fmode == TRUE:
	#Load in text file with file list
	files, titles = LoadList()
else:
	#Ask for directory and use glob
	files, titles = globList()

#Iterate over list and run particle measuring
	for x in files:
		GetParticles(files, titles, x, uservars)
	
	
