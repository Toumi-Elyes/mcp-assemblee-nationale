# Journal des modifications

Les nouveautés du connecteur MCP Assemblée nationale, de la plus récente à la plus ancienne.
Le même journal est publié sur la landing : https://landing-page-mcp-assemblee-national.vercel.app/nouveautes.

<!-- Fichier généré à partir de web/src/content/changelog.ts : modifier ce fichier, puis lancer `pnpm changelog` dans web/. -->

## 31 octobre 2026

- **Amélioré** · Les votes de la semaine en langage courant. Chaque vote dit ce qui a été voté (le texte entier, un article, une modification) et sur quel sujet, par exemple « Budget de l'État pour 2027 ». La vidéo de présentation, refaite, laisse le temps de lire chaque écran. Les étapes d'installation suivent l'aide officielle d'octobre 2026 : avec ChatGPT, il faut une formule Pro, Business ou Enterprise. ([#60](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/60))
- **Amélioré** · Une page d'accueil en langage simple. Le premier écran explique le service en trois étapes, avec un exemple de réponse. Une section « En clair » répond aux questions de base, avec un lexique et des questions à copier. ([#55](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/55))
- **Nouveau** · Trouver les députés de son département. « Qui est mon député ? » : la recherche de députés accepte un département, par exemple « Gironde », et liste ses députés par circonscription, de 2012 à aujourd'hui. Accents et fautes de frappe sont tolérés. ([#59](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/59))
- **Corrigé** · Un lien exact pour chaque vote cité. Les listes de votes donnent maintenant le lien de chaque scrutin vers le site de l'Assemblée nationale. L'assistant n'a plus à deviner une adresse, ce qui menait parfois à une page d'erreur. ([#57](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/57))

## 30 octobre 2026

- **Nouveau** · Comparer de 3 à 5 députés. Pour chaque paire de députés, la part de scrutins votés de la même façon, avec le nombre de scrutins comparés. ([#49](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/49))
- **Amélioré** · Les groupes analysés de 2012 à aujourd'hui. Positions, accords et cohésion des groupes pour chaque législature, de la 14e à la 17e. ([#47](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/47))
- **Amélioré** · La position des groupes dans le suivi d'un sujet. Le suivi d'un sujet montre comment chaque groupe a voté sur les derniers votes sur l'ensemble d'un texte. ([#48](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/48))
- **Amélioré** · Une recherche qui accepte le pluriel. « retraites » trouve aussi les scrutins dont le titre dit « retraite ». ([#50](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/50))
- **Nouveau** · Suivre un sujet d'une législature à l'autre. Pour un sujet, les scrutins de chaque législature depuis 2012 : nombre, résultats et derniers votes sur l'ensemble d'un texte. ([#41](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/41))
- **Nouveau** · Titres, résultats et votes par groupe de 2012 à 2022. Les scrutins des 14e et 15e législatures sont complétés par les archives de l'Assemblée nationale et se cherchent par sujet. ([#40](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/40))
- **Nouveau** · Les votes consultables depuis 2012. Les anciens députés et leurs votes sont retrouvés de la 14e à la 16e législature, en plus de la législature en cours. ([#35](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/35))
- **Amélioré** · Des réponses plus rapides. Les réponses déjà obtenues sont partagées entre les serveurs du connecteur. ([#34](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/34))
- **Nouveau** · Les dossiers législatifs dans ChatGPT. La recherche approfondie de ChatGPT trouve et ouvre les dossiers législatifs. ([#33](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/33))

## 29 octobre 2026

- **Corrigé** · Liens vers les scrutins de l'Assemblée. Chaque scrutin renvoie vers la bonne page du site de l'Assemblée nationale. ([#17](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/17))
- **Nouveau** · 13 outils d'analyse et d'export. Tendances, positions des groupes, bilan d'un député, comparaisons et exports CSV ou JSON, avec la méthode indiquée. ([#11](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/11))
- **Corrigé** · Audit de sécurité du connecteur. Plafond de requêtes par question, liens contrôlés et citations de tiers signalées. ([#7](https://github.com/Toumi-Elyes/mcp-assemblee-nationale/pull/7))
