# Nursissimo 
## Gestion de tournée des infirmiers

### Atelier Développement Logiciel 
#### 2018-2019

*Louis Cassedanne, Maxime Dieudonné, Charles de la Roche, Hippolyte Lévêque,  Alix Mallard, Romain Pascual*



# 1. Description du projet

## Enjeux sous-jacents

Les cabinets d'infirmiers ont un fonctionnement très spécifique à leur activité qui consiste en une répartition des soins à effectuer chez les patients au sein de toute l'équipe. Si celle-ci est mal faite, cela peut conduire à une perte considérable de temps / d'argent, et donc d'efficacité. Plus encore, cela peut contraindre le cabinet à refuser des rendez-vous à certaines dates si les interventions des infirmiers ne sont pas optimisées.
En particulier, les trajets effectués par les infirmiers sont évidemment la première source potentielle de perte de temps : Il paraît inconcevable qu'un infirmier ait à effectuer un soin au nord de la région parisienne chez un patient A, et le suivant tout au sud alors que certains de ses collègues iront en même temps réaliser des soins à proximité du patient A. 

## Notre solution

La solution que nous proposons se veut simple et efficace, sous la forme d'une application web:
- Celle-ci permet au compte administrateur du cabinet de: 
  - Créer des comptes infirmiers
  - Créer des comptes patients
  - Gagner du temps graĉe à une interface spécialement pensée pour la prise de rendez-vous par téléphone.
- Pour les infirmiers, l'interface permet de: 
  - Modifier ses informations personnelles et professionnelles (prise en charge de soins, demande de congés)
  - Visualiser son parcours de la prochaine journée (24 heures avant le début de celle-ci)
- Le tout est géré par un optimiseur qui prend en compte tous les rendez-vous d'une demi-journée (Voir section 3.1 pour la description complète)

## Les améliorations

Voici les pistes d'améliorations prioritaires pour une v2 du projet:
- Notre optimiseur devrait être capable de prendre en compte des rendez-vous à des horaires fixes. Si un patient doit recevoir un soin toutes les semaines, le même jour à la même heure, nous ne pouvons pas nous permettre de lui assurer seulement que son soin aura lieu à un moment dans la demi-journée (pour des raisons médicales évidentes).
- A l'heure actuelle, les compétences professionnelles des infirmiers sont renseignées dans la base de données, mais pas prise en compte dans l'optimisation. Cette contrainte devrait donc également être rajoutée durant le processus d'optimisation dans notre v2. 

