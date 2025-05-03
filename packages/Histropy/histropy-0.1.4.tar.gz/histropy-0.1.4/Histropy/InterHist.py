from tabulate import tabulate
import numpy as np
import easygui
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import TextBox
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from Histropy.ImageCalculator import ImageCalculator
from matplotlib.widgets import Button
import matplotlib.image as mpimg

class InterHist:
    mpl.use('TkAgg')
    """
        The InterHist class uses MatPlotLib's widgets to create an interactive histogram workspace for Histropy.
    """
    def __init__(self, file_path, lbound=0, rbound=255, overlay_image_list=[]):
        """
        Initializes an InterHist object, defines attributes, and sets up the display

        Args:
            file_path (str): The file path of the main image to be analyzed in Histropy when the program is opened.
        """
        self.fpath = file_path
        #Creating an ImageCalculator from the inputted image
        self.image_calculator = ImageCalculator(file_path)
        
        #Creating subplot mosaic
        self.fig, self.ax = plt.subplot_mosaic(
            [
                ['main', 'scale', 'image1'],
                ['main', 'bounds', 'image2'],
                ['main', 'display', 'image3'],
                ['main', 'overlays', 'image4']
            ],
            width_ratios=[4, 1.25, 0.75],
            layout='constrained',
        )
        #Defining list of colors to use for overlayed plots
        self.__color_list = [
            (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),   # tab:blue
            (1.0, 0.4980392156862745, 0.054901960784313725),                 # tab:orange
            (0.17254901960784313, 0.6274509803921569, 0.17254901960784313),  # tab:green
            (0.8392156862745098, 0.15294117647058825, 0.1568627450980392),   # tab:red
            (0.5803921568627451, 0.403921568627451, 0.7411764705882353),     # tab:purple
            (0.5490196078431373, 0.33725490196078434, 0.29411764705882354),  # tab:brown
            (0.8901960784313725, 0.4666666666666667, 0.7607843137254902),    # tab:pink
            (0.4980392156862745, 0.4980392156862745, 0.4980392156862745),    # tab:gray
            (0.7372549019607844, 0.7411764705882353, 0.13333333333333333),   # tab:olive
            (0.09019607843137255, 0.7450980392156863, 0.8117647058823529),   # tab:cyan
            (1.0, 0.4980392156862745, 0.4470588235294118),                    # xkcd:coral
            (0.7490196078431373, 0.9921568627450981, 0.23529411764705882),   # xkcd:lime
            (0.6901960784313725, 0.18823529411764706, 0.3764705882352941),   # xkcd:maroon
            (0.29411764705882354, 0.0, 0.5098039215686274),                   # xkcd:indigo
            (1.0, 0.8431372549019608, 0.0),                                   # xkcd:gold
            (0.8549019607843137, 0.4392156862745098, 0.8392156862745098),    # xkcd:orchid
            (0.4980392156862745, 0.4980392156862745, 0.6901960784313725),    # xkcd:slate
            (0.25098039215686274, 0.8784313725490196, 0.8156862745098039),   # xkcd:turquoise
            (0.5607843137254902, 0.47058823529411764, 0.7372549019607844),   # xkcd:violet
            (0.9607843137254902, 0.8784313725490196, 0.7019607843137254),    # xkcd:wheat
            (0.8235294117647058, 0.7058823529411765, 0.5490196078431373),    # xkcd:tan
            (0.0, 0.5019607843137255, 0.5019607843137255),                    # xkcd:teal
            (0.5294117647058824, 0.807843137254902, 0.9215686274509803)      # xkcd:sky blue
        ]
        self.num_plots = 0
        #Set up subplots and on-screen text
        self.extract_labels(lbound, rbound)
        self.create_main_hist()
        self.create_image_subplot()
        self.create_scale_subplot()
        self.create_range_subplot()
        self.create_calculation_subplot()
        self.create_overlay_subplot()

        #Create rectangle over main plot showing initial range [min, max]
        self.lower_bound_line = self.ax['main'].axvline(x=self.left_bound, color='b', linestyle='--')
        self.upper_bound_line = self.ax['main'].axvline(x=self.right_bound, color='c', linestyle='--')
        self.rectangle = self.ax['main'].fill_betweenx(self.ax['main'].get_ylim(), self.left_bound, self.right_bound, color='blue', alpha=0.2, linewidth=0)
        self.submit_lower(self.left_bound)

        #Add images from overlay list
        for im in overlay_image_list:
            self.add_image_from_fpath(im)

        #Display plot space
        plt.ion()
        plt.show(block=True)

    def extract_labels(self, lbound=0, rbound=255):
        """
            Extracts the metadata from the ImageCalculator and assigns them to InterHist attributes.
        """
        #Extracting Labels from Metadata
        if(lbound == 0 and rbound == 255):
            self.left_bound = self.image_calculator.min
            self.right_bound = self.image_calculator.max
        else:
            self.left_bound = lbound
            self.right_bound = rbound
        self.last_clicked = self.right_bound
        self.intensity_sum = self.image_calculator.calculate_total_intensity(calculation_range=(0, 256))
        self.size = self.image_calculator.height*self.image_calculator.width
        self.peak = self.image_calculator.y_limit
        self.radio_background = 'lightgoldenrodyellow'
    
    def create_image_subplot(self):
        """
        Sets up the thumbnail image display on the right side of the screen.
        """
        self.ax['image1'].set_title('Image 1', fontdict={'fontsize': mpl.rcParams['axes.titlesize'], 'fontweight': mpl.rcParams['axes.titleweight'], 'color': 'tab:blue', 'verticalalignment': 'baseline', 'horizontalalignment': 'center'})
        self.ax['image1'].set_xticks([])
        self.ax['image1'].set_yticks([])
        img_arr = mpimg.imread(self.fpath)
        is_grayscale = len(img_arr.shape) < 3 or img_arr.shape[2] == 1
        if is_grayscale:
            self.ax['image1'].imshow(img_arr, cmap='gray')
        else:
            self.ax['image1'].imshow(img_arr, cmap=None)
        image_ax_list = ['image2', 'image3', 'image4', "Image 2", "Image 3", "Image 4"]
        for i in range(0, 3):
            self.ax[image_ax_list[i]].set_title(image_ax_list[i+3])
            self.ax[image_ax_list[i]].set_xticks([])
            self.ax[image_ax_list[i]].set_yticks([])
            self.ax[image_ax_list[i]].set_visible(False)
        self.image_axs = image_ax_list
    
    def create_main_hist(self):
        """
            Sets up and adds data to the main histogram plot using the ImageCalculator information.
        """
        #Creating Main Histogram
        data = self.image_calculator.pixel_dict
        color = (self.__color_list[0][0], # redness
         self.__color_list[0][1], # greenness
         self.__color_list[0][2], # blueness
         1 # transparency
         )
        l = self.ax['main'].bar(list(data.keys()), data.values(), color=color, width=1, label='main')
        self.ax['main'].set_xlim(-10, 255+10)
        xpos=np.arange(275)

        #Setting Plot Y-Axis Scale
        self.ax['main'].set_yscale('linear')

        #Making Plot Labels
        self.ax['main'].set_xlabel('Pixel Intensity Values')
        self.ax['main'].set_ylabel('Number of Pixels')
        self.ax['main'].set_title(self.image_calculator.filename)

    def create_scale_subplot(self):
        """
            Sets up the scale subplot with buttons to switch scale and an input box for a y-limit.
        """
        #Making scale switch buttons
        self.ax['scale'].set_facecolor(self.radio_background)
        self.ax['scale'].set_title('Scale')
        self.radio = RadioButtons(self.ax['scale'], ('linear', 'log base 10'))
        inset_axes_1 = inset_axes(self.ax['scale'], width="30%", height="15%", loc='lower right')
        self.radio.on_clicked(self.reset_scale)

        #Creating y-limit input
        self.text3 = TextBox(inset_axes_1, 'Y-Axis Limit', initial=int(self.ax['main'].get_ylim()[1]), label_pad=0.09)
        self.text3.on_submit(self.submit_ylim)

    def create_range_subplot(self):
        """
            Sets up the range subplot with text fields to enter bounds.
        """
        #Setting up subplot background
        self.ax['bounds'].set_facecolor(self.radio_background)
        self.ax['bounds'].set_title('Intensity Range')
        self.ax['bounds'].set_xticks([])
        self.ax['bounds'].set_yticks([])
        #Creating individual fields
        inset_axes_1 = inset_axes(self.ax['bounds'], width="40%", height="25%", loc='center right')
        self.text1 = TextBox(inset_axes_1, 'Upper Bound', initial=self.right_bound, label_pad=0.09)
        self.text1.label.set_color('c')
        inset_axes_2 = inset_axes(self.ax['bounds'], width="40%", height="25%", loc='upper right')
        self.text2 = TextBox(inset_axes_2, 'Lower Bound', initial=self.left_bound, label_pad=0.09)
        self.text2.label.set_color('b')
        #Connecting Inputs to actions
        plt.connect('button_press_event', self.on_click)
        self.text2.on_submit(self.submit_lower)
        self.text1.on_submit(self.submit_higher)

    def create_calculation_subplot(self):
        """
            Sets up the calculation subplot with text displays for the different metrics.
        """
        #Setting up subplot background
        self.ax['display'].set_facecolor(self.radio_background)
        self.ax['display'].set_title('Calculations on Intensity Range')
        self.ax['display'].set_xticks([])
        self.ax['display'].set_yticks([])
        #Making individual text displays
        self.t1 = self.ax['display'].text(0.055, .84, f'# pixels on range: {self.size}')
        self.t2 = self.ax['display'].text(0.055, .69, f'% of all pixels on range: {100}')
        self.t3 = self.ax['display'].text(0.055, .54, f'Entropy on range: {round(self.image_calculator.calculate_entropy_value(), 3)}')
        self.t4 = self.ax['display'].text(0.055, .39, f'Mean on range: {round(self.image_calculator.calculate_mean(), 3)}')
        self.t5 = self.ax['display'].text(0.055, .24, f'RMS contrast on range: {round(self.image_calculator.get_rms_contrast(), 3)}')
        self.t6 = self.ax['display'].text(0.055, .09, f'Total intensity on range: {self.intensity_sum}')
   
    def create_overlay_subplot(self):
        """
            Sets up overlay subplot with buttons to add images or clear all images.
        """
        #Setting up subplot background
        self.ax['overlays'].set_facecolor(self.radio_background)
        self.ax['overlays'].set_title('Histogram Overlays')
        self.ax['overlays'].set_xticks([])
        self.ax['overlays'].set_yticks([])
        #Making buttons
        add_image_axes = inset_axes(self.ax['overlays'], width="30%", height="15%", loc='upper left')
        self.baddimage = Button(add_image_axes, 'Add Image')
        self.baddimage.on_clicked(self.add_image)
        clear_overlays_axes = inset_axes(self.ax['overlays'], width="40%", height="15%", loc='upper right')
        self.bclearoverlays = Button(clear_overlays_axes, 'Clear Overlays')
        self.bclearoverlays.on_clicked(self.clear_images)
    
    def reset_scale(self, scl):
        """
        Handles request to switch the scale based on radio button input from scale subplot.

        Args:
            scl (str): The scale to switch the plot to.
        """
        if(scl=='log base 10'):
            scl = 'log'
        self.ax['main'].set_yscale(scl)
        self.ax['main'].relim()
        self.ax['main'].autoscale()
        self.submit_ylim('')
        plt.draw()

    def submit_lower(self, text):
        """
        Handles request to reset lower bound and adjusts calculations subplot & main plot rectangle bounds display accordingly.

        Args:
            text (str): A str value of the new lower bound from the text input (int).
        """
        self.left_bound = int(text)
        if(self.lower_bound_line != None):
            self.lower_bound_line.remove()
        self.lower_bound_line = self.ax['main'].axvline(x=self.left_bound, color='b', linestyle='--')
        self.add_rectangle()
        calc_range = range(self.left_bound, self.right_bound+1)
        dict, ans = self.image_calculator.pixels_on_range(calc_range)
        self.t1.set_text(str(f'# pixels on range: {ans}'))
        self.t2.set_text(str(f'% of all pixels on range: {round(100*ans/self.size, 7)}'))
        self.t3.set_text(str(f'Entropy on range: {round(self.image_calculator.calculate_entropy_value(calc_range), 7)}'))
        self.t4.set_text(str(f'Mean on range: {round(self.image_calculator.calculate_mean(calc_range), 7)}'))
        self.t5.set_text(str(f'RMS contrast on range: {round(self.image_calculator.get_rms_contrast(calc_range), 7)}'))
        self.t6.set_text(str(f'Total intensity on range: {self.image_calculator.calculate_total_intensity(calc_range)}'))
        if self.num_plots > 0:
            self.update_plot(calc_range)
        plt.draw()

    def submit_higher(self, text):
        """
        Handles request to reset upper bound and adjusts calculations subplot & main plot rectangle bounds display accordingly.

        Args:
            text (str): A str value of the new upper bound from the text input (int).
        """
        self.right_bound = int(text)
        if(self.upper_bound_line != None):
            self.upper_bound_line.remove()
        self.upper_bound_line = self.ax['main'].axvline(x=self.right_bound, color='c', linestyle='--')
        self.add_rectangle()
        calc_range = range(self.left_bound, self.right_bound+1)
        dict, ans = self.image_calculator.pixels_on_range(calc_range)
        self.t1.set_text(str(f'# pixels on range: {ans}'))
        self.t2.set_text(str(f'% of all pixels on range: {round(100*ans/self.size, 7)}'))
        self.t3.set_text(str(f'Entropy on range: {round(self.image_calculator.calculate_entropy_value(calc_range), 7)}'))
        self.t4.set_text(str(f'Mean on range: {round(self.image_calculator.calculate_mean(calc_range), 7)}'))
        self.t5.set_text(str(f'RMS contrast on range: {round(self.image_calculator.get_rms_contrast(calc_range), 7)}'))
        self.t6.set_text(str(f'Total intensity on range: {self.image_calculator.calculate_total_intensity(calc_range)}'))
        if self.num_plots > 0:
            self.update_plot(calc_range)
        plt.draw()

    def submit_ylim(self, text):
        """
        Handles input for setting a new limit on the y-axis.

        Args:
            text (Event): Text input event in scale subplot.
        """
        if(text==''):
            self.ax['main'].autoscale()
            self.text3.set_val(int(round(self.ax['main'].get_ylim()[1])))
        else:
            self.ax['main'].set_ylim(0, int(round(float(text))))
            self.text3.set_val(text)
        self.add_rectangle()

    def on_click(self, event):
        """
        Handles mouse clicking on main plot to update range values.

        Args:
            event (Event): Mouse click event.
        """
        if event.inaxes is self.ax['main']:
            x = event.xdata
            idx = int(x.round())
            if(idx > self.last_clicked):
                self.text1.set_val(idx)
                self.submit_higher(str(idx))
            else:
                self.text2.set_val(idx)
                self.submit_lower(str(idx))
            self.last_clicked = idx

    def add_rectangle(self):
        """
            Draws the attribute rectangle on the main plot (used to display range bounds).
        """
        if(self.rectangle != None):
            self.rectangle.remove()
        i = int(self.text3.text)
        self.rectangle = self.ax['main'].fill_betweenx((0.0, i), self.left_bound, self.right_bound, color='blue', alpha=0.2, linewidth=0)
        plt.draw()    


    def add_image(self, event):
        """
        Handles request to add new image to overlay, called upon "Add Image" button being pressed in the overlays subplot.

        Args:
            event (Event): Button press event for "Add Image" in overlays subplot.
        """
        #Increase number of plots
        self.num_plots+=1
        #Create a new imagecalculator object for the new image
        path = easygui.fileopenbox()
        filename = path.rsplit('/', 1)[-1]
        im = ImageCalculator(path)
        data = im.pixel_dict
        #Set up color of the new histogram
        color = (self.__color_list[self.num_plots][0], # redness
         self.__color_list[self.num_plots][1], # greenness
         self.__color_list[self.num_plots][2], # blueness
         0.6 # transparency
         )
        #Set up color of the new plot text & other values
        color2 = (self.__color_list[self.num_plots][0], # redness
         self.__color_list[self.num_plots][1], # greenness
         self.__color_list[self.num_plots][2], # blueness
         1 # transparency
         )
        #Plot overlaid histogram
        self.ax['main'].bar(list(data.keys()), data.values(), antialiased=False, color=color, width=1)
        #Rest y-limit
        self.submit_ylim(str(round(self.ax['main'].get_ylim()[1])))
        self.add_rectangle()
        if(self.num_plots==1):
            #Set up a calculator to display image 2's information
            self.calculator2 = ImageCalculator(path)
            newt = self.ax['overlays'].text(0.055, 0.72, filename[:34], color=color2)
            self.nump2 = self.ax['overlays'].text(0.055, 0.6, "A", color=color2)
            self.percentp2 = self.ax['overlays'].text(0.055, 0.5, "B", color=color2)
            self.ep2 = self.ax['overlays'].text(0.055, 0.4, "C", color=color2)
            self.meap2 = self.ax['overlays'].text(0.055, 0.3, "D", color=color2)
            self.conp2 = self.ax['overlays'].text(0.055, 0.2, "E", color=color2)
            self.inp2 = self.ax['overlays'].text(0.055, 0.1, "F", color=color2)
            self.plots = [newt, self.nump2, self.percentp2, self.ep2, self.meap2, self.conp2, self.inp2]
            self.size2 = self.calculator2.height*self.calculator2.width
            calc_range = range(self.left_bound, self.right_bound+1)
            self.update_plot(calc_range)
            plt.draw()
        else:
            #Clear old imagecalculator information and have overlays only display the file names
            self.nump2.set_visible(False)
            self.percentp2.set_visible(False)
            self.ep2.set_visible(False)
            self.meap2.set_visible(False)
            self.conp2.set_visible(False)
            self.inp2.set_visible(False)
            newt = self.ax['overlays'].text(0.055, 0.72-(self.num_plots-1)*.12, filename[:34], color=color2)
            self.plots.append(newt)
        #Set up display thumbnails for the first 3 images that are overlaid
        for i in range(0, 3):
            if not self.ax[self.image_axs[i]].get_visible():
                self.ax[self.image_axs[i]].set_visible(True)
                self.ax[self.image_axs[i]].set_title(self.image_axs[i+3], fontdict={'fontsize': mpl.rcParams['axes.titlesize'], 'fontweight': mpl.rcParams['axes.titleweight'], 'color': color2, 'verticalalignment': 'baseline', 'horizontalalignment': 'center'})
                self.ax[self.image_axs[i]].set_xticks([])
                self.ax[self.image_axs[i]].set_yticks([])
                img_arr = mpimg.imread(path)
                is_grayscale = len(img_arr.shape) < 3 or img_arr.shape[2] == 1
                if is_grayscale:
                    self.ax[self.image_axs[i]].imshow(img_arr, cmap='gray')
                else:
                    self.ax[self.image_axs[i]].imshow(img_arr, cmap=None)
                plt.draw()
                break

    def add_image_from_fpath(self, path):
        #Increase number of plots
        self.num_plots+=1
        #Create a new imagecalculator object for the new image
        filename = path.rsplit('/', 1)[-1]
        im = ImageCalculator(path)
        data = im.pixel_dict
        #Set up color of the new histogram
        color = (self.__color_list[self.num_plots][0], # redness
         self.__color_list[self.num_plots][1], # greenness
         self.__color_list[self.num_plots][2], # blueness
         0.6 # transparency
         )
        #Set up color of the new plot text & other values
        color2 = (self.__color_list[self.num_plots][0], # redness
         self.__color_list[self.num_plots][1], # greenness
         self.__color_list[self.num_plots][2], # blueness
         1 # transparency
         )
        #Plot overlaid histogram
        self.ax['main'].bar(list(data.keys()), data.values(), antialiased=False, color=color, width=1)
        #Rest y-limit
        self.submit_ylim(str(round(self.ax['main'].get_ylim()[1])))
        self.add_rectangle()
        if(self.num_plots==1):
            #Set up a calculator to display image 2's information
            self.calculator2 = ImageCalculator(path)
            newt = self.ax['overlays'].text(0.055, 0.72, filename[:34], color=color2)
            self.nump2 = self.ax['overlays'].text(0.055, 0.6, "A", color=color2)
            self.percentp2 = self.ax['overlays'].text(0.055, 0.5, "B", color=color2)
            self.ep2 = self.ax['overlays'].text(0.055, 0.4, "C", color=color2)
            self.meap2 = self.ax['overlays'].text(0.055, 0.3, "D", color=color2)
            self.conp2 = self.ax['overlays'].text(0.055, 0.2, "E", color=color2)
            self.inp2 = self.ax['overlays'].text(0.055, 0.1, "F", color=color2)
            self.plots = [newt, self.nump2, self.percentp2, self.ep2, self.meap2, self.conp2, self.inp2]
            self.size2 = self.calculator2.height*self.calculator2.width
            calc_range = range(self.left_bound, self.right_bound+1)
            self.update_plot(calc_range)
            plt.draw()
        else:
            #Clear old imagecalculator information and have overlays only display the file names
            self.nump2.set_visible(False)
            self.percentp2.set_visible(False)
            self.ep2.set_visible(False)
            self.meap2.set_visible(False)
            self.conp2.set_visible(False)
            self.inp2.set_visible(False)
            newt = self.ax['overlays'].text(0.055, 0.72-(self.num_plots-1)*.12, filename[:34], color=color2)
            self.plots.append(newt)
        #Set up display thumbnails for the first 3 images that are overlaid
        for i in range(0, 3):
            if not self.ax[self.image_axs[i]].get_visible():
                self.ax[self.image_axs[i]].set_visible(True)
                self.ax[self.image_axs[i]].set_title(self.image_axs[i+3], fontdict={'fontsize': mpl.rcParams['axes.titlesize'], 'fontweight': mpl.rcParams['axes.titleweight'], 'color': color2, 'verticalalignment': 'baseline', 'horizontalalignment': 'center'})
                self.ax[self.image_axs[i]].set_xticks([])
                self.ax[self.image_axs[i]].set_yticks([])
                img_arr = mpimg.imread(path)
                is_grayscale = len(img_arr.shape) < 3 or img_arr.shape[2] == 1
                if is_grayscale:
                    self.ax[self.image_axs[i]].imshow(img_arr, cmap='gray')
                else:
                    self.ax[self.image_axs[i]].imshow(img_arr, cmap=None)
                plt.draw()
                break

    def clear_images(self, event):
        """
        Handles request to remove overlaid images/histograms. Called when "Clear Overlays" button is pressed in overlays subplot.

        Args:
            event (Event): Button press event for "Clear Overlays" in overlays subplot.
        """
        self.num_plots = 0
        self.ax['main'].cla()
        for txt in self.plots:
            txt.set_visible(False)
        self.create_main_hist()
        for i in range(0, 3):
            self.ax[self.image_axs[i]].set_visible(False)
        #Redraw bound lines
        self.lower_bound_line = self.ax['main'].axvline(x=self.left_bound, color='b', linestyle='--')
        self.upper_bound_line = self.ax['main'].axvline(x=self.right_bound, color='c', linestyle='--')
        self.rectangle = self.ax['main'].fill_betweenx(self.ax['main'].get_ylim(), self.left_bound, self.right_bound, color='blue', alpha=0.2, linewidth=0)

    def update_plot(self, calc_range):
        """
        Update's plot values for the overlaid calculation subplot based on new values of range.

        Args:
            calc_range (range): The new range of the image to calculate over based on inputted bounds.
        """
        dict, ans = self.calculator2.pixels_on_range(calc_range)
        self.nump2.set_text(str(f'# pixels on range: {ans}'))
        self.percentp2.set_text(str(f'% of all pixels on range: {round(100*ans/self.size2, 7)}'))
        self.ep2.set_text(str(f'Entropy on range: {round(self.calculator2.calculate_entropy_value(calc_range), 7)}'))
        self.meap2.set_text(str(f'Mean on range: {round(self.calculator2.calculate_mean(calc_range), 7)}'))
        self.conp2.set_text(str(f'RMS contrast on range: {round(self.calculator2.get_rms_contrast(calc_range), 7)}'))
        self.inp2.set_text(str(f'Total intensity on range: {self.calculator2.calculate_total_intensity(calc_range)}'))
