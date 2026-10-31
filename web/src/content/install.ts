import { GITHUB_URL, MCP_URL } from "@/lib/config";

export type AssistantId = "claude" | "chatgpt" | "gemini" | "local";

export type CodeSample = { label: string; code: string };

export type AssistantGuide = {
  id: AssistantId;
  name: string;
  availability: string;
  steps: readonly string[];
  note: string;
  sample?: CodeSample;
};

const GEMINI_CONFIG = JSON.stringify(
  { mcpServers: { "assemblee-nationale": { httpUrl: MCP_URL } } },
  null,
  2,
);

const LOCAL_CONFIG = JSON.stringify(
  {
    mcpServers: {
      "assemblee-nationale": {
        command: "uvx",
        args: ["--from", `git+${GITHUB_URL}`, "mcp-assemblee-nationale"],
      },
    },
  },
  null,
  2,
);

export const ASSISTANTS: readonly AssistantGuide[] = [
  {
    id: "claude",
    name: "Claude",
    availability: "Plan gratuit inclus, sur claude.ai et l'application",
    steps: [
      "Ouvrez claude.ai, puis Paramètres, puis Connecteurs.",
      "Cliquez sur « Ajouter un connecteur personnalisé ».",
      "Nom : Assemblée nationale. Dans le champ « URL », collez l'adresse copiée plus haut.",
      "Cliquez sur « Ajouter ». Aucune connexion n'est demandée.",
      "Dans une nouvelle conversation, ouvrez le bouton + et vérifiez que le connecteur est activé.",
    ],
    note: "Le plan gratuit autorise un connecteur personnalisé, les plans payants en autorisent plusieurs. Sur un compte d'équipe, c'est l'administrateur qui l'ajoute.",
  },
  {
    id: "chatgpt",
    name: "ChatGPT",
    availability: "Plans payants, depuis le navigateur sur chatgpt.com",
    steps: [
      "Dans Paramètres, ouvrez « Applications et connecteurs », puis « Paramètres avancés », et activez le « Mode développeur ». Le nom fait peur, mais c'est simplement l'option qui permet d'ajouter un connecteur.",
      "Revenez dans Applications et connecteurs et cliquez sur Créer.",
      "Nom : Assemblée nationale. Dans le champ « URL du serveur MCP », collez l'adresse. Authentification : Aucune.",
      "Cochez la case de confiance, puis validez.",
      "Dans une conversation, cliquez sur + puis Mode développeur, et activez Assemblée nationale.",
    ],
    note: "ChatGPT indique « non vérifié » pour toute application ajoutée par vos soins. C'est normal : ce connecteur ne fait que lire des données publiques.",
  },
  {
    id: "gemini",
    name: "Gemini",
    availability: "Pour utilisateurs avancés : Gemini CLI uniquement, dans un terminal",
    steps: [
      "Ouvrez le fichier ~/.gemini/settings.json.",
      "Ajoutez le bloc suivant, qui contient l'adresse du connecteur.",
      "Redémarrez Gemini CLI, puis tapez /mcp pour vérifier que le connecteur est listé.",
    ],
    note: "L'application Gemini grand public ne permet pas d'ajouter son propre connecteur, à notre connaissance. La même adresse fonctionnera dès que ce sera possible.",
    sample: { label: "Configuration Gemini CLI", code: GEMINI_CONFIG },
  },
  {
    id: "local",
    name: "En local",
    availability: "Pour développeurs : Claude Desktop, Cursor et autres, sur votre ordinateur",
    steps: [
      "Installez uv, puis redémarrez votre application pour qu'elle retrouve la commande uvx.",
      "Ajoutez le bloc suivant dans la configuration MCP de l'application.",
      "Redémarrez l'application. Le serveur tourne alors sur votre ordinateur.",
    ],
    note: "La méthode recommandée reste l'adresse du connecteur : Claude Desktop reprend vos connecteurs claude.ai.",
    sample: { label: "Configuration locale (uvx)", code: LOCAL_CONFIG },
  },
];
