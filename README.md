# Robotic Positioning Controller

This project was designed to allow easier use of the Arrick C4 Motor
controllers and generate contour plots based on measurement data. The
code is compatible with Python 2.7.x and was originally written in
Python 2.7.14

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

It is recommended that you install an IDE for viewing and running Python files. PyCharm is recommended as it does not require admin privileges. 
Spyder should also work and it comes preinstalled with Anaconda. Future versions should include a Jupyter Notebook to make data management testing easier.


```
Give examples
```

### Installing

1. First, install the latest version of Python 2.7 from the following [link](https://www.python.org/downloads/). Make sure you
are downloading **Python 2.7** and NOT Python 3. You may also choose to install [Anaconda or Miniconda](https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installation) to manage the packages
we will be using.

2. You must then open up the "Terminal" inside the IDE you are using to run the following command to install relevant packages.
Unfortunately these packages take up a sizable amount of space so ensure that the computer you are working on has at least 1GB of room.

3. Run the following command to install all packages at once:

```bash
pip install numpy matplotlib Gooey pyserial
```

Alternatively, if you are using Anaconda, use the following command:

```bash
conda install numpy matplotlib Gooey pyserial
```

End with an example of getting some data out of the system or using it for a little demo


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

## Built With

* [Python](https://www.python.org/) - The code base was entirely written in Python 2.7.14
* [PySerial](https://github.com/pyserial/pyserial) - Dependency Management
* [Numpy](http://www.numpy.org/) - Used for matrix manipulations and structuring data
* [Matplotlib](https://matplotlib.org/) - Used for interpolation and contour plotting
* [Gooey](https://github.com/chriskiehl/Gooey) - Used to construct initial menu selection

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

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
