""" 
Tadqeeq - Image Annotator Tool
An interactive image annotation tool for efficient labeling.
Developed by Mohamed Behery @ RTR Software Development (2025-04-27).
Licensed under the MIT License.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QShortcut
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QKeySequence, QFont
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
import numpy as np
import os
from functools import reduce
from collections.abc import Iterable
from skimage.io import imsave
from skimage.transform import resize
from scipy.ndimage import binary_fill_holes

from .utils import compute_segment_areas, rgba_array_to_pixmap, \
                   apply_lut_replacement, detect_overlapping_boxes_to_clean, \
                   mask_to_bounding_box, pixmap_to_rgba_array, \
                   locate_all_pixels_via_floodfill
                  
from warnings import filterwarnings
filterwarnings('ignore', category=UserWarning, message='.*low contrast image.*')

class ImageAnnotator(QWidget):
    
    """
    Interactive PyQt5 widget for image annotation using segmentation masks or bounding boxes.

    Args:
        image_path (str): Path to the input image.\n
        annotation_path (str): Path to save/load annotations (.npy, .png, or .txt).\n
        autosave (bool): Enable autosave after edits.\n
        key_sequence_to_save (str): Keyboard shortcut for manual save (default Ctrl+S).\n
        minimum_pen_width (int): Minimum width of drawing pen.\n
        minimum_font_size (int): Minimum font size for floating labels.\n
        hsv_offsets (tuple): HSV color starting offsets.\n
        opacity (float): Opacity for drawn mask overlays.\n
        label_slider_sensitivity (float): Sensitivity when scrolling between label classes.\n
        label_color_pairs (int): Number of distinct label-color pairs (for classes).\n
        floating_label_display_offsets (tuple): Floating label pixel offsets (x, y).\n
        bounding_box_side_length_thresholds (tuple): Minimum and maximum box size allowed.\n
        overlap_vs_smallest_area_threshold (float): Threshold to remove overlapping boxes (by small area).\n
        overlap_vs_union_area_threshold (float): Threshold to remove overlapping boxes (by union area).\n
        corner_label_attached_to_bounding_box (bool): Attach labels to bounding box corners.\n
        verbose (bool): Enable or disable printing log messages.
    """
    
    def __init__(self, 
                 image_path, 
                 annotation_path,
                 autosave=True,
                 key_sequence_to_save='Ctrl+S',
                 minimum_pen_width=5,
                 minimum_font_size=16,
                 hsv_offsets=(0,255,200), 
                 opacity=0.5,
                 label_slider_sensitivity=0.30,
                 label_color_pairs=32,
                 pen_width_slider_sensitivity=0.05,
                 maximum_pen_width_multiplier=3.0,
                 floating_label_display_offsets=(15,30),
                 bounding_box_side_length_thresholds=(25,2000),
                 overlap_vs_smallest_area_threshold=0.95,
                 overlap_vs_union_area_threshold=0.95,
                 corner_label_attached_to_bounding_box=True,
                 verbose=True):
        
        """
        Initialize the image annotator.

        Args:
            image_path (str): Path to the image file.
            annotation_path (str): Path to the annotation file (either .npy or .txt).
            autosave (bool): Whether to automatically save after changes.
            key_sequence_to_save (str): Key combination for saving manually.
            minimum_pen_width (int): Minimum width of annotation pen.
            minimum_font_size (int): Minimum font size for labels.
            hsv_offsets (tuple): HSV color offsets for label coloring.
            opacity (float): Opacity of the drawn annotations.
            label_slider_sensitivity (float): Sensitivity when scrolling through labels.
            label_color_pairs (int): Number of distinct label-color pairs.
            floating_label_display_offsets (tuple): Offset for floating labels when drawing.
            bounding_box_side_length_thresholds (tuple): Minimum and maximum size for bounding boxes.
            overlap_vs_smallest_area_threshold (float): Overlap threshold relative to smallest area to clean boxes.
            overlap_vs_union_area_threshold (float): Overlap threshold relative to union area to clean boxes.
            corner_label_attached_to_bounding_box (bool): Whether labels are attached to bounding boxes.
            verbose (bool): Whether to enable logging messages.
        """
        
        def configure_verbosity():
            self.__verbose = verbose
            self.__previous_message = ''
        
        def disable_maximize_button():
            nonlocal self
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        
        def configure_resize_scheduler():
            nonlocal self
            self.__resize_scheduler = QTimer(self)
            self.__resize_scheduler.setSingleShot(True)
            self.__resize_scheduler.timeout.connect(self.__resize_update_routine)
            
        def configure_saving_parameters():
            nonlocal self, key_sequence_to_save, autosave
            key_sequence_to_save = QKeySequence(key_sequence_to_save)
            self.__key_sequence_to_save = QShortcut(key_sequence_to_save, self)
            self.__key_sequence_to_save.activated.connect(self.save)
            self.__autosave = autosave
            
        def configure_displays():
            nonlocal self
            self.__image_display = QLabel(self)
            self.__label_to_annotate_display = QLabel('Label: N/A', self)
            self.__label_annotated_display = QLabel('Label: N/A', self)
            self.__minimum_widget_size_set = False
            self.floating_label_display_offsets = floating_label_display_offsets
            self.__label_index_hovered_over = -1
            self.__label_displays_configuration_complete = False
            
        def initialize_annotation_pen():
            nonlocal self, minimum_pen_width
            self.__annotation_pen = QPen(Qt.black, minimum_pen_width, Qt.SolidLine)
            self.__last_pen_position = None
            self.__yx_cursor_within_original_image = (0, 0)
            self.__erasing = False
        
        def configure_annotation_parameters():
            nonlocal self, minimum_pen_width, minimum_font_size, hsv_offsets, opacity
            self.__minimum_pen_width = minimum_pen_width
            self.__label_font_size = minimum_font_size
            self.__hsv_offsets = hsv_offsets
            self.__opacity = opacity
            
        def configure_bounding_boxes():
            self.__use_bounding_boxes = os.path.splitext(annotation_path)[-1].lower().strip() == '.txt'
            self.__bounding_box_side_length_thresholds = bounding_box_side_length_thresholds
            self.__overlap_vs_smallest_area_threshold = overlap_vs_smallest_area_threshold
            self.__overlap_vs_union_area_threshold = overlap_vs_union_area_threshold
            self.__corner_label_attached_to_bounding_box = corner_label_attached_to_bounding_box
        
        def initialize_sliders():
            self.__label_slider_enabled = True
            self.__pen_width_slider_sensitivity = pen_width_slider_sensitivity
            self.maximum_pen_width_multiplier = maximum_pen_width_multiplier
            self.pen_width_multiplier_accumulator = 0.0
            self.__label_slider_sensitivity = label_slider_sensitivity
            self.label_color_pairs = label_color_pairs
            self.label_index_accumulator = 0.0
        
        def load_image_annotation_pair():
            self.image_path = image_path
            self.annotation_path = annotation_path
            
        def enable_mouse_tracking():
            self.setMouseTracking(True)
            self.__image_display.setMouseTracking(True)
            self.__label_to_annotate_display.setMouseTracking(True)
            self.__label_annotated_display.setMouseTracking(True)

        super().__init__()
        
        configure_verbosity()
        disable_maximize_button()
        configure_resize_scheduler()
        configure_saving_parameters()
        configure_displays()
        initialize_annotation_pen()
        configure_annotation_parameters()
        configure_bounding_boxes()
        initialize_sliders()
        load_image_annotation_pair()
        enable_mouse_tracking()
        
    @property
    def maximum_pen_width_multiplier(self):
        return self.__maximum_pen_width_multiplier
    
    @maximum_pen_width_multiplier.setter
    def maximum_pen_width_multiplier(self, value):
        self.__maximum_pen_width_multiplier = value
    
    @property
    def verbose(self):
        """Returns the current verbosity setting."""
        return self.__verbose
        
    @property
    def erasing(self):
        """Returns whether erasing mode is currently active."""
        return self.__erasing
    
    @property
    def floating_label_display_offsets(self):
        """Returns floating label display pixel offsets."""
        return self.__floating_label_display_offsets
    
    @floating_label_display_offsets.setter
    def floating_label_display_offsets(self, value):
        """
        Sets the floating label display pixel offsets.

        This setter method updates the pixel offsets for displaying floating 
        labels on the image. The provided value sets the position of the floating 
        labels. If the value is non-empty or non-zero, it enables floating label 
        display. Otherwise, it disables the floating label feature.
        Args:
            value: The pixel offsets (e.g., a tuple or array) for positioning 
                   floating labels on the image. If the value is empty or zero, 
                   floating labels will be disabled.
        """
        self.__floating_label_display_offsets = value
        self.__is_floating_label = bool(self.__floating_label_display_offsets)
    
    @property
    def image_path(self):
        """Returns the currently loaded image as QPixmap."""
        return self.__image_path
    
    @image_path.setter
    def image_path(self, value:str):
        """Sets a new QPixmap image and rescale."""
        self.__image_path = value
        self.image = QPixmap(value)
        
    @property
    def label_index_to_annotate(self):
        """Returns the index of the label currently selected for annotation."""
        return self.__label_index_to_annotate
    
    @label_index_to_annotate.setter
    def label_index_to_annotate(self, value:int):
        """
        Sets the label index for annotation.
        
        This setter method updates the label that is currently selected for 
        annotating objects in the image. The provided index is used to select 
        the appropriate label from the internal list of labels. Additionally, 
        the annotation pen color is updated to match the color associated with 
        the selected label.
        """
        self.__label_index_to_annotate = value
        self.__label_to_annotate = self.labels[value]
        self.__annotation_pen.setColor(self.label_colors[value])
        
    @property
    def label_to_annotate(self):
        """Returns the label currently selected for annotation."""
        return self.__label_to_annotate
        
    @property
    def is_floating_label(self):
        """Returns whether floating label display mode is active."""
        return self.__is_floating_label
    
    @property
    def label_color_pairs(self):
        return self.__label_color_pairs
    
    @label_color_pairs.setter
    def label_color_pairs(self, value):
        """
        Sets the dictionary of label-color pairs and adjusts internal label and color mappings.
        
        This setter method:
        - Accepts a dictionary or iterable input and sets it to the internal `__label_color_pairs` attribute.
        - If the input is a dictionary, it directly updates the `__label_color_pairs`, `__labels`, and `__label_colors` attributes.
        - If the input is an iterable (e.g., list of labels), it automatically generates corresponding colors based on the label indices.
        - If the input is an integer, it generates labels from `0` to `value-1` and assigns unique colors to each label.
        - If the input format is invalid, it raises a `ValueError` indicating that the input should either be an iterable or an integer.
        
        Args:
            value (dict, Iterable, int): 
                - A dictionary of label-color pairs (label: color), 
                - A list of labels to generate colors for, 
                - Or an integer specifying the number of labels to generate with sequential numeric values.
        
        Raises:
            ValueError: If the input is neither an iterable nor an integer.
        """
        try:
            self.__label_color_pairs = dict(value)
            self.__labels = list(self.__label_color_pairs.keys())
            self.__label_colors = list(self.__label_color_pairs.values())
            self.__n_labels = len(self.__labels)
        except TypeError:
            if isinstance(value, Iterable):
                self.labels = list(value)
            elif type(value) is int:
                self.labels = list(range(value))
            else:
                raise ValueError('`labels` should either be `Iterable` or `int`.')
                
    @property
    def labels(self):
        return self.__labels
    
    @labels.setter
    def labels(self, value:list):
        """
        Sets the list of labels and generates corresponding colors for each label.
        
        This setter method:
        - Accepts a list of labels and sets it to the internal `__labels` attribute.
        - Calculates the number of labels (`__n_labels`) from the length of the provided list.
        - Generates a unique color for each label using a color model based on HSV (Hue, Saturation, Value).
        - Maps each label to its corresponding color and stores them in `__label_color_pairs`.
        
        Args:
            value (list): The list of labels to set.
        
        Notes:
            - The color for each label is generated based on its index using a specific HSV color scheme.
            - The generated colors are stored in the internal attributes (`__label_colors`, `__label_color_pairs`).
        """
        def color_from_label_index(index):
            hsv_bin_sizes = (255 - np.array(self.__hsv_offsets)) // self.__n_labels
            h, s, v = map(lambda a, b: a * index + b, hsv_bin_sizes, self.__hsv_offsets)
            return QColor.fromHsv(h, s, v)
        
        self.__labels = value
        self.__n_labels = len(value)
        self.__label_colors = [color_from_label_index(index) for index in range(self.__n_labels)]
        self.__label_color_pairs = dict(zip(self.__labels, self.__label_colors))
    
    @property
    def label_colors(self):
        """Get the list of colors assigned to each label."""
        return self.__label_colors
    
    @property
    def n_labels(self):
        """Get the total number of labels."""
        return self.__n_labels
    
    @property
    def corner_label_attached_to_bounding_box(self):
        """Check if the corner label is attached to the bounding box."""
        return self.__corner_label_attached_to_bounding_box
        
    @property
    def image(self):
        """Get the currently loaded image."""
        return self.__image
    
    @image.setter
    def image(self, value:QPixmap):
        """
        Sets the image and adjusts the internal parameters based on the new image.
        
        This setter method:
        - Sets the internal `__image` attribute to the provided `QPixmap`.
        - Stores the original shape of the image in `__original_array_shape` (height and width).
        - If the provided `QPixmap` is null (doesn't exist in `image_path`), a blank white image is created to ensure a valid image is set.
        - Calculates the `__scale_factor` based on the current widget size and the image width.
        - Scales the image to fit the widget size while maintaining the aspect ratio, using smooth transformation.
        - Resizes the widget to match the scaled image size.
        
        Args:
            value (QPixmap): The QPixmap representing the new image to set.
        """
        self.__image = value
        self.__original_array_shape = [value.height(), value.width()]
        if value.isNull():
            blank_image = QPixmap(self.size())
            blank_image.fill(Qt.white)
            self.__image = blank_image
        self.__scale_factor = self.width() / self.image.width()
        self.__image = value.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.resize(self.__image.size())
    
    @property
    def drawing(self):
        """Get the current annotation overlay (QPixmap)."""
        return self.__drawing
    
    @drawing.setter
    def drawing(self, value:QPixmap):
        """
        Sets the drawing layer with the provided QPixmap, resizing it to match the size of the image.
        
        This setter method:
        - Initializes the internal `__drawing` attribute as a transparent QPixmap with the same size as the image.
        - Uses a QPainter to draw the provided `value` (a QPixmap) onto the newly created `__drawing`.
        - The `value` QPixmap is copied onto the transparent layer at position (0, 0), ensuring the drawing is correctly aligned with the image.
        
        Args:
            value (QPixmap): The QPixmap to set as the drawing layer. This is drawn onto a transparent QPixmap with the size matching the image.
        
        Notes:
            - The `drawing` layer is reset to a transparent QPixmap each time this setter is called.
            - The method ensures that the drawing is positioned correctly by using QPainter to render the `value` QPixmap.
        """
        self.__drawing = QPixmap(self.image.size())
        self.__drawing.fill(Qt.transparent)
        painter = QPainter(self.__drawing)
        painter.drawPixmap(0, 0, QPixmap(value))
        painter.end()
    
    @property
    def annotation_path(self):
        """Get the path to the annotation file to be used by the CV model."""
        return self.__annotation_path
    
    @annotation_path.setter
    def annotation_path(self, value:str):
        """
        Sets the annotation path, determines the type of annotations (bounding boxes or segment masks),
        and loads the corresponding annotations.
        
        This setter method:
        - Sets the internal `__annotation_path` to the provided value.
        - Determines whether to use bounding boxes or labelled segment masks based on the file extension (`.txt` for bounding boxes, `.npy` for segment masks).
        - If bounding boxes are used:
            - Attempts to read and parse the `.txt` file into bounding box data, storing it in `__bounding_boxes`.
            - Raises an error if the file is empty or cannot be loaded.
        - If labelled segment masks are used:
            - Loads the corresponding `.npy` file containing the segment masks into `labelled_segment_masks`.
        - In case of errors (e.g., file not found, empty file, etc.), logs the error and clears any existing annotations.
        - Calls the `__annotate_update_routine` method to refresh the annotations after setting the path.
        
        Args:
            value (str): The file path to the annotation data, either a `.txt` file for bounding boxes or a `.npy` file for labelled segment masks.
        
        Notes:
            - The method differentiates between bounding box annotations and segment mask annotations based on the file extension.
            - If an error occurs while reading the file, the annotations are cleared and a fresh start is initiated.
        """
        self.__annotation_path = value
        self.__use_bounding_boxes = os.path.splitext(value)[-1].lower().strip() == '.txt'
        try:
            if self.__use_bounding_boxes:
                with open(value) as file:
                    lines = file.readlines()
                table = [line.strip().split() for line in lines if line.strip()]
                assert len(table) > 0, 'Empty annotations file...'
                self.__bounding_boxes = np.int32(table)
            else:
                self.__path_to_labelled_segment_masks = os.path.splitext(value)[0] + '.npy'
                self.labelled_segment_masks = np.load(self.__path_to_labelled_segment_masks)
        except Exception as error:
            if isinstance(error, AssertionError) or isinstance(error, FileNotFoundError):
                self.log('No annotations existing, starting afresh...')
                self.__clear_annotations()
        finally:
            self.__annotate_update_routine()
            
    @property
    def use_bounding_boxes(self):
        """Get the flag indicating whether bounding boxes are used for annotations."""
        return self.__use_bounding_boxes
        
    @property
    def bounding_boxes(self):
        """Get the bounding boxes used for annotation."""
        return self.__bounding_boxes
    
    @property
    def labelled_segment_masks(self):
        """Get the labelled segment masks for annotations."""
        return self.__labelled_segment_masks
    
    @labelled_segment_masks.setter
    def labelled_segment_masks(self, value:np.ndarray):
        """
        Sets the labelled segment masks, sorts them by segment area, and updates the overall segment mask.
        
        This setter method:
        - Computes the areas of each segment in the provided `value` array using the `Helper.compute_segment_areas` function.
        - Sorts the segments by their areas in ascending order.
        - Combines the sorted segment masks into a single mask.
        
        Args:
            value (np.ndarray): A 3D numpy array containing the labelled segment masks.
        """
        areas = compute_segment_areas(value)
        self.__labelled_segment_masks = value[np.argsort(areas)]
        self.__overall_segment_mask = self.__combine_labelled_segment_masks()
    
    @property
    def overall_segment_mask(self):
        """Get the overall segment mask that combines all labelled segment masks."""
        return self.__overall_segment_mask
    
    @property
    def label_index_accumulator(self):
        """Floating-point accumulator for label scrolling."""
        return self.__label_index_accumulator
    
    @label_index_accumulator.setter
    def label_index_accumulator(self, value:float):
        """
        Sets the label index accumulator and updates the active label index for annotation.
        
        Functionality:
        - Wraps the floating-point accumulator value within the total number of labels using modulo.
        - Calculates the integer label index to annotate, with a safeguard against floating-point 
          quantization errors (e.g., ensuring 31.999999... correctly maps to 31 when flooring, not 32).
        - If label slider mode is enabled, logs the label index and corresponding label name.
        
        Parameters:
            value (float): The new value for the label index accumulator, which can be fractional 
                           to allow smooth scrolling or adjustments.
        """
        self.__label_index_accumulator = value % self.n_labels
        self.label_index_to_annotate = int(value % self.n_labels) % self.n_labels # To avoid quantization error issues when flooring (e.g. 31.99999999999 gives 32 not 31)
        if self.__label_slider_enabled: # Not to depend on the order of initialization
            self.log(f'Label Slider: {self.__label_index_accumulator:.2f}: {self.label_index_to_annotate + 1}/{self.n_labels}, {self.labels[self.label_to_annotate]}')
      
    @property
    def pen_width_multiplier_accumulator(self):
        """Floating-point accumulator for pen width scrolling."""
        return self.__pen_width_multiplier_accumulator
    
    @pen_width_multiplier_accumulator.setter
    def pen_width_multiplier_accumulator(self, value:float):
        """
        Sets the pen width multiplier accumulator and updates the effective pen width.
        
        Functionality:
        - Clamps the accumulator value to the [0.0, 1.0] range.
        - Computes the actual pen width multiplier based on the clamped value and the maximum allowed multiplier.
        - Logs the updated pen width multiplier if the label slider mode is not enabled (to avoid unintended logs during initialization or label adjustments).
        
        Parameters:
            value (float): A normalized value (typically between 0 and 1) representing the percentage of desired maximum pen width multiplier to be applied for pen resizing.
        """
        self.__pen_width_multiplier_accumulator = 0.0 if value < 0.0 else 1.0 if value > 1.0 else value
        self.pen_width_multiplier = 1 + self.__pen_width_multiplier_accumulator * (self.maximum_pen_width_multiplier - 1)
        if not self.__label_slider_enabled: # Not to depend on the order of initialization
            self.log(f'Pen Width Slider: {self.pen_width_multiplier:.2f}')
        
    @property
    def pen_width_multiplier(self):
        """The current multiplier applied to the base pen width."""
        return self.__pen_width_multiplier
    
    @pen_width_multiplier.setter
    def pen_width_multiplier(self, value:float):
        """
        Sets the pen width multiplier and resizes the annotation pen accordingly.
    
        Parameters:
            value (float): The new pen width multiplier to apply.
        """
        self.__pen_width_multiplier = value
        self.__resize_pen()
        
    def save(self):
        """
        Save current annotations to disk.
        
        - Bounding boxes are saved as a plain text (.txt) file.
        - Segmentation masks are saved both as a NumPy array (.npy) and a PNG image (.png).
        
        Raises:
            OSError: If unable to write to the save path.
        """
        directory_path = os.path.dirname(self.annotation_path)
        os.makedirs(directory_path, exist_ok=True)
        if self.use_bounding_boxes:
            lines = [' '.join(row)+'\n' for row in self.bounding_boxes.astype(str)]
            with open(self.annotation_path, 'w') as file:
                file.writelines(lines)
        else:
            np.save(self.__path_to_labelled_segment_masks, self.labelled_segment_masks)
            imsave(self.annotation_path, self.overall_segment_mask)
        absolute_file_path = os.path.abspath(self.annotation_path)
        self.log(f'Annotations saved to "{absolute_file_path}"')
    
    def log(self, message:str):
        """
        Print a log message if verbosity is enabled.

        Args:
            message (str): Message to print.
        """
        if self.__verbose:
            print(' ' * len(self.__previous_message), end='\r')
            print(message, end='\r')
            self.__previous_message = message
        
    def __combine_labelled_segment_masks(self):
        """
        Combines multiple labelled segment masks into a single mask by merging them.
        
        The method iterates over the labelled segment masks and merges them into one mask:
        - For each mask, the annotated portions (i.e., portions not equal to 255) are copied into the corresponding positions of the next mask.
        - The resulting combined mask has all the annotations merged.
        
        If no labelled segment masks are present, the method returns a mask of the original shape, filled with the value 255 (representing no annotations).
        
        Returns:
            np.ndarray: A single combined mask containing all annotations, or a mask filled with 255 if no segment masks exist.
        
        Notes:
            - The merged mask will have the same shape as the original segment mask array.
            - The method uses the `reduce` function to apply the merge operation iteratively across all masks.
        """
        def merge(mask_a, mask_b):
            annotated_portion_in_mask_a = mask_a != 255
            annotated_indices_in_mask_a = np.where(annotated_portion_in_mask_a)
            mask_b[annotated_indices_in_mask_a] = mask_a[annotated_indices_in_mask_a]
            return mask_b
        if self.labelled_segment_masks.size:
            masks = self.labelled_segment_masks.copy()
            return reduce(merge, masks).astype('uint8')
        return np.zeros(self.__original_array_shape, 'uint8') + 255
    
    def __resize_update_routine(self):
        """Handle window resize events, rescaling images and updating annotation layers."""
        self.__reload_image()
        self.__retrace_annotations()
        self.__combine_layers_and_update_image_display()
        self.__update_label_displays()
        self.__resize_pen()
        
    def __annotate_update_routine(self):
        """Update the annotation overlay and label displays after changes."""
        self.__retrace_annotations()
        self.__combine_layers_and_update_image_display()
        self.__update_label_displays()
    
    def __reload_image(self):
        """Reload the original image without affecting current annotations."""
        self.image_path = self.image_path
    
    def __retrace_annotations(self):
        """Clear overlay layer and redraw all annotations (bounding boxes or masks)."""
        self.drawing = None
        if self.__use_bounding_boxes:
            self.__trace_bounding_boxes()
        else:
            self.__trace_segments()
            
    def __trace_bounding_boxes(self):
        """
        Draws bounding boxes on the image and optionally labels them with the corresponding label names.
        
        The method iterates over all the bounding boxes and draws them on the drawing layer:
        - Each bounding box is drawn with a color corresponding to its label.
        - If the `corner_label_attached_to_bounding_box` flag is set, the label for the bounding box is displayed at its corner.
        
        The bounding box dimensions are scaled according to the current scale factor, and the label text is displayed with a white font on a background matching the label's color.
        """
        painter, pen, brush = QPainter(self.drawing), QPen(self.__annotation_pen), QBrush(Qt.Dense7Pattern)
        pen.setWidthF(self.__annotation_pen.widthF() / self.__minimum_pen_width)
        if self.corner_label_attached_to_bounding_box:
            font_size = int(self.__label_font_size * self.__scale_factor)
            font = QFont('Arial', font_size)
            painter.setFont(font)
            
        for bounding_box in self.bounding_boxes:
            label_index, dimensions = bounding_box[0], bounding_box[1:]
            dimensions = np.int32(dimensions * self.__scale_factor)
            color = self.label_colors[label_index]
            pen.setColor(color); brush.setColor(color)
            painter.setPen(pen); painter.setBrush(brush)
            painter.drawRect(QRect(*dimensions))
            if self.corner_label_attached_to_bounding_box:
                x_offset, y_offset = dimensions[:2]
                text = f'Label: {self.labels[label_index]}'
                font_metrics = painter.fontMetrics()
                text_width, text_height = round(font_metrics.horizontalAdvance(text) * 1.2), font_metrics.height()
                text_box = QRect(x_offset, y_offset, text_width, text_height)
                painter.fillRect(text_box, self.label_colors[label_index])
                pen.setColor(Qt.white); painter.setPen(pen)
                x_text, y_text = [x_offset, y_offset] + np.int32([0.08 * text_width, 0.77 * text_height])
                painter.drawText(x_text, y_text, text)
    
    def __trace_segments(self):
        """
        Traces and generates the drawing layer for the segmented image, applying colors based on the labels.
        
        This method performs the following steps:
        - Prepares an RGBA lookup table based on the label colors and the opacity setting.
        - Resizes the overall segment mask to match the current image dimensions.
        - Uses the lookup table to map segment mask values to RGBA colors.
        - Converts the resulting RGBA array into a QPixmap and stores it in the `drawing` attribute.
        
        The resulting `drawing` is used to display the segmented image with colors corresponding to different labels.
        """
        def prepare_rgba_lookup_table():
            alpha = int(self.__opacity * 255)
            get_rgb_channels = lambda color: [color.red(), color.green(), color.blue()]
            lookup_table = np.zeros([256, 4], 'uint8')
            lookup_table_modification = np.uint8([get_rgb_channels(color) + [alpha] for color in self.label_colors])
            lookup_table[:self.n_labels] += lookup_table_modification
            return lookup_table
        
        current_array_shape = self.height(), self.width()
        scaled_overall_segment_mask = resize(self.overall_segment_mask, current_array_shape, 0)
        lookup_table = prepare_rgba_lookup_table()
        rgba_array = lookup_table[scaled_overall_segment_mask]
        self.drawing = rgba_array_to_pixmap(rgba_array)
    
    def __combine_layers_and_update_image_display(self):
        """
        Combines the base image, drawing layer, and optional pen tracer overlay into a single QPixmap,
        then updates the image display widget.
    
        This method performs the following steps:
        - Creates a compound QPixmap from the original image.
        - Uses QPainter to draw the current drawing layer onto the compound image.
        - Optionally draws an additional pen tracer overlay when it exists.
        - Updates the GUI's image display with the resulting composed image.
        """
        compound_layer = QPixmap(self.image)
        painter = QPainter(compound_layer)
        painter.drawPixmap(0, 0, self.drawing)
        if hasattr(self, '_ImageAnnotator__pen_tracer_overlay'):
            painter.drawPixmap(0, 0, self.__pen_tracer_overlay)
        painter.end()
        self.__image_display.setPixmap(compound_layer)
        
    def __get_mask_for_annotations_hovered_over(self):
        """
        Retrieves a mask indicating which annotations are currently hovered over by the cursor.
        
        The method generates a mask that marks annotations under the cursor’s position:
        
        - If bounding boxes are used, it checks if the cursor is within the bounds of each bounding box.
        - If segment masks are used, it checks if the cursor is within any segment by verifying the pixel value at the cursor’s position.
        
        Returns:
            np.ndarray: A boolean mask where each element corresponds to an annotation, indicating whether it is hovered over by the cursor.
        
        Notes:
            - The method returns a boolean array where `True` indicates that the annotation is hovered over, and `False` otherwise.
            - If no annotations are present or the cursor is not hovering over any annotation, the returned mask will be all `False`.
        """
        annotation_hover_mask = np.zeros(self.bounding_boxes.shape[0] if self.use_bounding_boxes else self.labelled_segment_masks.shape[0], bool)
        annotations_exist = bool(annotation_hover_mask.size)
        if annotations_exist:
            y_cursor, x_cursor = self.__yx_cursor_within_original_image
            if self.use_bounding_boxes:
                for index, (_, x_offset, y_offset, width, height) in enumerate(self.bounding_boxes):
                    annotation_hover_mask[index] = \
                        y_offset <= y_cursor <= y_offset + height and \
                        x_offset <= x_cursor <= x_offset + width
            else:
                annotation_hover_mask = self.labelled_segment_masks[:, y_cursor, x_cursor] != 255
        return annotation_hover_mask
    
    def __get_mask_for_smallest_annotation_hovered_over(self):
        """
        Retrieves the mask for the smallest annotation currently hovered over by the cursor.
        
        This method checks which annotations are under the cursor and determines the smallest one based on its area:
        
        - If bounding boxes are used, the area is calculated as the product of the bounding box dimensions.
        - If segment masks are used, the area is computed using a helper function.
        
        The method returns a mask corresponding to the smallest hovered annotation.
        
        Returns:
            np.ndarray: A boolean mask indicating the smallest annotation hovered over, or an empty mask if no annotation is hovered over.
        
        Notes:
            - The method compares annotations based on their area and returns a mask for the smallest one.
            - If no valid annotation is found under the cursor, it returns an empty mask.
        """
        annotation_hover_mask = self.__get_mask_for_annotations_hovered_over()
        if annotation_hover_mask.sum() < 2:
            return annotation_hover_mask
        annotations = self.bounding_boxes if self.use_bounding_boxes else self.labelled_segment_masks
        annotations_to_inspect = annotations[annotation_hover_mask]
        if self.use_bounding_boxes:
            areas = np.prod(annotations_to_inspect[:,-2:], axis=1)
        else:
            areas = compute_segment_areas(annotations_to_inspect)
        index_of_interest = np.argmin(areas)
        smallest_annotation_hover_mask = (annotations == annotations_to_inspect[index_of_interest]).all(axis=1 if self.use_bounding_boxes else (1,2))
        return smallest_annotation_hover_mask
    
    def __drop_smallest_annotation_hovered_over(self):
        """
        Drops the smallest annotation currently hovered over by the cursor.
    
        This method generates a mask for the smallest annotation under the cursor and removes it from the collection of annotations:
        
        - If bounding boxes are used, it removes the corresponding bounding box from the list.
        - If segment masks are used, it removes the corresponding segment mask from the array.
    
        Returns:
            bool: True if an annotation was successfully removed, False if no annotation was hovered over or removed.
    
        Notes:
            - The method checks for the smallest annotation under the cursor and removes it based on the current configuration (bounding boxes or segment masks).
            - The method returns `True` if an annotation was removed, and `False` if no annotation was found or removed.
        """
        smallest_annotation_hover_mask = self.__get_mask_for_smallest_annotation_hovered_over()
        if smallest_annotation_hover_mask.any():
            if self.use_bounding_boxes:
                self.__bounding_boxes = self.bounding_boxes[~smallest_annotation_hover_mask]
            else:
                self.labelled_segment_masks = self.labelled_segment_masks[~smallest_annotation_hover_mask]
            return True
        return False
    
    def __get_label_index_hovered_over(self):
        """
        Retrieves the label index of the smallest annotation currently hovered over by the cursor.
        
        This method checks for the smallest annotation under the cursor by generating a mask and then determines
        the label index based on whether bounding boxes or segment masks are used:
        
        - If bounding boxes are used, it returns the index of the first label in the smallest hovered bounding box.
        - If segment masks are used, it returns the label index of the smallest hovered segment mask that is not empty (i.e., excluding the background).
        
        Returns:
            int: The index of the label hovered over, or -1 if no annotation is hovered over.
        
        Notes:
            - If no annotation is detected under the cursor, the method returns -1.
            - The method handles both bounding boxes and segment masks based on the current configuration.
        """
        smallest_annotation_hover_mask = self.__get_mask_for_smallest_annotation_hovered_over()
        if smallest_annotation_hover_mask.any():
            if self.use_bounding_boxes:
                smallest_annotation_hovered_over = self.bounding_boxes[smallest_annotation_hover_mask].squeeze()
                return smallest_annotation_hovered_over[0]
            else:
                smallest_annotation_hovered_over = self.labelled_segment_masks[smallest_annotation_hover_mask].squeeze()
                annotated_portion = smallest_annotation_hovered_over != 255
                return np.unique(smallest_annotation_hovered_over[annotated_portion])[0]
        return -1
    
    def __clear_annotations(self):
        """
        Clears all annotations from the drawing, either by resetting bounding boxes or labelled segment masks.
        
        If bounding boxes are used:
            - Resets the bounding boxes array to an empty array with shape (0, 5), which represents no bounding boxes.
        
        If bounding boxes are not used:
            - Resets the labelled segment masks array to an empty array with the same shape as the original array, representing no segment masks.
        
        This method effectively removes all annotations from the image or drawing.
        """
        if self.use_bounding_boxes:
            self.__bounding_boxes = np.empty([0, 5], 'int32')
        else:
            self.labelled_segment_masks = np.empty([0] + self.__original_array_shape, 'int32')
        
    def __draw(self, current_position:QPoint, mode:str):
        """
        Draws either a point or a line on the drawing based on the specified mode.
        
        If the mode is 'point', draws a point at the current position.
        If the mode is 'line', draws a line from the last recorded position to the current position.
        
        The method raises a ValueError if an invalid mode is provided.
        
        Args:
            current_position (QPoint): The current position where the drawing action should take place.
            mode (str): The drawing mode, either 'point' or 'line'. 'point' draws a single point, 'line' draws a line from the last position to the current one.
        
        Raises:
            ValueError: If the mode is not 'point' or 'line'.
        """
        if mode not in {'point', 'line'}:
            raise ValueError("The argument `mode` can either take the value of 'point' or 'line'.")
        
        painter = QPainter(self.drawing)
        painter.setPen(self.__annotation_pen)
        if mode == 'point' or self.__last_pen_position is None:
            painter.drawPoint(current_position)
        else:
            painter.drawLine(self.__last_pen_position, current_position)
        painter.end()
        
    def __configure_label_display(self, label_display:QLabel, label_index:int, hovering:bool):
        """
        Configures the display of a label in a QLabel widget based on the label index and hovering state.
    
        If the label index is invalid (negative) or erasing is active and not hovering:
            - Sets the label text to 'N/A' and the background to transparent.
    
        Otherwise, it sets the label text to the corresponding label from the list and the background color to the label's color.
    
        The label text is padded to align properly with the maximum text length of all labels.
    
        Args:
            label_display (QLabel): The QLabel widget where the label text and style will be applied.
            label_index (int): The index of the label to display, used to retrieve the label text and color.
            hovering (bool): Indicates whether the mouse is hovering over a label for interaction.
        """
        if label_index < 0 or (self.erasing and not hovering):
            text = 'N/A'
            background_color = 'transparent'
        else:
            text = self.labels[label_index]
            background_color = self.label_colors[label_index].name()
        maximum_text_length = reduce(lambda a, b: max(len(str(a)), len(str(b))), self.labels + ['N/A'])
        label_display.setText(f'Label: {text:<{maximum_text_length}}')
        label_display.setStyleSheet(f'background: {background_color}; border: 1px solid black; padding: 2px;')
        
    def __update_label_displays(self):
        """
        Update and reposition both floating label displays.
    
        - Updates the 'Label to Annotate' (current active label) and 'Hovered Label' (label under cursor).
        - Dynamically repositions the labels based on cursor location or screen corner.
        - Ensures consistent layout between the two label displays.
        """
        self.__label_index_hovered_over = self.__get_label_index_hovered_over()
        
        self.__configure_label_display(self.__label_to_annotate_display, self.label_index_to_annotate, False)
        self.__configure_label_display(self.__label_annotated_display, self.__label_index_hovered_over, True)
        
        if self.__last_pen_position and self.is_floating_label:
            x_offset = self.__last_pen_position.x() + self.__floating_label_display_offsets[0]
            y_offset = self.__last_pen_position.y() + self.__floating_label_display_offsets[1]
        else:
            x_offset = self.width() - max(self.__label_to_annotate_display.width(), self.__label_annotated_display.width())
            y_offset = 0
        self.__label_to_annotate_display.move(x_offset, y_offset)
        self.__label_annotated_display.move(x_offset, y_offset + self.__label_to_annotate_display.height())
        
        if not self.__label_displays_configuration_complete:
            common_width = max(self.__label_to_annotate_display.width(), self.__label_annotated_display.width()) - 25
            self.__label_to_annotate_display.setFixedWidth(common_width - 1)
            self.__label_annotated_display.setFixedWidth(common_width - 1)
            self.__label_displays_configuration_complete = True
            
    def __reconfigure_label_annotated_display(self):
        """
        Update only the hovered label display.
        
        - Refreshes the label information under the current mouse position.
        - Does not reposition any floating labels or change layout.
        """
        self.__label_index_hovered_over = self.__get_label_index_hovered_over()
        self.__configure_label_display(self.__label_annotated_display, self.__label_index_hovered_over, True)
    
    def __resize_pen(self):
        """
        Dynamically adjust the drawing pen width based on window size.
        
        - Scales the annotation pen width proportionally relative to the initial minimum widget width and the pen width multiplier.
        - Ensures that the pen stays visually consistent across different window resize events.
        """
        widget_minimum_width = self.minimumWidth()
        if widget_minimum_width:
            ratio = self.width() / widget_minimum_width
            self.__annotation_pen.setWidthF(ratio * self.__minimum_pen_width * self.pen_width_multiplier)
    
    def resizeEvent(self, event):
        """
        Handle window resize events.
        
        - Sets the initial minimum widget size based on the first resize.
        - Rescales the image display to match the new widget size.
        - Starts a timer to schedule an optimized resize update routine.
        
        Args:
            event (QResizeEvent): The resize event object containing new size info.
        """
        if not self.__minimum_widget_size_set:
            self.setMinimumSize(self.size())
            self.__minimum_widget_size_set = True
        self.__image_display.resize(self.size())
        self.__resize_scheduler.start(200)
        event.accept()
    
    def wheelEvent(self, event):
        """
        Handles mouse wheel events to modify either label selection or pen width, 
        depending on the current mode.
        
        Behavior:
        - If erasing mode is active, it is disabled.
        - If label slider mode is enabled:
            - Adjusts the label index accumulator based on the wheel direction and sensitivity.
            - Updates the label display accordingly.
        - Otherwise:
            - Adjusts the pen width accumulator based on the wheel direction and sensitivity.
        
        After handling the wheel input, this method updates the pen tracer overlay 
        and refreshes the image display.
        
        Parameters:
            event (QWheelEvent): The wheel event triggered by user input.
        """
        if self.erasing:
            self.__erasing = False
        delta = event.angleDelta().y()
        if self.__label_slider_enabled:
            delta = self.__label_slider_sensitivity * np.sign(delta)
            self.label_index_accumulator += delta
            self.__update_label_displays()
        else:
            delta = self.__pen_width_slider_sensitivity * np.sign(delta)
            self.pen_width_multiplier_accumulator += delta
        self.__update_pen_tracer_overlay()
        self.__combine_layers_and_update_image_display()
    
    def mousePressEvent(self, event):
        """
        Handles mouse press events to manage annotation drawing, erasing, and UI mode toggling.
        
        Behavior depends on the mouse button pressed:
        - Left Button:
            - If in erasing mode, attempts to remove the smallest annotation under the cursor.
              If an annotation is removed:
                - Retraces annotations.
                - Updates the annotated label display.
                - Optionally triggers autosave if enabled.
            - Otherwise, draws a point annotation at the cursor position.
            - In both cases, updates the combined image display.
        
        - Right Button:
            - Toggles the erasing mode.
            - Updates the pen tracer overlay and refreshes the image and label displays.
        
        - Middle Button:
            - Toggles the label slider mode (used for navigating label indices).
            - Updates the pen tracer overlay and refreshes the image display.
        
        Parameters:
            event (QMouseEvent): The mouse press event containing button and position data.
        """
        if event.button() == Qt.LeftButton:
            if self.__erasing:
                updated = self.__drop_smallest_annotation_hovered_over()
                self.__retrace_annotations()
                if updated:
                    self.__reconfigure_label_annotated_display()
                    if self.__autosave:
                        self.save()
            else:
                self.__draw(event.pos(), 'point')
            self.__combine_layers_and_update_image_display()
        elif event.button() == Qt.RightButton:
            self.__erasing ^= True
            self.__update_pen_tracer_overlay()
            self.__combine_layers_and_update_image_display()
            self.__update_label_displays()
        elif event.button() == Qt.MiddleButton:
            self.__label_slider_enabled ^= True
            self.__update_pen_tracer_overlay()
            self.__combine_layers_and_update_image_display()
            
    def __update_pen_tracer_overlay(self):
        """
        Updates the pen tracer overlay used to visually indicate the pen position and size on the image.
    
        Functionality:
        - If no previous pen position is recorded, the method exits early.
        - Initializes a transparent QPixmap the same size as the image to serve as the overlay.
        - If in erasing mode, the overlay is left blank and the method returns.
        - Otherwise, draws a circle (tracer) at the last pen position to indicate where and how large 
          the next annotation will be.
            - If label slider mode is not active, uses the current label color for the tracer.
            - Otherwise, uses a black pen.
        - The tracer's size reflects the current pen width adjusted by scaling factors.
    
        This method is called whenever visual feedback about the drawing tool is needed,
        such as when the pen size or position changes.
        """
        if self.__last_pen_position is None:
            return
        self.__pen_tracer_overlay = QPixmap(self.image.size())
        self.__pen_tracer_overlay.fill(Qt.transparent)
        if self.__erasing:
            return
        painter = QPainter(self.__pen_tracer_overlay)
        if not self.__label_slider_enabled:
            pen = QPen(self.label_colors[self.label_index_to_annotate], 1)
        else:
            pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        pen_width = self.__annotation_pen.widthF()
        width = pen_width - 6 * self.pen_width_multiplier * self.__scale_factor
        painter.drawEllipse(self.__last_pen_position, width, width)
        painter.end()
        
    def mouseMoveEvent(self, event):
        """
        Handles mouse movement events and updates the image display based on cursor position and button states.
    
        If the left mouse button is held down:
            - If erasing is enabled, it attempts to drop the smallest annotation hovered over and retraces annotations.
            - Otherwise, it draws a line based on the mouse movement.
            - Combines layers and updates the image display.
    
        Additionally, updates the label displays and tracks the last position of the pen.
        
        Args:
            event (QMouseEvent): The event object containing details about the mouse movement.
        """
        self.__yx_cursor_within_original_image = (np.array([event.y(), event.x()]) / self.__scale_factor).astype(int)
        if event.buttons() & Qt.LeftButton:
            if self.__erasing:
                updated = self.__drop_smallest_annotation_hovered_over()
                if updated:
                    self.__retrace_annotations()
                    if self.__autosave:
                        self.save()
            else:
                self.__draw(event.pos(), 'line')
        self.__update_pen_tracer_overlay()
        self.__combine_layers_and_update_image_display()
        self.__update_label_displays()
        self.__last_pen_position = event.pos()
        
    def mouseDoubleClickEvent(self, event):        
        """
        Handles mouse double-click events, performing different actions based on the button pressed.
        
        If the right mouse button is double-clicked:
            - Prompts the user with a warning message asking for confirmation to clear annotations.
            - If confirmed, clears all annotations and disables erasing mode.
        
        If the left mouse button is double-clicked and erasing is not active:
            - Performs a flood-fill algorithm to locate all connected pixels starting from the double-clicked position.
            - If bounding boxes are used, checks the size of the bounding box and adds it to the list if it meets the size thresholds.
            - If bounding boxes are not used, creates and labels a segment mask, and adds it to the list of labelled segment masks.
        
        After updating annotations or segment masks, triggers the update routine and optionally saves the state if autosave is enabled.
        
        Args:
            event (QMouseEvent): The event object containing details about the mouse double-click.
        """
        updated = False
        if event.button() == Qt.RightButton:
            response = QMessageBox.warning(self, 'Clear Drawing?', 'You are about to clear your annotations for this image!', QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if response == QMessageBox.Ok:
                self.__clear_annotations()
                self.__erasing = False
                updated = True
        elif event.button() == Qt.LeftButton and not self.erasing:
            yx_root = event.y(), event.x()
            rgba_array = pixmap_to_rgba_array(self.drawing)
            rgb_array = rgba_array[:,:,:-1]
            traversed_pixels_mask = locate_all_pixels_via_floodfill(rgb_array, yx_root)
            if self.use_bounding_boxes:
                bounding_box = mask_to_bounding_box(traversed_pixels_mask)
                x_offset, y_offset, width, height = (bounding_box / self.__scale_factor).astype('int32').tolist()
                minimum_side_length, maximum_side_length = min(width, height), max(width, height)
                lower_side_length_bound, upper_side_length_bound = self.__bounding_box_side_length_thresholds
                if lower_side_length_bound <= minimum_side_length and maximum_side_length <= upper_side_length_bound:
                    self.__bounding_boxes = np.concatenate([
                        self.bounding_boxes,
                        np.array([self.label_index_to_annotate, x_offset, y_offset, width, height])[np.newaxis, ...]
                    ])
                boxes_to_remove_mask = detect_overlapping_boxes_to_clean(self.bounding_boxes, self.__overlap_vs_smallest_area_threshold, self.__overlap_vs_union_area_threshold)
                self.__bounding_boxes = self.bounding_boxes[~boxes_to_remove_mask]
            else:
                segment_mask = resize(traversed_pixels_mask, self.__original_array_shape, 0)
                segment_mask = binary_fill_holes(segment_mask).astype(int)
                labelled_segment_mask = apply_lut_replacement(segment_mask, self.label_index_to_annotate)
                self.labelled_segment_masks = np.concatenate([labelled_segment_mask[np.newaxis, ...], self.labelled_segment_masks])
            updated = True
        if updated:
            self.__annotate_update_routine()
            if self.__autosave:
                self.save()