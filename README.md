# Robotic Positioning Controller

This project was designed to allow easier use of the Arrick C4 Motor
controllers and generate contour plots based on measurement data. The
code was written in Python 2.7.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

It is recommended that you install an **I**ntegrated **D**evelopment **E**nvironment (IDE) for viewing and running Python files. [PyCharm](https://www.jetbrains.com/pycharm/download/) is recommended as it does not require admin privileges. 

Spyder should also work and it comes preinstalled with [Anaconda]((https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation)).
Future versions should include a Jupyter Notebook to make data management testing easier.

It is also assumed that you already have a built XY Positioning system (either 18 or 30 inch model). This code will simply
help make controlling the motors more intuitive.

### Installing

1. First, install the latest version of Python 2.7 from the following [link](https://www.python.org/downloads/). Make sure you
are downloading **Python 2.7** and NOT Python 3. You may also choose to install [Anaconda or Miniconda](https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation) to manage the packages
we will be using.

2. Install an IDE such as [PyCharm](https://www.jetbrains.com/pycharm/download/) or use Spyder (included in Anaconda)

3. You must then open up the "Terminal" inside the IDE you are using to run the following command to install relevant packages.
Unfortunately these packages take up a sizable amount of space so ensure that the computer you are working on has at least 1 GB of room.

4. Run the following command to install all packages at once:

```bash
pip install numpy matplotlib Gooey pyserial
```

Alternatively, if you are using Anaconda, use the following command:

```bash
conda install numpy matplotlib Gooey pyserial
```

=======

## Deployment

Add additional notes about how to deploy this on a live system

Open the file ["basic_xy_positioner_gui.py"](basic_xy_positioner_gui.py) in your favorite IDE and click run.
Running from the command line on Linux/Mac systems can be done by simply typing:

```bash
python basic_xy_positioner_gui.py
```

Make sure that it is configured to be executable by using:

```bash
chmod +x basic_xy_positioner_gui.py
```

For Windows 10, you must first configure your PATH variables in order to run python from the command line. Follow the steps
on this [site](https://superuser.com/questions/143119/how-to-add-python-to-the-windows-path) to learn how to add Python to the PATH.
Note that this is completely optional and that the program can still be run through an IDE.

The GUI should pop up with options that you may define. Additional parameters can be tweaked by modifying the source files.

It may be necessary to purchase a USB-to-Serial cable as the one currently in use is liable to
breaking. Ensure that the stopper is in place for motor 1 on the 30 inch system to ensure homing
works correctly.

### Running an Area Scan

##### Required Arguments

==========

* Input the dimensions of the object (x goes across and is controlled by motor #1, y goes up and down by using motor #2) into *x_distance* and *y_distance*.
* The *grid_step_dist* selects how far apart each measurement point should be.
* The *dwell_time* is by default set to 1, but can be changed to 0 to allow for the user to wait an indefinite amount of time before inputting a value.

##### Optional Arguments

==========

* The *filename* is a prefix that will appear at the beginning of all resulting file output. All output can be found in the folder
`results/` which will be automatically generated if not present.
* The *measure* setting can be turned off to simply observe how the motors are stepping through the grid.
* The *auto_zoom_scan* setting will automatically conduct a zoom scan over the point with the highest value after travelling
to it. Zoom scan data is stored separately from area scan data.

The default settings create a 4x6 grid with spacing of 2.8 cm with a 1 second dwell time. The default file prefix is "raw_values" and the automatic zoom scan is not conducted.

### Moving to a Grid Position

### Running a Zoom Scan

### Manual Control

## Built With

* [Python](https://www.python.org/) - This code base was written in Python 2.7.14
* [PySerial](https://github.com/pyserial/pyserial) - Dependency Management
* [Numpy](http://www.numpy.org/) - Used for matrix manipulations and structuring data
* [Matplotlib](https://matplotlib.org/) - Used for interpolation and contour plotting
* [Gooey](https://github.com/chriskiehl/Gooey) - Used to construct initial menu selection

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests.

## Authors

* **Ganesh Arvapalli** - *Software Engineering Intern* - [garva-pctest](https://github.com/garva-pctest)

Originally written for the internal use of PCTEST Engineering Lab, Inc.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Andrew Harwell
* Baron Chan
* Kaitlin O'Keefe
* Steve Liu
* PCTEST Engineering Lab, Inc.
