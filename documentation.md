# Nursissimo 
## Gestion de tournée des infirmiers

### Atelier Développement Logiciel 
#### 2018-2019

*Louis Cassedanne, Maxime Dieudonné, Charles de la Roche, Hippolyte Lévêque,  Alix Mallard, Romain Pascual*



Section #1: description du projet
========

 éventuellement les améliorations


Section #2: Vue d’ensemble de l’architecture
========

### SQLalchemy :
### Flask :
### Bootstrap : 
Cette collection d’outil destinée à la création de sites internet et d’application web a été choisie pour sa facilité de prise en main. Chaque membre de l’équipe ayant initialement un profil bien plus orienté vers le Back End et le développement en python, l’aspect efficace, intuitif et simple de Bootstrap a semblé être la meilleure des solutions :
Les thèmes proposés par Bootstrap permettent, depuis la v2, de concevoir des applications et sites web “adaptatifs”, c’est-à-dire s’adaptant dynamique au support sur lequel ils sont utilisés (Ordinateurs, tablettes, smartphones…). Ceci est important pour nous car l’application sera utilisée par des infirmiers en déplacement, qui doivent donc pouvoir l’utiliser notamment depuis leurs smartphones.
Le Framework Bootstrap propose directement les définitions de base de tous les composants HTML, ainsi que de nombreux éléments graphiques standardisés et prêts à l’emploi.
 

Flask, front en boostrap, SQLalchemy et justifier les choix


Section #3: Architecture détaillée de chaque entité
========

### Utilisation

API permet lancement de l'app, connexion au front end etc.. ??
SQLAlchemy à détailler (ORM)
justification de l’algo
Configuration

### Modèle

Schéma de classe, BDD 
Office
La classe Office contient les informations relatives au cabinet. Chaque cabinet possède un identifiant qui permet de récupérer les infirmiers travaillant au sein du cabinet et les patients qui y sont rattachés. 
Nurse et Patient
Les classes centrales sont les classes Nurse et Patient, héritant toutes les deux de BasePerson qui contient des attributs caractéristiques d’une personne (adresse email, téléphone etc). Grâce à SQLAlchemy les tables Nurse et Patient contiennent les colonnes correspondantes ce qui permet de garder les informations des infirmiers et patients, de les modifier, supprimer ou d’en ajouter des nouveaux.
Comme précisé pour la classe office, les deux classes possèdent un attribut office_id qui permet d’identifier le cabinet auquel la personne est rattachée.
Appointment

diagramme de séquence (mettre 1 pour office et 1 pour nurse)
