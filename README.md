# dev_log_tournees_infirmiers
=======
Ce repo correspond au projet scolaire "Tournées des infirmiers" de l'électif Développement logiciel.

Makefile
========

Makefile allows you to run some usefull terminal command.

For instance, you can quickly install all the dev_log project as a standart python library on your virtual environnement.
To do so, right after cloning the project from GitHub, just run:

    $ make install

Make sure you have the `wheel` python library installed before. If not, run:

    $ pip install wheel

Now, everything should work properly, you can run every script contained in `scripts` directory in your terminal. We created `dev_log_hello_world` for you to try !


N.B. : You can create as much Makefile commands as you want, following the same syntax as the existing ones. For instance, the `make clean` command will remove all useless stuff automatically created in the repository, as defined in the makefile.

dev_log
=======

This is where all stuff is coded. Put every .py file here.

scripts
=======
Create some scripts to test your code and run it in terminal 
