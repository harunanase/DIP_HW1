from PIL import Image, ImageOps
import numpy as np
import math


"""
    my image lib
"""
class ImageAPI():

    def __init__(self):

        """
            initialized the scalar mapped dict
            scalar range: -20 ~ 20
                        : lowerBound <= scalar < upperBound
        """
        self.__scalarLowerBound = -20
        self.__scalarUpperBound = 20 + 1
        self.__scalarStartPlace = 0




        """
            initialize value mapped dict, linear, alpha=(0.6 ~ 1.4), beta=1, default=[1, 0]
            exponential, alpha=(0.3 ~ 0.5) * (e^-e), beta=-1, default=[1, 0]
            logairthmically, alpha=(1 ~ 80), beta=2, default=[0, 0]
        """
        self.__linearScalarMappedDict = { i:0 for i in range(self.__scalarLowerBound, self.__scalarUpperBound) }
        self.__expScalarMappedDict = { i:0 for i in range(self.__scalarLowerBound, self.__scalarUpperBound) }
        self.__logScalarMappedDict = { i:0 for i in range(self.__scalarLowerBound, self.__scalarUpperBound) }

        linearValue = 0.6
        expValue = 0.3
        logValue = 1


        for i in range(self.__scalarLowerBound, self.__scalarUpperBound):
            self.__linearScalarMappedDict[i] = [linearValue, 1]
            linearValue += 0.02
            
            self.__expScalarMappedDict[i] = [expValue*(math.e**(-math.e)), -1]
            expValue += 0.005

            self.__logScalarMappedDict[i] = [logValue, 2]
            logValue += 2


        self.__linearScalarMappedDict[self.__scalarStartPlace] = [1, 0]
        self.__expScalarMappedDict[self.__scalarStartPlace] = [1, 0]
        self.__logScalarMappedDict[self.__scalarStartPlace] = [0, 0]


        
       


    ########################
    # basic file operation #
    ########################

    def open(self, filename):
        return Image.open(filename)
    
    def save(self, originFile, newFileName):
        originFile.save(newFileName)
    
    def display(self, img):
        img.show()
    
    # normal resize as same ratio, but cannot exceed the size
    def resize(self, img, size):
        ratio = img.width / img.height
        if ratio == 1:
            return img.resize(size)
        elif ratio < 1:
            newSize = (int(size[0]*ratio), int(size[1]))
            return img.resize(newSize)
        else:
            newSize = (int(size[0]), int(size[1]/ratio))
            return img.resize(newSize)


    # convert various format of image
    def pil2np(self, pilImg):
        return np.asarray(pilImg)
    def np2pil(self, npImg):
        return Image.fromarray(np.uint8(npImg))
       



    ###############################
    # contrast adjustment (inner) #
    ###############################
    """
        The following three member function can never be invoked
        explicitly, these are only for inner operations, use the 
        contrast adjustment (outer) instead. 
    """
    
    # linear, y = alpha * x + beta
    def __linear_contrast(self, pilImg, alpha, beta):
        if(alpha == 1 and beta == 0):
            # means the default value, img no changed
            return pilImg

        npImg = self.pil2np(pilImg)
        adjusted = alpha * npImg + beta
        adjusted = self.__pixel_adjustment(adjusted)
        return self.np2pil(adjusted)

    # exponential, y = exp(alpha * x + beta)
    def __exp_contrast(self, pilImg, alpha, beta):
        if(alpha == 1 and beta == 0):
            # means the default value, img no changed
            return pilImg
        npImg = self.pil2np(pilImg)
        adjusted = np.exp(alpha * npImg + beta)
        adjusted = self.__pixel_adjustment(adjusted)
        return self.np2pil(adjusted)

    # logarithmic, y = ln(alpha * x + beta), beta > 1
    def __log_contrast(self, pilImg, alpha, beta):
        if(alpha == 0 and beta == 0):
            # means the default value, img no changed
            return pilImg
        if beta <= 1:
            raise ValueError('Logarithmic Contrast beta value <= 1')
        
        npImg = self.pil2np(pilImg)
        adjusted = 20 * np.log((alpha * npImg + beta)) + 1
        adjusted = self.__pixel_adjustment(adjusted)
        return self.np2pil(adjusted)

 

    # inner method,  pixel adjustment, adjust pixel > 255 || pixel < 0
    # do not invoked it explicitly
    def __pixel_adjustment(self, npImg):
        npImgModifiable = np.array(npImg)
        npImgModifiable[ npImgModifiable>255 ] = 255
        npImgModifiable[ npImgModifiable<0 ] = 0
        return np.asarray(npImgModifiable)
    





    ###############################
    # Contrast adjustment (outer) #
    ###############################
    """
        Use these, not the above. 
        Scalar value range: -20 ~ 20
    """
    def linear_contrast(self, pilImg, scalar):
        return self.__linear_contrast(pilImg, *self.__linearScalarMappedDict[scalar])
    def exp_contrast(self, pilImg, scalar):
        return self.__exp_contrast(pilImg, *self.__expScalarMappedDict[scalar])
    def log_contrast(self, pilImg, scalar):
        return self.__log_contrast(pilImg, *self.__logScalarMappedDict[scalar])






    ################################
    # Zoom in, bilinear adjustment #
    ################################

    # resizing an image 
    # @size: a tuple = (width, height)
    def bilinear_resize(self, pilImg, size):
        # setting resample args to BILEANER, we can resize 
        # an image using bilinear interpolation.
        # see doc: 
        # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.Image.resize 
        return pilImg.resize(size, resample=Image.BILINEAR)


    


    ##########################
    # Histogram Equalization #
    ##########################
    
    def histogram_equalization(self, pilImg):

        # Using Pillow histogram equalized
        # see doc:
        # https://pillow.readthedocs.io/en/stable/reference/ImageOps.html#PIL.ImageOps.equalize
        histogramBefore = pilImg.histogram()
        equalizedImage = ImageOps.equalize(pilImg)       
        histogramAfter = equalizedImage.histogram()
        
        
        return histogramBefore, histogramAfter, equalizedImage

    
