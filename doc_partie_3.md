
# 2. Vue d'ensemble de l'architecture

## Architecture global

Nous avons décidé d'uiliser l'architecture suivante pour notre projet :
- Flask pour le back et le serveur
- SQL Alchemy pour les bases de données
- Bootstrap pour le Front

## Choix du framework Flask

Flask est un microcontroller pour développement Web qui présente de nombreux avantages pour effectuer un projet de développement de logiciel.
![Flask logo](/dev_log/static/logo_flask.png=250x "flask logo")
#### Minimaliste et simpliste
Flask est très petit. C'est un framework qui n'installe que très peu d'éléments (environ 2000 lignes de codes) et qui s'apprend très rapidement. A l'inverse de Django, la courbe d'apprentissage pour entamer une application est très courte. Il n'y a pas de restrictions et on a une liberté totale d'implémenter ce que l'on veut comme on le veut.
#### Flexible et étendable
Le framework est très flexible et très bien conçu. Même si Flask reste un micro framework et donc ne peut pas tout faire, il est très étendable et on peut ajouter les fonctionnalités désirées assez facilement. La structure de l'application dépend vraiment de ses choix, il y a uniquement quelques spécifications prédéfinies mais il est facile de les détourner si l'on veut.
#### Système de routage et Blueprints
Le système de routage (dit "routing") est très intuitif sur Flask avec l'utilisation de décorateurs pour définir certaines routes. Les "Blueprints" sont comme des modules pour l'application.
#### Serveur web et debogage
Il est possible d'exécuter le serveur web intégré à Flask et de voir son application fonctionner sans encombres. De surcroît, Flask est livré avec avec un débogueur intégré au navigateur qui est très utile lorsque l'on développe.
#### Notre organisation 
Notre back est organisé sur le principe du MVC : model-view-controller.
Nous avons décidé de séparer notre applications en plusieurs blueprints. Chaque blueprint correspond à une route principale, auxquelles est associée de nombreuses sous routes. L'ensemble de nos fonctions se situent dans le controller associé au blueprint. Nos modèles sont définis à l'aide d'un ORM présenté ci-dessous. L'ensemble des "views" associés à nos routes se trouvent dans un dossier template où la plupart des templates s'appuient sur Bootstrap.

----------------------------------------------------------------------------------------------------------------------------------------

## Choix de SQL Alchemy

SQL Alchemy est un outil de mapping objet-relationnel très utilisé par la communauté des développeurs Python.
#### L'avantage des ORM
Le technique de mapping relationnel (ou object relationnal mapping - ORM) est une technique de programmation informatique qui crée l'illusion d'une base de données orientée objet à partir d'une base de données relationnelle en définissant des correspondances entre cette base de données et les objets du langage utilisé. Les ORM permettent une manipulation bien plus simple des données. L'écriture des requêtes et l'ensemble des opérations sur les bases de données (sélection, jointure, projection) sont extrêmement simplifiées. Enfin, les ORM permmettent de mieux organiser son code dans l'esprit MVC (model view controller).
#### Notre organisation

