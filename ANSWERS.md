# TP 1 Chat scurisé
### Prise en main

1. Comment s'appelle cette topologie ?

Il s'agit d'une topologie en étoile. Chaque utilisateur est relié à un client et la communication est relayée par un serveur central. Cela permet à de nombreux utilisateurs de communiquer avec un serveur unique (+ simple). Attention à la surcharge de requêtes qui peut entrainer sa fermeture. Une erreur tierce du serveur entraine la fermeture de la communication, mais une erreur client ne gène pas les autres utilisateurs (sauf celui qui ne verra pas de réponse à son dernier message, son interlocuteur ayant mometanément disparu...).

2. Que remarquez-vous dans les log ?

Les messages apparaissent en clair en dehors de l'interface du chat. 

3. Pourquoi est-ce un problème et quel principe cela viole-t-il ?

Chaque personne connectée au client, appartenant à la conversation a accès aux messages en clair.
Cela viole la règle de la confidentialité.

4. Quelle solution la plus simple pouvez-vous mettre en place pour éviter cela ? Détaillez votre
réponse.

Il faut chiffrer la communication pour la rendre confidentielle pour les interlocuteurs.C'est-à-dire "codifier" le message selon un algorithme de chiffrement impossible à "retro-engineerer" mathématiquement, afin d'éviter de voir sa conversation écoutée.

### Chiffrement

1. Est-ce que urandom est un bon choix pour de la cryptographie ? Pourquoi ?

Tout d'abord, il faut noter que urandom est un choix plus adapté que np.random, qui repose sur une génération déterministe ce qui limite son usage à un cadre mathématique/ de simulation. urandom génère son rendu grâce à l'entropy (lorsque celui est suffisamment important) directement lié par le système, relevant des interruptions que l'on lui applique (timing touches clavier, etc.). Toutefois ces interruptions dépendant de la fréquence de l'horloge du système (valeurs discrètes), cela limite les valeurs possibles, bien qu'extrêmement larges. Pour un usage cryptographique moins 'banal', d'autres moyen de générer du 'pseudo' aléatoire son envisageable, en changeant de mode opératoire à chaque génération par exemple (photographie de lampes à magma (apériodique), entropie du bruit thermique lié à d'autres phénomènes (dont interruption par exmeple), etc.).

2. Pourquoi utiliser ses primitives cryptographiques peut être dangereux ?

En utilisant ces primitives cryptographiques, tous les systèmes de sécurité basés là-dessus s'écroulent. Il faut être alerte sur la veille technologique, mais aussi sur son utilisation dans le monde. Une primitve répandue mondialement est certes robuste car gage de qualité, mais cela veut également dire que force personnes tentent de la faire tomber. 
Concevoir ses propres primitives "exotiques" peut être une bonne idée de manière à ce que l'ennemi ne sache pas quoi faire contre une méthode inconnue, mais cela veut aussi dire que cette méthode n'a pas beaucoup d'expérience et manque de robusstesse car elle n'a pas été améliorée au fil des attaques.

3. Pourquoi malgré le chiffrement un serveur malveillant, peut-il encore nous nuire ?

En partant du principe que le message est indéchiffrable, il est possible de surcharger de requêtes, de récupérer des informations annexes aux utilisateurs du chat, etc.
De plus, nous avons implanté un chiffrement, mais rien n'empêche pour l'instant de le modifier en cours de route, faussant l'intégrité de la communication.

4. Quelle propriété manque-t-il ici ?

Il manque ainsi la propriété de l'intégrité selon laquelle chaque information devrait être certifiée non altérée ou par des membres authorisés, le tout selon des normes strictes.

### Authenticated Symetric Encryption

1. Pourquoi Fernet est moins risqué que le précédent chapitre en terme d'implémentation ?

Cela est moins risqué car le module fernet vérifie la bonne intégrité du message au moment de la réception via un token comportant sa version, un "timestamp", son propre initialization vector "signé" via HMAC.
En cas d'altération du message, le token devient invalide, alertant le problème.

2. Un serveur malveillant peut néanmoins attaquer avec de faux messages, déjà utilisés dans le passée.Comment appelle-t-on cette attaque ?

En volant le mot de passe
3. Quelle méthode permet de s'en affranchir ?

En ajoutant une durée de vie au message, cela réduit la fenêtre d'attaque car ce dernier sera ignoré, lorsque "périmé".

### TTL

1. Remarquez-vous une différence avec le chapitre précédent ?

Non, les paramètres (taille, temps d'execution, etc.) apparaissent identiques.

2. Maintenant, soustrayez 45 au temps lors de l'émission. Que se passe-t-il et pourquoi ?

30-45 <0. Les messages sont invalides d'entrée de jeu et les messages sont ignorés.

3. Est-ce efficace pour se protéger de l'attaque du précédent chapitre ?

Cela réduit la fenêtre de tir de l'ennemi, ne pouvant usurper l'utilisateur que dans un temps imparti contre une durée illimitée avant. Le principe disponibilité est respecté.

4. Quelle(s) limite(s) cette solution peut-elle rencontrer dans la pratique ?

Cas illustratifs : 
- La communication basse fréquence permet de communiquer sur de longues distances notamment par la marine en océan. Toutefois, celle-ci est lente (de l'ordre des minutes). Le timestamp doit ainsi être élevé, augmentant la fenêtre d'attaque des ennemis.
- Pour des fichiers volumineux, un mauvais timestamp incapaciterait toute transmission.
- Le timestamp doit être le plus petit possible sans incapaciter la communication, ce qui peut amener à des compromis peu arrangeant.

### Regard critique (inconvénients-alternatives)

Les trois principes de Kerckhoffs sont respectés. C'est un bon début, à présent, il faudrait mettre en place un système de traçabilité et d'authentification plus profond au chat afin de laisser le moins de portes ouvertes aux attaques.

Concernant la traçabilité, une classification bien plus soignée des logs permettrait d'améliorer ce point en repertioriant non seulement les erreurs mais aussi tout autre type d'information (date, IP, contenu, etc.) Toutefois, cela engendre des inconvénients comme de plus lourdes données à grande échelle, l'identification possible des utilisateurs du chat par l'ennemi, etc. Cela pourrait également poser des questions d'étique sur l'espionnage des conversations de l'utilisateurs.
Se tourner vers les métadonnées permettrait une meilleure confidentialité, bien que même si en place pour les GAFAM par exemple, son usage laisse nombre de profilages.

Une autre faille pourrait être celle des mots de passes qui pourraient être plus sécurisés.
Une idée de randomiser le mot de passe à chaque conversation pourrait empêcher un ennemi de le récupérer depuis l'interception des communications, laclef étant dérivé du mot de passe.

Le chat est hébergé localement, pour les raisons de l'exercice, toutefois le serveur doit être tout autant sécurisé contre les surcharges de requêtes, utilisateurs trop curieux/malveillants avec des restrictions administratrices très fortes, et une protection de flux transitant robuste car c'est ici que chaque message passe