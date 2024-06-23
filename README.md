# Projet SMA

Projet permettant de simuler le comportement d'un groupe de personnes lors d'un évènement festif de type concert ou festival. La salle dispose de 3 toilettes disposés aux extrémités de la salle ( représentés par des carrés bleus ). Les bars eux, sont représentés par des carrés verts et sont disposés de manière aléatoire afin de pouvoir après plusieurs exécutions, déterminer quel serait le meilleur placement et la quantité nécessaire pour un déroulement fluide.
3 types d'agents sont utilisés : les agents représentant le public, les barmans et un manager qui déploie les barmans la ou la demande est la plus affluente.


## Dépendances requises

Les dépendances requises pour lancer le projet sont les suivantes :

 - pygame
 - faker

## Installation

 1. Disposer d'une version de Python > 3.6
 2. Cloner ce dépôt en utilisant :
  ```bash
git clone https://github.com/AlexandreFyl/SMA.git
```
 3. Executer la commande suivante pour installer les dépendances :
```bash
pip install pygame faker
```

## Utilisation

Pour lancer le projet, il suffit d'exécuter la commande suivante : 
```bash
py main.py
```

## Configuration

Le nombre de festivaliers est de barmans peut être défini à la ligne 61 du main.py via la fonction **populateAgents**. Tel que :
```python
listeners, bartenders  =  populateAgents(200, 4, scene, bars)
```
Le nombre de bars, lui, est determiné à la ligne 55 du main.py via la fonction place_bars, comme suit :
```python
bars  =  place_bars(3, scene, toilets)
```
De nouveaux toilettes peuvent également être ajoutés dans la liste dédiée présente à la ligne 47.
Nous trouvons aussi au début du fichier deux constantes correspondant à la taille de la fenêtre et au nombre de FPS.
