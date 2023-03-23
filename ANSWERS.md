# TP 1 Chat scurisé
### Prise en main

1. Comment s'appelle cette topologie ?

Il s'agit d'une topologie en étoile. Chaque utilisateur est relié à un serveur et la communication est relayée par ce serveur.

2. Que remarquez-vous dans les log ?

Les messages apparaissent en clair en dehors de l'interface du chat.

3. Pourquoi est-ce un problème et quel principe cela viole-t-il ?

Chaque personne connectée au serveur, appartenant à la conversation a accès aux messages en clair.
Cela viole la règle de la confidentialité.

4. Quelle solution la plus simple pouvez-vous mettre en place pour éviter cela ? Détaillez votre
réponse.

Il faut chiffrer la communication pour la rendre confidentielle pour les interlocuteurs.========================

### Chiffrement

1. Est-ce que urandom est un bon choix pour de la cryptographie ? Pourquoi ?
Tout d'abord, il faut noter que urandom est un choix plus adapté que np.random, qui repose sur une génération déterministe ce qui limite son usage à un cadre mathématique/ de simulation. urandom génère son rendu grâce à l'entropy (lorsque celui est suffisamment important) directement lié par le système, relevant des interruptions que l'on lui applique (timing touches clavier, etc.). Toutefois ces interruptions dépendant de la fréquence de l'horloge du système (valeurs discrètes), cela limite les valeurs possibles, bien qu'extrêmement larges. Pour un usage cryptographique moins 'banal', d'autres moyen de générer du 'pseudo' aléatoire son envisageable, en changeant de mode opératoire à chaque génération par exemple (photographie de lampes à magma (apériodique), entropie du bruit thermique lié à d'autres phénomènes (dont interruption par exmeple), etc.).

2. Pourquoi utiliser ses primitives cryptographiques peut être dangereux ?
==========================
3. Pourquoi malgré le chiffrement un serveur malveillant, peut-il encore nous nuire ?
En partant du principe que le message est indéchiffrable, il est possible de surcharger de requêtes, de récupérer des informations annexes aux utilisateurs du chat, etc.
De plus, nous avons implanté un chiffrement, mais rien n'empêche pour l'instant de le modifier en cours de route, faussant l'intégrité de la communication.

4. Quelle propriété manque-t-il ici ?
Il manque ainsi la propriété de l'intégrité selon laquelle chaque information devrait être certifiée non altérée ou par des membres authorisés, le tout selon des normes strictes.

### Authenticated Symetric Encryption

1. Pourquoi Fernet est moins risqué que le précédent chapitre en terme d'implémentation ?

2. Un serveur malveillant peut néanmoins attaquer avec de faux messages, déjà utilisés dans le passée.Comment appelle-t-on cette attaque ?

3. Quelle méthode permet de s'en affranchir ?

### TTL

1. Remarquez-vous une différence avec le chapitre précédent ?

2. Maintenant, soustrayez 45 au temps lors de l'émission. Que se passe-t-il et pourquoi ?

3. Est-ce efficace pour se protéger de l'attaque du précédent chapitre ?

4. Quelle(s) limite(s) cette solution peut-elle rencontrer dans la pratique ?

### Regard critique (inconvénients-alternatives)
