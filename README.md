# Nursissimo   <img src="dev_log/static/nurse_logo.png" width=60 align=center />

<br/>

## Collaborative school project

Nursissimo is a software for nurses' offices. It allows the nurses' offices to register patients in the database easily,
to make appointments, and to quickly visualize the different nurses timetable depending on the day. Nursissimo also 
allows nurses to check their daily planning, the different appointments and the tips between these appointments. Moreover,
they also can also report their days off.

<br/>

## Installing and running Nursissimo application

**1**. Install the Python `virtualenv` package:

`pip3 install virtualenv` or `pip install virtualenv`

**2**. Go in the directory of your choice and there, create a python virtual environment in the said 
directory and activate it:

`cd ./your_directory`

`virtualenv venv`

- Linux / MacOS: `source venv/bin/activate`

- Windows: `.\venv\Scripts\activate.bat`

**3**. Go in the folder `venv` and clone the github project:

`cd ./venv`

`git clone git@github.com:charlesdlrsa/dev_log_tournees_infirmiers.git`

_If you don't have `git` on your computer, you can download the zip of this project at the top right of this page and unzipped it in your folder `venv` giving it the name `dev_log_tourneees_infirmiers`._

**4**. To use our application, you need to install our requirements. You have two methods according to your computer:

- Linux / MacOs:

`cd ./dev_log_tourneees_infirmiers`

`pip3 install wheel` or `pip install wheel`

`make install`

- Windows:

`cd ./dev_log_tournees_infirmiers`

`pip3 install -r requirements.txt` or `pip install -r requirements.txt`

<br/>

**5**. Run the app:

`python3 run.py` or `python run.py`

<br/>

## Try our features with our database examples

#### Authentification

You can log in with an administrator account. Depending on your office, select the *As Admin* mode and fill in the identifiers : 

- Doctissimo office

`username: doctissimo@hotmail.fr`

`password : password`

- Malakoff office

`username : malakoff@gmail.com`

`password : password`

You can also log in with a nurse account corresponding to the initial database. The following profiles have been initialized :

- Doctissimo office

`username : laurent.cabaret@hotmail.fr`

`username : jpp@hotmail.fr`

`username : celine.hudelot@hotmail.fr`

`username : jeanmarie.detriche@hotmail.fr`

- Malakoff office

`username : pierre.dupont@hotmail.fr`

The passwords are initialized to `password`

<br/>

## Our strengths

#### Our optimizer

Our software use a specific optimizer to determine the different appointments of a nurse in a day. Its goal is to minimize
the transport time of a nurse. 
- It allows the largest number of appointments to a nurse in a reduced geographic area around
the nurse office. 
- Then he gives the best way for every nurse to go the appointments, minimizing the tips time. 
- If it is possible, our optimizer favors walking rather than driving.

#### The Google Maps visualization

We propose to the nurses to visualize their daily tips in a Google Maps map. This functionnality will help them to prepare their daily work.
- The nurse can visualize the complete itinerary of the day in his map, with all the appointement markers on the map.
- The nurse can also visualize a specific tip between two appointments by selecting the destination appointment.
- We differenciate the "driving" tips (in blue) and the "walking" tips (in green).

#### An intuitive use

Our technical choices for this software have a goal : having a simple to use service. Every essential task in a nurses' office have a dedicated tab in our application. We
 
