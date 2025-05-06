import pytest
import os
import cv2
import numpy as np

from snapdedup.snap_differentiator import SnapDifferentiator


@pytest.fixture(scope="module")
def setup_snaps():
    # Define directories
    input_dir = os.path.abspath('test_snaps')
    output_dir = os.path.abspath('output')

    # print(f"Input directory: {input_dir}")
    # print(f"Output directory: {output_dir}")

    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create test snaps if they do not exist
    snap1_path = os.path.join(input_dir, 'img_prep_1.png')
    snap2_path = os.path.join(input_dir, 'img_prep_2.png')

    if not os.path.exists(snap1_path):
        snap1 = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(snap1_path, snap1)
        # print(f"Created snap: {snap1_path}")

    if not os.path.exists(snap2_path):
        snap2 = np.zeros((100, 100, 3), dtype=np.uint8)
        snap2[50:] = [255, 255, 255]  # Add a white rectangle in the second snap
        cv2.imwrite(snap2_path, snap2)
        # print(f"Created snap: {snap2_path}")

    # Verify the snaps are created successfully
    assert os.path.exists(snap1_path), f"Test snap {snap1_path} was not created."
    assert os.path.exists(snap2_path), f"Test snap {snap2_path} was not created."

    yield input_dir, output_dir, snap1_path, snap2_path

    # Cleanup output directory after tests
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))


def test_display_difference(setup_snaps):
    input_dir, output_dir, snap1_path, snap2_path = setup_snaps
    img_p = SnapDifferentiator()

    # print(f"Testing display difference with snaps: {snap1_path} and {snap2_path}")
    img_p.display_difference(snap1_path, snap2_path, output_dir, is_cv_read=False)

    # Verify that the output snap is created
    output_snap_path = os.path.join(output_dir, 'snap_difference.png')
    assert os.path.exists(output_snap_path), "Output snap not found."

    # Load the output snap
    output_snap = cv2.imread(output_snap_path)
    assert output_snap is not None, "Failed to read the output snap."

    # Check that the output snap has red highlights where the differences are
    red_mask = np.all(output_snap == [0, 0, 255], axis=-1)
    assert np.any(red_mask), "No differences highlighted in red."
