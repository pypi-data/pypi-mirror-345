# snapdedup

 - snapdedup is a Python package for processing images, including comparing two images and highlighting the differences.

## Installation

 - You can install the package via pip:

 - ```
   pip install snapdedup
   ```

# Usage
 - Here's a basic example of how to use the SnapDifferentiator class to display the difference between two images

 - ```
   import os
   from snapdedup.snap_differentiator import SnapDifferentiator

   # Define paths
   dir = 'img'
   op_directory = 'op_img_dir'
   image_1 = 'img_prep_1.png'
   image_2 = 'img_prep_2.png'

   # Create an instance of SnapDifferentiator
   img_p = SnapDifferentiator()

   # Display and save the difference between the two images
   img_p.display_difference(os.path.join(dir, image_1), os.path.join(dir, image_2), os.path.join(dir, op_directory), is_cv_read=False)
   ```
   

# Running Tests
 - To run tests, you need to have these installed.
   - pytest
   - pytest-cov


# Improvements or Issues
  - Other image processing features
  - Please email us if you find any issues.

# Contact
 - Please mail us if you have any issues.
 - Make sure to put subject as --> Improvements for python library

# License
 - MIT License

# Acknowledgements
 - Stackoverflow

# Developers
 - Sarthak Gholap
 - Harshit Dalal