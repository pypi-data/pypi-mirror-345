# Camera Stage Mapping calibration

This Python module allows you to calibrate a microscope's stage against the camera.  By moving the sample a known number of steps, and tracking how far the image translates, it is possible to recover the number of steps per pixel.  This code goes a step further, and recovers a 2x2 affine transformation matrix, so it will cope with rotation, flipping, and non-uniform scaling of the X and Y axes.  The calibration routines are designed to be relatively robust and minimally parameterised, so they start by determining a sensible step size automatically.

As part of the calibration, you can use either FFT-based or directly calculated cross correlation to track motion of the sample.  This code is probably useful on its own, and is found in the ``fft_image_tracking`` and ``correlation_image_tracking`` submodules.  The underlying mechanism of tracking stage and camera coordinates simultaneously is handled by the ``CameraStageTracker`` class, in ``camera_stage_tracker``.  The main calibration function is ``camera_stage_calibration_1d.calibrate_backlash_1d``.  For 2D calibration, I recommend running this once for X and once for Y, then using ``camera_stage_calibration_1d.image_to_stage_displacement_from_1d`` to combine the two calibrations.  This is more robust than the 2D grid calibration method.

## Hardware interface
Rather than tie these functions to a specific class interface, as found in many lab control frameworks, the calibration routines simply require functions to be passed in as arguments.  This is done for maximum flexibility, and to impose the fewest necessary constraints on the hardware we are controlling.  In the future, we may define a class interface to use, and would welcome input on how to do this without forcing a particular taxonomy of laboratory instruments upon everyone using the library.

## Installing
```
pip install camera-stage-mapping
```
This package is published on PyPI and can be installed using ``pip``.  It's managed using ``poetry`` and can be installed by cloning the repository and running ``poetry install``.  For details of how to set up a development environment, please see [CONTRIBUTING].

## Documentation
The functions all have fairly extensive docstrings and the module is documented on [readthedocs].

[readthedocs]: https://camera-stage-mapping.readthedocs.io/en/latest/index.html
[CONTRIBUTING]: ./CONTRIBUTING.md