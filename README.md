#AQoPA

Automated Quality of Protection Analysis tool of QoP-ML models. AQoPA is available in two modes: console and GUI mode.

[Project Homepage](http://qopml.org)

*Instruction for **pip** and **virtualenv** users is below.*


##INSTRUCTIONS FOR GNU/LINUX

### INSTALLATION

Instalation steps for GNU/Linux (Debian, Ubuntu)

1. Install **Python 2.7** ```sudo apt-get install python```
2. Install **wxPython 2.8** ```sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n```
3. Install pythpn **PLY** package ```sudo apt-get install python-ply```
4. Download and extract AQoPA from [http://qopml.org/aqopa/](http://qopml.org/aqopa/)

Instalation steps for GNU/Linux (CentOS, Fedora, OpenSUSE, RedHat)

1. Install **Python 2.7** ```yum install python```
2. Download and install **wxPython 2.8** from [http://www.wxpython.org/download.php](http://www.wxpython.org/download.php)
3. Install pythpn **PLY** package ```yum install python-ply```
4. Download and extract **AQoPA** from  [http://qopml.org/aqopa/](http://qopml.org/aqopa/)

### RUN

####GNU/Linux GUI version:
python bin/aqopa-gui

####GNU/Linux console version:
python bin/aqopa-console

Run 'python bin/aqopa-console -h' to see all available options.


##INSTRUCTIONS FOR MICROSOFT WINDOWS

Tested on Windows 7.

### INSTALLATION 

1. Download and install **Python 2.7** from [http://www.python.org/download/releases/2.7.6/](http://www.python.org/download/releases/2.7.6/) (Python will be installed into "C:\Python27" directory by default.)
2. Add Python directory to environment variable PATH:
 - Open command line as Administrator: *Start > cmd (mouse right-click -> Run as Administrator)*
 - Run ```wmic ENVIRONMENT where "name='Path' and username='<%USERNAME%>'" set VariableValue="%Path%;C:\Python27\"```
 - Restart Windows
3. Download and install **wxPython 2.8** from [http://www.wxpython.org/download.php#stable](http://www.wxpython.org/download.php#stable)
4. Download and extract python **PLY 3.4** package from [http://www.dabeaz.com/ply/](http://www.dabeaz.com/ply/)
5. Install **PLY 3.4**:
 - Open command line: *Start > cmd*
 - Go to extracted directory with **ply-3.4**
 - Run ```python setup.py install```
6. Download and extract **AQoPA** from website: [http://qopml.org/aqopa/](http://qopml.org/aqopa/)

### RUN     

#### Microsoft Windows GUI version:
1. Go to extracted AQoPA directory.
2. Double click **aqopa-gui**


#### Microsoft Windows console version:
1. Open command line: *Start > cmd*
2. Go to extracted AQoPA directory.
3. Run **python bin/aqopa-console -h** to see all available options.

---

## INSTRUCTIONS FOR PIP & VIRTUALENV USERS


## INSTRUCTIONS FOR GNU/LINUX

### INSTALLATION

#### Instalation steps for GNU/Linux (Debian, Ubuntu)

1. Install **PIP** ```sudo apt-get install python-pip```
2. Install **PLY 3.4** using pip ```sudo pip install PLY```
3. Install **AQoPA** using pip ```sudo pip install AQoPA```

#### Installing wxPython without virtualenv:
4. Install **wxPython 2.8** ```sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n```

####Installing wxPython with virtualenv:
When using **virtualenv** the **wxPython** package may not be installed in the virtual environment. It is installed into the global python environment.
In order to make wxPython visible in virtual environment you need to create wx files in your virtual environment.

We assume that using **apt-get** the **wxPython** package has been installed in "/usr/lib/python2.7/dist-packages/" directory and the content of wx.pth file is "wx-2.8-gtk2-unicode". Otherwise, you have to find out where is wx.pth file and check its content.

4. Install **wxPython 2.8** ```sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n```
5. Update **wxPython paths**. Replace with the path of virtualenv you have created: 
 - ```echo "/usr/lib/python2.7/dist-packages/wx-2.8-gtk2-unicode" > <virtual_env_path>/lib/python2.7/site-packages/wx.pth```
 - ```ln -s /usr/lib/python2.7/dist-packages/wxversion.py <virtual_env_path>/lib/python2.7/site-packages/wxversion.py```

### RUN

#### GNU/Linux GUI version:
Run aqopa-gui command: **aqopa-gui**

#### GNU/Linux console version:
Run aqopa-console command: **aqopa-console**
Run **aqopa-console -h** to see all available options.


## INSTRUCTIONS FOR MICROSOFT WINDOWS

Tested on Windows 7.

### INSTALLATION 

1. Download and install **Python 2.7** from [http://www.python.org/download/releases/2.7.6/](http://www.python.org/download/releases/2.7.6/) (Python will be installed into "C:\Python27" directory by default.)
2. Download and install **wxPython 2.8** from [http://www.wxpython.org/download.php#stable](http://www.wxpython.org/download.php#stable)
3. Download and run **pip-win 1.6** from [https://sites.google.com/site/pydatalog/python/pip-for-windows](https://sites.google.com/site/pydatalog/python/pip-for-windows) (Pip-win win install some Python packages after first run.)
4. Install **PLY** using **pip-win**. Write **pip install PLY** in the text input and click Run.
5. Install **AQoPA** using **pip-win**. Write **pip install AQoPA** in the text input and click Run.

### RUN 

#### Microsoft Windows GUI version:
1. Open directory "C:\Python27\Scripts" (assuming that Python has been installed in "C:\Python27").
2. Double click **aqopa-gui.exe**

#### Microsoft Windows console version:
1. Open command line (cmd).
2. Go to "C:\Python27\Scripts" (assuming that Python has been installed in "C:\Python27").
3. Run **aqopa-console.exe -h** to show the help of AQoPA console command.


