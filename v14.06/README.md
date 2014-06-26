Mise à jour du modèle de données (Juin 2014)
============================================

Le modèle de données existant sera simplifié, en passant de 14 à 3 modèles. Les 3 modèles qui seront proposés

# Le modèle Service d'information

* Les champs de l'actuel modèle Service d'information
* Ceux provenant de l'opérateur du SI : Nom, URL Opérateur
* Les champs des sous-fiches s'y rattachant
* Site web
* Application mobile
* Centre d'appel
* Service web
* Open data
* Comarquage

Ces champs seraient préfixés par le nom de sous-fiche afin d'organiser la fiche du service d'information selon des
«paragraphes»

# Le modèle Offre de transport

* Les champs de l'actuel modèle Offre de transport
* Un champ Exploitant
* Un champ URL Exploitant
* Un champ Autorité
* Un champ URL Autorité

# Les modèles "Guichet d'information" et "Calcul d'itinéraire"

Seront archivés dans un fichier CSV puis supprimés dans un 2ème temps

# Fonctionnement des scripts

Le premier script lancé unifie tout les POIs en utilisant les champs de type "link"
Le deuxième script s'occupe de réordonner ces champs et de réparé les quelques metadata que nous auriont perdu lors de
la migration

Un troisième script est lancé afin de réindéxer entiérement la base de données et ainsi conseré les performances et la
précisions des moteur de recherche
