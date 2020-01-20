# qbike
ANT+ Cycling Training on Raspberry Pi.

This is a simple hobby project using python, inspired and kickstarted by
* http://www.johannesbader.ch/2014/06/track-your-heartrate-on-raspberry-pi-with-ant/

It requires the following useful libraries:
* python-ant
* PyQt4
* pyqtgraph

[This video](http://youtu.be/lVoNQ8jtVbI) shows it working.

## Update 2020

I had some issues getting the old code to work and had rather forgotten a lot of what went on before. Software rot is not just in the code and systems; brain too, I think. Anyway...

I found the IDs in the setup were set to 1009, which seems to be the Garmin product. I switched to 1008 for the Suunto but still no joy. I found a hardcoded 1009 in the ant.core and changed it to 1008 but that had probably been there when everything was working before. I don't think the error was to do with vendor and product IDs (but it might).

**qbike** works now first time of starting after inserting the Movestick Mini or if you press the 'Start' button again after getting the blocking error in antnode_start and Ctrl-C'ing in the terminal window that launched it.
