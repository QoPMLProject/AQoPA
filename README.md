# AQoPA

**Automated Quality of Protection Analysis** tool of QoP-ML models. AQoPA is available in two modes: console and GUI mode.

[Project Homepage](http://qopml.org)

---

# Windows

Tested on Windows 7.

## Installation (both modes)

* Download and install **Python 2.7** from [this website](http://www.python.org/download/releases/2.7.6/). Python will be installed into "C:\Python27" directory by default.
* Download and run **pip-win 1.6** from [this website](https://sites.google.com/site/pydatalog/python/pip-for-windows). Pip-win win install some Python packages after first run.
* Install **PLY** using **pip-win**. Write **pip install PLY** in the text input and click Run.
* Install **AQoPA** using **pip-win**. Write **pip install AQoPA** in the text input and click Run. 
* Download and install **numpy 1.7.2** from [this website](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy).

## GUI mode

### Installation 

* Download and install **wxPython 2.8** from [this website](http://www.wxpython.org/download.php#stable).

### Run
* Open directory "C:\Python27\Scripts" (assuming that Python has been installed in "C:\Python27").
* Run file **aqopa-gui.exe**.

### Console mode

### Installation
No additional installation is required.

### Run
* Open command line (**cmd**).
* Go to "C:\Python27\Scripts" (assuming that Python has been installed in "C:\Python27").
* Run **aqopa-console.exe -h** to show the help of AQoPA console command.

---

# Linux (Debian, Ubuntu)

## Installation (both modes)

* Install **PIP**
```
sudo apt-get install python-pip
```
* Install **PLY** using **pip**
```
sudo pip install PLY
```
* Install *numpy** using **pip**
```
sudo pip install numpy
```
* Install *AQoPA** using **pip**
```
sudo pip install AQoPA
```

## GUI mode

### Installation (without virtualenv)
* Install **wxPython 2.8**
```
sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n
```

### Installation (with virtualenv)
When using virtualenv the **wxPython** package may not be installed in the virtual environment. It is installed into the global python environment.

In order to make **wxPython** visible in virtual environment you need to create wx files in your virtual environment.

We assume that using apt-get the wxPython package has been installed in "/usr/lib/python2.7/dist-packages/" directory and the content of **wx.pth** file is "wx-2.8-gtk2-unicode". Otherwise, you have to find out where is **wx.pth** file and check its content.

* Install **wxPython 2.8**
```
sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n
```
* Update **wxPython** paths. Replace **<virtualenv_path>** with the path of virtualenv you have created.
```
echo "/usr/lib/python2.7/dist-packages/wx-2.8-gtk2-unicode" > <virtual_env_path>/lib/python2.7/site-packages/wx.pth
```
```
ln -s /usr/lib/python2.7/dist-packages/wxversion.py <virtual_env_path>/lib/python2.7/site-packages/wxversion.py
```

### Run
Run **aqopa-gui** command.
```
aqopa-gui
```

## Console mode

### Installation
No additional installation is needed.

### Run
Run **aqopa-console** command. Use ***-h*** flag to see help.
```
aqopa-console -h
```
