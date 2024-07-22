# KSCB_2024
This is a repo to store codes used in CASCB summer school. The first tutorial was designed in 2023 and updated in 2024 with Windows PC. 
The codes, are for educational purpose, in this demo use these tutorial as a backbone

https://www.geeksforgeeks.org/create-a-pong-game-in-python-pygame/

https://pysource.com/2018/01/31/object-detection-using-hsv-color-space-opencv-3-4-with-python-3-tutorial-9/ 

And some additional function in the notebook is listed here:
https://pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/

In this tutorial, you will use the following files in the repo frequently to test the code and practice coding. For more information about the code, please check out each of the files.

'pong_game.py'
This is the main script run the game and play with different mode (arguments) in the game.

'color_identification.py'
This is made to isolate specific colour spectrum, which faciliates colour tracking

'color_ranges.json'
This is made to store the colour profile from color_identification.py and is used in 'pong_game.py'

'tutorial.ipynb'
This is for you to practice coding and finish interesting tasks designed in the tutorial.
If you have a favourite python IDE (such as pycharm, spyder, VS code), feel free to test your 'tutorial.ipynb' there


To set up python environment, I use anaconda and below is the instruction to install dependencies in a conda virtual environment (skip the basic step and just install dependencies via pip if you do not want to use conda environment)

Install the latest anaconda version for your operating system (https://www.anaconda.com/products/individual).

Open the anaconda prompt and create a virtual environment via conda 

Create the virtual environment with the 'requirements.txt' file

```
conda create --name kscb_2024 --file requirements.txt
```

or type in the following commands.

```
conda create --name kscb_2024 --channel conda-forge python=3.11
conda activate kscb_2024
pip install pygame opencv-python notebook imutils
```

Once the virtual enviroment in your PC is activated. Move to this repository and enjoy the game.

I would recommend you to start with
```
python pong_game.py -o -b
```
or
```
python pong_game.py -s
```
to get some favour of the game before moving on to use computer vision to control the striker. For more information, check out 'pong_game.py' or 'tutorial.ipynb'