Nous listons désormais ici les améliorations secondaires (qui permettent essentiellement un meilleur workflow d'utilisation de notre application):
- implémentation d'alertes SMS/mails tant pour les infirmiers que pour les patients, afin de les informer des prochains rendez-vous qui arrivent.
- Possibilité de valider un rendez-vous a posteriori si celui-ci a bien eu lieu, ou de l'invalider dans le cas contraire (contre-temps précisé au même moment par l'infirmier dans l'application)
- Sur un smartphone, notre interface de vue du planning de la journée pour un infirmier pourrait directement lancer l'application "Google Maps" avec le guidage vers la prochaine destination.


# 2. Vue d’ensemble de l’architecture

## Architecture globale

Nous avons décidé d'utiliser l'architecture suivante pour notre projet :
- Flask pour le back et le serveur
- SQL Alchemy pour les bases de données
- Bootstrap pour le Front
- AMPL pour la résolution des problèmes linéaires

## Choix du framework Flask

Flask est un microcontroller pour développement Web qui présente de nombreux avantages pour effectuer un projet de développement de logiciel.

![Flask logo](/dev_log/static/flask_logo.png)
##### Minimaliste et simpliste
Flask est très petit. C'est un framework qui n'installe que très peu d'éléments (environ 2000 lignes de codes) et qui s'apprend très rapidement. A l'inverse de Django, la courbe d'apprentissage pour entamer une application est très courte. Il n'y a pas de restrictions et on a une liberté totale d'implémenter ce que l'on veut comme on le veut.
##### Flexible et étendable
Le framework est très flexible et très bien conçu. Même si Flask reste un micro framework et ne peut donc pas tout faire, il est très évolutif et on peut ajouter les fonctionnalités désirées assez facilement. La structure de l'application dépend vraiment de ses choix, il y a uniquement quelques spécifications prédéfinies mais il est facile de les détourner si l'on veut.
##### Système de routage et Blueprints
Le système de routage (dit "routing") est très intuitif sur Flask avec l'utilisation de décorateurs pour définir certaines routes. Les "Blueprints" sont comme des modules pour l'application.
##### Serveur web et debogage
Il est possible d'exécuter le serveur web intégré à Flask et de voir son application fonctionner sans encombres. De surcroît, Flask est livré avec un débogueur intégré au navigateur qui est très utile lorsque l'on développe.
##### Notre organisation 
Notre back est organisé sur le principe du MVC : model-view-controller.
Nous avons décidé de séparer notre application en plusieurs blueprints. Chaque blueprint correspond à une route principale à laquelle sont associées de nombreuses sous-routes. L'ensemble de nos fonctions se situent dans le controller associé au blueprint. Nos modèles sont définis à l'aide d'une ORM présentée ci-dessous. L'ensemble des "views" associés à nos routes se trouvent dans un dossier template et s'appuient sur Bootstrap.

## Choix de SQL Alchemy

SQL Alchemy est un outil de mapping objet-relationnel très utilisé par la communauté des développeurs Python.

![SQL Alchemy logo](/dev_log/static/sqlalchemy_logo.jpg)
##### L'avantage des ORM
Le technique de mapping relationnel (ou object relationnal mapping - ORM) est une technique de programmation informatique qui crée l'illusion d'une base de données orientée objet à partir d'une base de données relationnelle en définissant des correspondances entre cette base de données et les objets du langage utilisé. Les ORM permettent une manipulation bien plus simple des données. L'écriture des requêtes et l'ensemble des opérations sur les bases de données (sélection, jointure, projection) sont extrêmement simplifiées. Enfin, les ORM permmettent de mieux organiser son code dans l'esprit MVC (model view controller).
##### Notre organisation
Nous avons décidé de séparer notre modèle en plusieurs classes : cabinet, infirmiers, patients, rendez-vous, soins, rendez-vous planifiés. Les classes sont reliées entre elles par des "foreign keys" et des "relationships" afin de pouvoir effectuer des jointures de façon très simple.

## Choix de Bootstrap 
![Bootstrap logo](/dev_log/static/bootstraps_logo.png)
##### Facilité de prise en main
Cette collection d’outil destinée à la création de sites internet et d’application web a été choisie pour sa facilité de prise en main. Chaque membre de l’équipe ayant initialement un profil bien plus orienté vers le Back End et le développement en python, l’aspect efficace, intuitif et simple de Bootstrap a semblé être la meilleure des solutions.
##### L'aspect "responsive"
Les thèmes proposés par Bootstrap permettent, depuis la v2, de concevoir des applications et sites web “adaptatifs”, c’est-à-dire s’adaptant dynamiquement au support sur lequel ils sont utilisés (Ordinateurs, tablettes, smartphones…). Ceci est important pour nous car l’application sera utilisée par des infirmiers en déplacement, qui doivent donc pouvoir l’utiliser notamment depuis leurs smartphones.
##### Composants disponibles
Le Framework Bootstrap propose directement les définitions de base de tous les composants HTML, ainsi que de nombreux éléments graphiques standardisés et prêts à l’emploi.

## Choix d'AMPL

A Mathematical Programming Language (AMPL) est un langage de modélisation algébrique qui permet de décrire et de résoudre de larges problèmes d'optimisation.

![AMPL logo](/dev_log/static/AMPL_logo.jpg)

##### Gratuit et Simple d'utilisation

AMPL est très simple d'utilisation et gratuit pour une utilisation scolaire. Il suffit d'incorporer les différents fichiers et les solveurs souhaiter pour pouvoir l'utiliser dans un projet. AMPL possède par ailleurs une bibliothèque python (amplpy) qui permet de l'utiliser simplement depuis un programme python.

##### AMPL IDE

AMPL possède une IDE qui (AmplIde) qui permet de run les différents programmes linéaires en dehors de l'application. Cela simplifie grandement le debuggage. Par ailleurs, cela permet de définir le programme linéaire directement dans l'IDE
et ainsi d'éditer seulement le jeu de données dans l'application.

##### Compatibilité

AMPL est compatible avec Linux, MacOS et Windows (sous réserve d'ajouter les bonnes librairies), ce qui rend son uilisation plus versatile.

# 3. Architecture détaillée de chaque entité

## Utilisation

API permet lancement de l'app, connexion au front end etc.. ??

justification de l’algo

Configuration

## Modèle

### Schéma de classe, Base de données

__Office__

La classe `Office` contient les informations relatives au cabinet. Chaque cabinet possède un identifiant qui permet de récupérer les infirmiers travaillant au sein du cabinet et les patients qui y sont rattachés. 

__Nurse et Patient__

Les classes centrales sont les classes `Nurse` et `Patient`, héritant toutes les deux de la classe `BasePerson` qui contient des attributs caractéristiques d’une personne (adresse email, téléphone etc). 
Grâce à SQLAlchemy les tables `nurse` et `patient` contiennent les colonnes correspondantes ce qui permet de garder les informations des infirmiers et patients, de les modifier, supprimer ou d’ajouter des nouveaux.
Comme précisé pour la classe `Office`, les deux classes possèdent un attribut `office_id` qui permet d’identifier le cabinet auquel la personne est rattachée.

__Appointment et Schedule__

Les classes `Appointment` et `Schedule` sont très similaires, en effet à terme un objet de la classe `Appointment` possède un alter ego dans la classe `Schedule` (après que l'optimiseur ait tourné).
En effet on stocke dans la table `appointment` les informations liées à la demande de rendez-vous réceptionnée par le cabinet (identifiant du patient qui demande, soin demandé, date et demie journée).
La veille du jour du rendez-vous l'optimiseur attribue le rendez-vous à un infirmier et grâce au trajet qu'il lui donne on peut définir une horaire à ce rendez-vous. Ces informations sont stockées 
dans la table `schedule` pour stocker les résultats de l'optimiseur à part et simplifier les échanges.

__Absence__

La table `absence` associée à cette classe permet de stocker les absences des infirmiers afin de ne pas leur affecter de rendez-vous durant celles-ci.
Chaque absence est donc associée à un infimier via son identifiant. Etant donné que l'optimiseur tourne par demie-journée, on note la date et la demie-journée durant laquelle l'infimier ne sera pas disponible.  

__Care__

Cette classe contient les soins que peuvent fournir les infirmiers. Chacun possède un identifiant, qui permet notamment de repérer le soin associé à un rendez-vous,
ainsi qu'une description et la durée associée à la prestation de ce soin. Nous n'avons stocké qu'une petite dizaine de soins mais il est tout à fait possible d'en rajouter qutant que nécessaire.


![Schéma de classe](classes_DevLog.png)
_Schéma de classes_

![Schéma BDD](erd_from_sqlite.png)
_Schéma de la base de données_

## Interactions

### Diagramme de séquence d'authentification

![Diagramme de séquence 1](dev_log/static/diag_seq_1.png)

### Diagramme de séquence de prise de rendez-vous

![Diagramme de séquence 2](dev_log/static/diag_seq_2.png)
