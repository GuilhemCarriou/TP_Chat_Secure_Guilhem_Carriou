# TP 1 Chat scurisé
### Prise en main

1. Comment s'appelle cette topologie ?

Il s'agit d'une topologie en étole. Chaque utilisateur est relié à un serveur et la communication est relayée par ce serveur.

2. Que remarquez-vous dans les log ?

Les messages apparaissent en clair en dehors de l'interface du chat.

3. Pourquoi est-ce un problème et quel principe cela viole-t-il ?

Chaque personne connectée au serveur, appartenant à la conversation a accès aux messages en clair.
Cela viole la règle de la confidentialité.

4. Quelle solution la plus simple pouvez-vous mettre en place pour éviter cela ? Détaillez votre
réponse.

Il faut chiffrer la communication pour la rendre confidentielle pour les interlocuteurs.

### Chiffrement

