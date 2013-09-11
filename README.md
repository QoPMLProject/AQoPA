# AQoPA

**Automated Quality of Protection Analysis** tool of QoP-ML models

**[Project Homepage][home]** 

# Download

## Download ZIP file

AQoPA as ZIP file can be downloaded using **[this][aqopa]** link.
```
wget https://github.com/QoPMLProject/AQoPA/archive/master.zip
unzip master.zip
rm master.zip
cd AQoPA-master
``` 

## Download using GIT

You have to clone AQoPA GIT repository.
```
git clone https://github.com/QoPMLProject/AQoPA.git
cd AQoPA
```

# Setup

AQoPA can be used in two modes: console and GUI mode. Console mode does not need additional setup.
We also recommend using **virtualenv**. You can find more informations **[here][virtualenv]** 

## Setup GUI Mode

AQoPA GUI is built with usage of **[wxPython][wxPython]**. 
You need to install wxPython GUI toolkit to use GUI mode of AQoPA. Installations instructions are available **[here][wxPythonInstall]**.

Ubuntu users just need to install 3 packages: **python-wxgtk2.8 python-wxtools wx2.8-i18n**.
```
sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n
```

# Run

AQoPA binaries are located in **bin/** folder.

## Run Console Mode

Run **aqopa-console.py** file with **-h** option to view all available options.
```
cd bin
python aqopa-console.py -h 
```

## Run GUI Mode

Run **aqopa-gui.py** file.
```
cd bin
python aqopa-gui.py 
```

[home]: http://qopml.org
[aqopa]: https://github.com/QoPMLProject/AQoPA/archive/master.zip
[virtualenv]: http://www.virtualenv.org/en/latest/
[wxPython]: http://www.wxpython.org/
[wxPythonInstall]: http://www.wxpython.org/download.php#stable
