import os
import cv2

from collections import Counter
from PIL import Image

from logs.custom_logs import LoggerCfg


class SnapDifferentiator(object):
    def __init__(self):
        self.__logger = LoggerCfg('SnapDifferentiator').get_logger()

    def display_difference(self, snap1, snap2, output_directory=None, is_cv_read=False):
        """
        Display and save the diff between two snaps.

        Parameters:
        - snap1 (str or ndarray): Path to the first snap or the snap array.
        - snap2 (str or ndarray): Path to the second snap or the snap array.
        - is_cv_read (bool): If True, the snaps are already read using cv2.
        - output_directory (str): Path to the directory where the result should be saved.
        """
        try:
            if not output_directory:
                raise Exception("ParameterException: Invalid directory path. Provide a proper directory path")

            # Read snaps if not already read
            if not is_cv_read:
                try:
                    snap1 = cv2.imread(snap1)
                    snap2 = cv2.imread(snap2)
                except Exception as e:
                    raise Exception(f"SnapReadException: Could not read one or both snaps {e}")
                if snap1 is None or snap2 is None:
                    raise Exception("SnapReadException: Could not read one or both snaps")

            # Compute the difference
            try:
                diff = cv2.subtract(snap1, snap2)
            except Exception as de:
                raise Exception(f"SnapDiffException: Snaps must be of same size {de}")

            # Convert to grayscale and create a red mask
            conv_hsv_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(conv_hsv_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

            # Highlight differences in red
            diff[mask != 255] = [0, 0, 255]
            snap1[mask != 255] = [0, 0, 255]
            snap2[mask != 255] = [0, 0, 255]

            # Create the directory if it doesn't exist
            try:
                if not os.path.exists(output_directory):
                    os.makedirs(output_directory)
            except Exception as e:
                raise Exception(f"Invalid directory path. Could not create directory {e}")

            # Save the diff snap
            diff_filename = os.path.join(output_directory, 'snap_difference.png')
            cv2.imwrite(diff_filename, diff)
        except Exception as e:
            self.__logger.info(f'DisplayDiffError: {e}')
