
# 2. Vue d'ensemble de l'architecture

## Architecture global

Nous avons décidé d'utiliser l'architecture suivante pour notre projet :
- Flask pour le back et le serveur
- SQL Alchemy pour les bases de données
- Bootstrap pour le Front

## Choix du framework Flask

Flask est un microcontroller pour développement Web qui présente de nombreux avantages pour effectuer un projet de développement de logiciel.

![Flask logo](/dev_log/static/logo_flask.png)
#### Minimaliste et simpliste
Flask est très petit. C'est un framework qui n'installe que très peu d'éléments (environ 2000 lignes de codes) et qui s'apprend très rapidement. A l'inverse de Django, la courbe d'apprentissage pour entamer une application est très courte. Il n'y a pas de restrictions et on a une liberté totale d'implémenter ce que l'on veut comme on le veut.
#### Flexible et étendable
Le framework est très flexible et très bien conçu. Même si Flask reste un micro framework et ne peut donc pas tout faire, il est très évolutif et on peut ajouter les fonctionnalités désirées assez facilement. La structure de l'application dépend vraiment de ses choix, il y a uniquement quelques spécifications prédéfinies mais il est facile de les détourner si l'on veut.
#### Système de routage et Blueprints
Le système de routage (dit "routing") est très intuitif sur Flask avec l'utilisation de décorateurs pour définir certaines routes. Les "Blueprints" sont comme des modules pour l'application.
#### Serveur web et debogage
Il est possible d'exécuter le serveur web intégré à Flask et de voir son application fonctionner sans encombres. De surcroît, Flask est livré avec un débogueur intégré au navigateur qui est très utile lorsque l'on développe.
#### Notre organisation 
Notre back est organisé sur le principe du MVC : model-view-controller.
Nous avons décidé de séparer notre application en plusieurs blueprints. Chaque blueprint correspond à une route principale à laquelle sont associées de nombreuses sous-routes. L'ensemble de nos fonctions se situent dans le controller associé au blueprint. Nos modèles sont définis à l'aide d'une ORM présentée ci-dessous. L'ensemble des "views" associés à nos routes se trouvent dans un dossier template et s'appuient sur Bootstrap.


## Choix de SQL Alchemy

SQL Alchemy est un outil de mapping objet-relationnel très utilisé par la communauté des développeurs Python.

![SQL Alchemy logo](/dev_log/static/logo_sqlalchemy.jpg)
#### L'avantage des ORM
Le technique de mapping relationnel (ou object relationnal mapping - ORM) est une technique de programmation informatique qui crée l'illusion d'une base de données orientée objet à partir d'une base de données relationnelle en définissant des correspondances entre cette base de données et les objets du langage utilisé. Les ORM permettent une manipulation bien plus simple des données. L'écriture des requêtes et l'ensemble des opérations sur les bases de données (sélection, jointure, projection) sont extrêmement simplifiées. Enfin, les ORM permmettent de mieux organiser son code dans l'esprit MVC (model view controller).
#### Notre organisation
Nous avons décidé de séparer notre modèle en plusieurs classes : cabinet, infirmiers, patients, rendez-vous, soins, rendez-vous planifiés. Les classes sont reliées entre elles par des "foreign keys" et des "relationships" afin de pouvoir effectuer des jointures de façon très simple.

