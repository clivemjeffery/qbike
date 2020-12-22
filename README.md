# qbike
ANT+ Cycling Training on Raspberry Pi.

This is a simple hobby project using python, inspired and kickstarted by
* http://www.johannesbader.ch/2014/06/track-your-heartrate-on-raspberry-pi-with-ant/

It requires the following useful libraries:
* python-ant
* PyQt4
* pyqtgraph

[This video](http://youtu.be/lVoNQ8jtVbI) shows it working.

## Update 2020 - Number 1

I had some issues getting the old code to work and had rather forgotten a lot of what went on before.

Software rot is not just in the code and systems; brain too, I think. Anyway...

I found the IDs in the setup were set to 1009, which seems to be the Garmin product. I switched to 1008 for the Suunto but
still no joy. I found a hardcoded 1009 in the ant.core and changed it to 1008 but that had probably been there when
everything was working before. I don't think the error was to do with vendor and product IDs (but it might).

**qbike** works now first time of starting after inserting the Movestick Mini or if you press the 'Start' button again after
getting the blocking error in ```_start_antnode_``` and Ctrl-C'ing in the terminal window that launched it.

## Update 2020 - Number 2 (December)

Talk about forgotten... I'm working through trying the project out on old PCs. I have an HP laptop with Ubuntu 20.04 and,
if it works here, I'll repeat the setup and install steps on a mini PC. So....

### Install python and set up development environment

First update and upgrade apt

```
$ sudo apt update
$ sudo apt -y upgrade
$ sudo apt autoremove
```

Then check the local python (it is included with Ubuntu) and install pip:

```
$ python3 -V
Python 3.8.5
```
The current version of Python is 3.9.1 and I added that version during the updates described here. TODO: Check the following:

```
$ sudo apt install -y python3.9
$ sudo apt install -y python3.9-pip
$ sudo apt install -y python3.9-venv
```
This installs the latest python, pip and venv alongside the system installed version. Venv is installed because using a virtual environment is the way to choose which one to use for a project.

Intialise and test with a minimal Hello World python program:

```
$ mkdir rep
$ cd rep
$ python3.9 -m venv env
$ source ./env/bin/activate
(env)$ which python
/home/.../env/bin/python
(env)$ python hello.py
Hello, World of Python.
$ deactivate
```

Install git and/or GitKraken:

```
$ sudo apt install git
$ sudo snap install gitkraken --classic
```

If using GitKraken, load the app, log to GitHub and clone the qbike repo. If just using git, clone it from the command line as usual.

I added environments to qbike, on the first run-through using the system python3.8 and secondly using python3.9. For example:

```
$ cd  ~/rep/qbike
$ python3.9 -m venv env9
```

I ensured that `env*/` is `.gitignore`d. Now activate the environment and, if necessary, upgrade pip:

```
$ source ./env9/bin/activate
$ python -m pip install --upgrade pip
```

### Check the QBike packages

Next I looked at the qbike required packages.

#### Ant+ Libraries

There was little chance with the original python-ant, which is a very old library. It isn't availble via pip3, possibly because it was for python2 or perhaps it has been deprecated and removed.

There is a rewritten implementation at half2me/libant which I've cloned and successfully used against the Movestick for both HR and Speed/Cadence sensors. That's good news.

Steps to clone and set up libant into the qbike environment and run copies of the demos (note that it is QBike's environment that is used):

```
$ cd ~/rep
$ git clone https://github.com/half2me/libant.git
$ cd qbike
$ env9/bin/activate
$ pip install -e ../libant
```

The last command uses pip to install the library into the qbike environment in 'edit' mode. This is good for development where you might be changing the library and, apparently, means that you don't need to keep re-installing it. See what happens if you make changes in the library.

When you plug in the Movestick, it gets mounted automatically as /dev/ttyUSB0 (or another number, presumably, is there are other USB devices connected). By default, Ubuntu users don't have access to this as a serial device. According to the libant README.md, there is/was a bug using it via the USB driver (try it to see if still a problem).

The serial driver works if you add your user to the tty and dialout groups. The command shown in libant's README works, but you need to log out or restart for the permissions to take effect (but maybe just unplugging and replugging the Movestick would have worked).

```
$ sudo adduser purple dialout
```

Then I copied a couple of the demos into qbike and tried them out. They work!

#### Qt library

It seemed sensible to upgrade to PyQt5, which is the latest stable version. First, I tried it out in a separate project with its own environment. Starting withou an activated environment:

```
$ cd ~/rep
$ mkdir tryqt
$ cd tryqt
$ python3.9 -m venv env9
$ source env9/bin/activate
$ pip install pyqt5
```

The apt package for PyQt5 did not install all dependencies at the time of us. A progrm to put up a window with a 'Hello World' title, failed, as follows:

```
$ python helloQt.py
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
```

After the message shown above, the process crashed and core dumped. The solution was to install a missing library:

```
$ sudo apt install libxcb-xinerama0
```

The HR/time plot in QBike is made with PyQtGraph and this now works with Qt5.

```
$ pip install pyqtgraph
```

A test program with this library ran successfully.

Upgrading qbike to PyQt5 was straightforward with very few changes to the code. The new way to deal with signals and slots required changes to the way the push buttons were 'wired up'. I'd imported a configuration package (and hardly used it) that does not seem to be supported under 5, so I just removed it.

See `q5bike.py` which now runs in simulation mode.

#### Integrating both PyQt5 and libant

This was surprisingly successfull with only a few hours work. A libant Node can be created and a message reading callback set to it. Messages of different types may arrive at any time, so the `readNodeMessage` callback just copies the desired values from each type of message. The separate callback, `timerFunction` fetches the current values into the display accumulators every second.

Since libant also picks up speed-cadence sensor messages, these have been easy to add using the hooks I put in the first time around. The display layout needs some tweaking to accommodate them as originally intended.

See `q5hrsc.py`

## Next steps

* Add more 'columns' to the display for speed and cadence.
* Read or calculate distance and display somewhere.
