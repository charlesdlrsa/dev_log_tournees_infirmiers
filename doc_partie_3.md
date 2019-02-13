
# 2. Vue d'ensemble de l'architecture

## Architecture global

Nous avons décidé d'uiliser l'architecture suivante pour notre projet :
- Bootstrap pour le Front
- Flask pour le back et le serveur
- SQL Alchemy pour les bases de données

## Choix du framework Flask

Flask est un microcontroller pour développement Web qui présente de nombreux avantages pour effectuer un projet de développement de logiciel.
### Minimaliste et simpliste
Flask est très petit. C'est un framework qui n'installe que très peu d'éléments (environ 2000 lignes de codes) et qui s'apprend très rapidement. A l'inverse de Django, la courbe d'apprentissage pour entamer une application est très courte. Il n'y a pas de restrictions et on a une liberté totale d'implémenter ce que l'on veut comme on le veut.
### Flexible et étendable
Le framework est très flexible et très bien conçu. Même si Flask reste un micro framework et donc ne peut pas tout faire, il est très étendable et on peut ajouter les fonctionnalités désirées assez facilement. La structure de l'application dépend vraiment de ses choix, il y a uniquement quelques spécifications prédéfinies mais il est facile de les détourner si l'on veut.
### Système de routage et Blueprints
Le système de routage (dit "routing") est très intuitif sur Flask avec l'utilisation de décorateurs pour définir certaines routes. Les "Blueprints" sont comme des modules pour l'application. Nous avons décidé de séparer notre code en plusieurs blueprints, chacun associé à un controller.
### Serveur web et deboogage
Il est possible d'exécuter le serveur web intégré à Flask et de voir son application fonctionner sans encombres. De surcroît, Flask est livré avec avec un débogueur intégré au navigateur qui est très utile lorsque l'on développe.

