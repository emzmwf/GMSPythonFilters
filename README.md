# GMSPythonFilters
Collection of scripts for filtering of TEM images in Gatan Microscopy Suite using Python libraries

GMS_Py_Denoise_NLMeans - scikit-image implementation of non linear means denoising. VERY slow, but good removal of salt and pepper noise while keeping edges

GMS_CV2Filters0.4 - applies six different filters using opencv-python to the front-most image in Gatan Digital Micrograph (Convolution, Blur, Median Blur, Gaussian Blur, Bilateral, Wiener), copies tags and calibrations, and displays in new workspace
