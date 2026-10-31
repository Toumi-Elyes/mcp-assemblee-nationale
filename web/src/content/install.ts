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
    availability: "Toutes les formules, y compris la gratuite, sur claude.ai et dans l'application",
    steps: [
      "Sur claude.ai, ouvrez « Customize » (Personnaliser), puis « Connectors » (Connecteurs).",
      "Cliquez sur « + Add », puis sur « Add custom connector » (ajouter un connecteur personnalisé).",
      "Nom : Assemblée nationale. Collez l'adresse copiée plus haut, puis cliquez sur « Continue » deux fois.",
      "Pour la connexion, choisissez « No sign in » (aucune connexion), puis cliquez sur « Add ».",
      "Dans une conversation, cliquez sur le bouton + en bas à gauche, puis « Connectors », et activez Assemblée nationale.",
    ],
    note: "La formule gratuite autorise un connecteur personnalisé, les formules payantes en autorisent plusieurs. Sur un compte d'équipe, c'est un propriétaire du compte qui l'ajoute. Les menus peuvent s'afficher en français ou en anglais selon votre langue.",
  },
  {
    id: "chatgpt",
    name: "ChatGPT",
    availability: "Formules Pro, Business et Enterprise, sur le site chatgpt.com (pas dans l'application mobile). Pas avec les formules gratuite et Plus.",
    steps: [
      "Sur chatgpt.com, ouvrez « Plugins ».",
      "Cliquez sur le bouton +, puis sur « Add custom MCP server ». C'est le nom technique d'un connecteur.",
      "Nom : Assemblée nationale. Sous « Connection », collez l'adresse copiée plus haut. Authentification : aucune.",
      "Cochez « I understand and want to continue », puis cliquez sur « Create as a plugin ».",
      "Dans une nouvelle conversation, tapez @ dans la zone de saisie et choisissez Assemblée nationale.",
    ],
    note: "Sur une formule Business, seul un administrateur peut ajouter un connecteur. ChatGPT affiche un avertissement pour tout connecteur ajouté par vos soins : c'est normal, ce connecteur ne fait que lire des données publiques. Étapes vérifiées sur l'aide d'OpenAI en octobre 2026 ; les menus changent souvent.",
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
