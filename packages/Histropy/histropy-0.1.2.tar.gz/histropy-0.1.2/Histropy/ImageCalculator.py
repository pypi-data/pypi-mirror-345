from tabulate import tabulate
import PIL
import numpy as np
import math

class ImageCalculator:
    """
        The ImageCalculator class creates calculator objects to extract numerical information for analysis of images.
    """
    def __init__(self, file_path):
        """
        Initialized an ImageCalculator using the given file path to open an image for analysis and setting up a dict of pixel values.

        Args:
            file_path (str): The file path of the image to be analyzed.
        """        
        self.filename = file_path.rsplit('/', 1)[-1]
        self.image = PIL.Image.open(file_path)
        image_transformed = self.__preprocessing()
        self.pixels = image_transformed.load()
        self.height, self.width = image_transformed.size
        self.__get_histogram_data(self.height, self.width)
        self.y_limit = max(self.pixel_dict.values())

    def __preprocessing(self):
        """
        Converts the object's image into grayscale if it is in color.

        Returns:
            Image: A grayscale version of the object's PIL Image.
        """        
        img = self.image
        if img.mode != 'L':
            img = PIL.ImageOps.grayscale(img)
        return img
    
    def pixels_on_range(self, range_to_calculate):
        """
        Returns the number of pixels on a given range as well as a dictionary trimmed to the range of pixels we specify.

        Args:
            range_to_calculate (range): The range of pixels values [0, 255] that we want to recieve a dict and count of.

        Returns:
            dict, int: The dict containing the pixels with values within range_to_calculate as well as the total number of pixels within that range.
        """        
        new_pix = {k: self.pixel_dict[k] for k in self.pixel_dict.keys() & list(range_to_calculate)}
        total_pixels = sum(new_pix.values())
        return new_pix, total_pixels
    
    #
    def __get_histogram_data(self, h, w):
        """
        Creates histogram dictionary from image pixel data and saves it in the object's dict attribute.

        Args:
            h (int): The height of the object's image.
            w (int): THe width of the object's image.
        """        
        pixel_vals = {}
        sum = 0
        maximum = -256
        minimum = 256
        pix = self.pixels
        #Add each pixel to the dictionary
        for i in range(0, h):
            for j in range(0, w):
                value = round(pix[i, j])
                if(value > maximum):
                    maximum = value
                if(value < minimum):
                    minimum = value
                sum+= value
                if value in pixel_vals:
                    pixel_vals[value] = pixel_vals[value]+1
                else:
                    pixel_vals[value] = 1
        #Sort the dictionary by key value
        myKeys = list(pixel_vals.keys())
        myKeys.sort()
        sorted_pixel_vals = {i: pixel_vals[i] for i in myKeys}
        #Set metadata for dict
        self.min = minimum
        self.max = maximum
        self.pixel_dict = sorted_pixel_vals
        self.mean = sum/(h*w)

    def calculate_total_intensity(self, calculation_range=None):
        """
        Calculates the sum total intensity on a given range.

        Args:
            calculation_range (range, optional): The range to calculate over. Defaults to None which is taken as the whole image's range.

        Returns:
            int: The total intensity on calculation_range. (The sum of all pixel values in a given range).
        """        
        if calculation_range is None:
            calculation_range = (self.min, self.max+1)
        newpix, ct = self.pixels_on_range(calculation_range)
        if(ct==0):
            return 0
        intensity_total = sum(intensity*count for intensity,count in newpix.items())
        return intensity_total
        
    def calculate_mean(self, calculation_range=None):
        """
        Calculates the mean pixel value on a given range

        Args:
            calculation_range (range, optional): The range to calculate over. Defaults to None which is taken as the whole image's range.

        Returns:
            int: The mean pixel value on calculation_range.
        """        
        if calculation_range is None:
            return self.mean
        else:
            intensity_total = self.calculate_total_intensity(calculation_range)
            pix, ct = self.pixels_on_range(calculation_range)
            if(ct==0):
                return 0
            return intensity_total/ct
        
    # Method to 
    def calculate_entropy_value(self, calculation_range=None):
        """
        Calculates simplified shannon entropy values using the equation outlined in https://doi.org/10.48550/arXiv.2404.13497

        Args:
            calculation_range (range, optional):  The range to calculate over. Defaults to None which is taken as the whole image's range.

        Returns:
            int: The calculated entropy value over calculation_range.
        """        
        sum=0
        if calculation_range is None:
            num_pixels = self.height*self.width
            pi_vals = self.pixel_dict
        else:
            pi_vals, num_pixels = self.pixels_on_range(calculation_range)
        for key in pi_vals.keys():
            value = pi_vals[key]/num_pixels
            if value != 0:
                sum+= (value*np.log2(value))
        if(sum == 0):
            return 0
        return sum*-1
    
    def __get_std_dev(self, calculation_range=None):
        """
        Calculates the standard deviation of a range of pixel.

        Args:
            calculation_range (range, optional): The range to calculate over. Defaults to None which is taken as the whole image's range.

        Returns:
            int: The standard deviation of the dictionary values within calculation_range (aka the standard deviation of the section of our histogram defined by calculation_range).
        """        
        mean = self.calculate_mean(calculation_range)
        num_pix = -1
        sum = 0
        for i in range(0, self.height):
            for j in range(0, self.width):
                if calculation_range == None or self.pixels[i, j] in calculation_range:
                    sum += pow(self.pixels[i, j]-mean, 2)
                    num_pix+=1
        return math.sqrt(sum/(num_pix))

    def get_maximum(self, calculation_range=None):
        """
        Returns the maximum pixel value on a given range.

        Args:
            calculation_range (range, optional): The range to consider finding the max pixel value on. Defaults to None which is taken as the whole image's range.

        Returns:
            int: The maximum pixel value on calculation_range.
        """        
        if calculation_range is None:
            return self.max
        else:
            newpix, total = self.pixels_on_range(calculation_range)
            return max(newpix.keys())
        
     
    def get_rms_contrast(self, calculation_range=None):
        """
        Calculates the rms contrast of a range of pixels.

        Args:
            calculation_range (range, optional): The range to calculate over. Defaults to None which is taken as the whole image's range.

        Returns:
            _type_: The rms contrast on calculation_range.
        """        
        stddev = self.__get_std_dev(calculation_range)
        return stddev/255
    
