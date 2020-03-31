# Word-Hunt-Finder
Helps you find words in Word Hunt with a simple webcam.

Uses python packages OpenCV, NumPy, and Python-tesseract, which can be downloaded with the help of Anaconda and the environment.yml file provided.

To use it, run main.py and a window of your camera's view should appear. Move your phone screen (with the Word Hunt active) so that it is visible in the camera and a purple/pink border should appear around the main portion of the Word Hunt screen and a separate window should pop up with a perspective corrected version of the phone screen (top-down view).
Once you have a good, decently-focused shot of the screen (check the test images provided if you are unsure), press Enter and both streams should freeze. Press Enter again to go through and process the straightened image, or press Backspace to unfreeze the camera streams and try to get a better image.
Once Enter is pressed two times in a row, the program should output the character grid and all possible words that can be created from longest to shortest within 5 seconds.


Evan Wang (alien_lover)
