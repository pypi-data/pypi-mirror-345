""" 
Tadqeeq - Image Annotator Tool
An interactive image annotation tool for efficient labeling.
Developed by Mohamed Behery @ RTR Software Development (2025-04-27).
Licensed under the MIT License.
"""

from PyQt5.QtWidgets import QApplication
import sys
from .widgets import ImageAnnotator

def main():
    if len(sys.argv) != 3:
        print("Usage: tadqeeq <image_path> <annotation_path>")
        sys.exit(1)
    app = QApplication(sys.argv)
    window = ImageAnnotator(image_path=sys.argv[1], annotation_path=sys.argv[2])
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()