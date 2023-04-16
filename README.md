### Application de recommandation de films

#### Description

L'application contient une page principale proposant des films issues de dbpedia.org. 
La recommandation des films se basent sur :
- Les genres de films sélectionnés par l'utilisateur
- Les films likés par l'utilisateur 

Les deux autres pages ont pour fonctions de gérer la sélection des genres et des films likés.

#### Technologies

Repose sur le langage python et les librairies/frameworks :
- Flask pour la gestion des requêtes HTTP
- Jinja2 pour le rendu des templates
- rdflib pour la gestion et les requêtes des base de données graphes (local et dbpedia.org)