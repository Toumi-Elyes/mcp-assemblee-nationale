# Politique de sécurité

## Signaler une vulnérabilité

Merci de **ne pas ouvrir d'issue publique** pour une faille de sécurité.

Utilisez le signalement privé de GitHub :

1. Ouvrez l'onglet **Security** du dépôt [Toumi-Elyes/mcp-assemblee-nationale](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/security).
2. Cliquez sur **Report a vulnerability** (Security Advisories).
3. Décrivez le problème, comment le reproduire et son impact potentiel.

Vous recevrez une réponse dès que possible. Une correction est publiée sur `main`, puis le signalement est rendu public avec votre accord.

## Version prise en charge

Seule la branche `main` (et donc le serveur public déployé depuis elle) est prise en charge. Il n'y a pas de correctifs pour les anciennes versions.

## Périmètre

**Concerné**

- le code du serveur MCP (`src/assemblee_mcp/`, `api/`) ;
- la configuration de déploiement (`vercel.json`) ;
- la page de démonstration (`web/`) ;
- les risques propres à un serveur MCP : injection de consignes par du texte tiers, liens non sûrs repris dans les réponses, appels excessifs vers CIVIX.

**Hors périmètre**

- l'API CIVIX et les données de l'Assemblée nationale : signalez-le à [CIVIX](https://www.civix.fr) ou à l'Assemblée nationale ;
- les assistants (Claude, ChatGPT, Gemini) et la plateforme d'hébergement ;
- les erreurs de données ou les bugs sans impact de sécurité : ouvrez une [issue](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/issues) ;
- les tests de charge ou d'attaque par déni de service sur le serveur public.

## Mesures en place

- Budget d'appels vers CIVIX par appel d'outil.
- Limitation de débit sur le pare-feu de l'hébergeur.
- Texte tiers cité et signalé comme tel.
- Liens repris uniquement vers une liste de sites autorisés, en https.
- Serveur en lecture seule, sans compte, sans cookie, sans secret côté utilisateur.
