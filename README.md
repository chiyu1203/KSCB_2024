# KSCB_2023
This is a repo to store codes used in CASCB summer school in 2023
The codes, are for educational purpose, in this demo use these tutorial as a backbone

https://www.geeksforgeeks.org/create-a-pong-game-in-python-pygame/

https://pysource.com/2018/01/31/object-detection-using-hsv-color-space-opencv-3-4-with-python-3-tutorial-9/ 

And some additional function in the notebook is listed here:
https://pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/

General anaconda environment for all setups and data analyses

Install the latest anaconda version for your operating system (https://www.anaconda.com/products/individual).

Open the anaconda prompt and create a virtual environment via conda

```
conda create --name kscb_2023 --channel conda-forge python=3.11
```
Activate the virtual environment
```
conda activate kscb_2023
```
Install dependencies via pip
```
pip install pygame opencv-python notebook imutils
```
Optional package (in case you want to plot some outputs):
```
pip install matplotlib
```


If you have a favourite python IDE (such as pycharm, spyder, VS code), use that to test your code and only use jupyter notebook to look up what the next practice is about.


If you want to use jupyter notebook or anything similiar to code, note that the nature of running seperate cells on notebook may return error: display Surface quit if you repeat the same main function without initiating Pygame modules. This is likely due to pygame.quit() uninitialize all PyGame modules at the end of the main function to close the display. One way to circuvment this error is to initiating Pygame module each time when running the main function. Therefore I have changed the structure of the demo code to match that matter on the jupyter notebook. The other way to circuvment this error is to go to Run > Run All Cells, each time when testing the cells on the notebook. This also mean that you need to commend out old cells or not call them to ensure they are not executed.
