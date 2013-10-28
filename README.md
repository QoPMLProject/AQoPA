# AQoPA

**Automated Quality of Protection Analysis** tool of QoP-ML models

**[Project Homepage][home]** 

# Quick Installation in 3 steps

Assuming that you use **apt-get** and you do not use **virtualenv**.
```
sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n
```
```
wget https://github.com/QoPMLProject/AQoPA/archive/master.zip
```
```
pip install AQoPA-master.zip
```

## Run

```
aqopa-gui
```

---

# Download

AQoPA can be downloaded as ZIP file using **[this][aqopa]** link.

```
wget https://github.com/QoPMLProject/AQoPA/archive/master.zip
``` 

# Installation

AQoPA is written in Python and needs Python in version 2.7 or newer.
We also recommend using **virtualenv**. You can find more informations **[here][virtualenv]** 

## Requirements

AQoPA needs following packages:

```
PLY
```

```
numpy
```

They will be installed during AQoPA installation automatically or can be installed manually using **pip** command. 

## Installation

AQoPA can be installed from ZIP file with **pip** command:

```
pip install AQoPA-master.zip
```

# Modes Setup

AQoPA can be used in two modes: console and GUI mode. Console mode does not need additional setup.

## Setup GUI Mode

AQoPA GUI is built with **[wxPython][wxPython]**. 
You need to install wxPython GUI toolkit to use GUI mode of AQoPA. Installations instructions are available **[here][wxPythonInstall]**.

Ubuntu users just need to install 3 packages: **python-wxgtk2.8 python-wxtools wx2.8-i18n**.

```
sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n
```

## wxPython and virtualenv

When using **virtualenv** the **wxPython** package may not be installed in the virtual environment. It is installed into the global python environment.

In order to make **wxPython** visible in virtual environment you need to create **wx** files in your virtual environment. 

We assume that using **apt-get** the **wxPython** package has been installed in "/usr/lib/python2.7/dist-packages/" directory and the content of **wx.pth** file is "wx-2.8-gtk2-unicode". Otherwise, you have to find out where is **wx.pth** file and check its content. 

```
echo "/usr/lib/python2.7/dist-packages/wx-2.8-gtk2-unicode" > <virtual_env_path>/lib/python2.7/site-packages/wx.pth
```
```
ln -s /usr/lib/python2.7/dist-packages/wxversion.py <virtual_env_path>/lib/python2.7/site-packages/wxversion.py
```

# Run

## Run Console Mode

Run **aqopa-console** file with **-h** option to view all available options.

```
aqopa-console -h 
```

## Run GUI Mode

Run **aqopa-gui** file.

```
aqopa-gui 
```

[home]: http://qopml.org
[aqopa]: https://github.com/QoPMLProject/AQoPA/archive/master.zip
[virtualenv]: http://www.virtualenv.org/en/latest/
[wxPython]: http://www.wxpython.org/
[wxPythonInstall]: http://www.wxpython.org/download.php#stable
