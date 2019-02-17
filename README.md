# Nursissimo   <img src="dev_log/static/nurse_logo.png" width=60 align=center />

<br/>

## Collaborative school project

Nursissimo is a software for nurses' offices. It allows the offices to easily register patients and nurses in their database,
to schedule appointments, and to quickly visualize the different nurses schedules depending on the day. Nursissimo applciation also 
allows nurses to check their daily planning, the different appointments and the journeys between these appointments. Moreover,
they also can also report their days off.

<br/>

## Installing and running Nursissimo application

**1.** Install the Python `virtualenv` package:

`pip3 install virtualenv` or `pip install virtualenv`

**2.** Go in the directory of your choice and there, create a python virtual environment in the said 
directory and activate it:

`cd ./your_directory`

`virtualenv venv`

- Linux / MacOS: `source venv/bin/activate`

- Windows: `.\venv\Scripts\activate.bat`

**3.** Go in the folder `venv` and clone the github project:

`cd ./venv`

`git clone git@github.com:charlesdlrsa/dev_log_tournees_infirmiers.git`

_If you don't have `git` on your computer, you can download the zip of this project at the top right of this page and unzipped it in your folder `venv` giving it the name `dev_log_tourneees_infirmiers`._

**4.** To use our application, you need to install our requirements. You have two methods according to your computer:

- Linux / MacOs:

`cd ./dev_log_tourneees_infirmiers`

`pip3 install wheel` or `pip install wheel`

`make install`

- Windows:

`cd ./dev_log_tournees_infirmiers`

`pip3 install -r requirements.txt` or `pip install -r requirements.txt`

<br/>

**5.** Run the app:

`python3 run.py` or `python run.py`

<br/>

## Try our features with our database examples

#### Authentification

You can log in to the application as an office administrator or as an office nurse. <br/>
To try our features, we set in the database two office accounts with their corresponding nurses and patients. <br/>
We advise you to use Massy office's account which is more provided with examples, but feel free to use both accounts.

- Massy office

Admin: `username: massy@hotmail.fr` and `password : password` <br/>
Nurse: `username : laurent.cabaret@hotmail.fr` and `password : password` <br/>
Nurse: `username : jpp@hotmail.fr` and `password : password` <br/>
Nurse: `username : celine.hudelot@hotmail.fr` and `password : password` <br/>
Nurse: `username : jeanmarie.detriche@hotmail.fr` and `password : password` <br/>

- Malakoff office

Admin: `username : malakoff@gmail.com` and `password : password` <br/>
Nurse: `username : nicolas.travers@hotmail.fr` and `password : password` <br/>
Nurse: `username : remi.geraud@hotmail.fr` and `password : password` <br/>

#### Add nurses and patients

Even if our Massy office's account has a lot of nurses and patients, you can try to add new patients or to edit existing nurses by yourself. You will see that we have implemented autocompletion for the postal address by using the Google Maps API and that we check the format of each input (phone number, email address).

#### See and add vacations

By clicking on the button `See vacations` in the nurses list, you can see, add and delete the vacations of a specific nurse. For example, if you go to Laurent Cabaret's vacations, you will see that we display in red the vacations in the past and that the administrator has the power to delete the nurse vacations.

#### See and add appointments

By going to the `Appointments` tab, you can see all the planned appoinments for a specific date or for a specific patient, or for both. <br/>
You can also choose to add a new appointment for a specific patient, a specific care and a specific date. Here, you will see several features we have implemented:

- You cannot add an appointment less than 24 hours before the desired date. This constraint is unfortunatly necessary to allow the nurses to know their exact planning 24 hours before each day.

- By clicking on the button `Search availabilities`, our application will show to the administrator if there are some availabilities to add a new appointment during the week of the selected date. These availabilities are determined in function of the date, of the patient appointments, and of the available nurses. It's our optimizer goal to predict if the nurses will be able to do all the planned appointments more the new appointment during a specific halfday.

For example, you can try to add a new appointment for the patient `Charles de la Roche` on the 24/04/2109.<br/>
You will see that the patient has already an appointment the 26/04/2019, so you cannot add another appointment.<br/>
You will also see that no nurse is available the 23/04/2019 in the morning and that's perfectly normal. Indeed, if you check the vacation of the nurses, you will show that 3 of the 4 nurses are in day off and the only one available has already 7 appointments in the morning.

#### See a nurse planning

By going to the `Planning` tab, you can see the planning of each nurse. Here, you will see several features we have implemented:

- You cannot see a planning more than 24 hours before the desired date. This is due to our optimizer. To set all the appointments to the nurses and optimize their journeys, we need to have all the appointments of the selected half-day. Yet, we can add appointments until 24 hours before a day. Therefore, we must wait that all the possible appointments had been added to launch the optimizer and show the planning of each nurse.

- By clicking on the button `View planning`, our application will launch the optimizer. This last one will attribute the planned appointments to all the available nurses in order to minimize their traveled distance and maximize their walk. Taking into account that a travel duration depends on the traffic and a care duration depends on a patient, we have deliberately planned a margin at the end of the half-day.

For the example, we have autorized the Massy's office administrator to view the planning of the morning on the 02/05/2019 (only this date is autorized in the future). We booked 10 appointments on this date's half-day and we closed the appointment booking for this half-day. <br/>
On this date, two nurses are in vacations so only `Laurent Cabaret` and `Jean-Philippe Poli` are available. You can check the distribution of the appointments done by the optimizer between the two nurses and check their journeys. <br/> <br/>

You can also try to add appointments by yourself for a date and check the planning of the nurses the day before this date. <br/>
If you want to bypass this constraint of the 24 hours to make some tests, you can add appointments using this URL `http://127.0.0.1:5000/appointments/add_appointment/patient-***/date-***/care-1/halfday-Morning` by replacing the stars *** in the URL by a patient id (number between 1 and 14) and the date of tomorrow in this format YYYYY/MM/DD. Feel free to add as many appointments as you want (no more than 14, the number of patients) and then go see the planning of each nurse for tomorrow morning. You will see how our algorithm optimizes the paths.

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

Our technical choices for this software have a goal : having a simple to use service. Every essential task in a nurses' office have a dedicated tab in our application (appointments, nurses, patients,...). The Bootstrap interface gives us this simplicity. It also allows the use of the software on a smartphone (responsive design), an essential issue for the nurses during their trips. 
 
