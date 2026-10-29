import { MCP_URL } from "@/lib/config";
import { CopyButton } from "./copy-button";
import { Section } from "./section";

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
        args: [
          "--from",
          "git+https://github.com/Toumi-Elyes/mcp-assemblee-nationale",
          "mcp-assemblee-nationale",
        ],
      },
    },
  },
  null,
  2,
);

const Steps: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <ol className="mt-3 list-decimal space-y-1.5 pl-5 text-sm">{children}</ol>;
};

const CodeBlock: React.FC<{ code: string; label: string }> = ({ code, label }) => {
  return (
    <div className="mt-3">
      <pre className="card overflow-x-auto p-3 font-mono text-xs">
        <code>{code}</code>
      </pre>
      <CopyButton value={code} label={label} className="mt-2 px-3 py-1.5 text-sm" />
    </div>
  );
};

const Panel: React.FC<{ id: string; title: string; note: string; children: React.ReactNode }> = ({
  id,
  title,
  note,
  children,
}) => {
  return (
    <article id={id} className="card p-5">
      <h3 className="text-xl font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-muted">{note}</p>
      {children}
    </article>
  );
};

export const InstallSection: React.FC = () => {
  return (
    <Section
      id="installer"
      eyebrow="Installer"
      title="Prêt en 2 minutes, sans rien coder"
      intro="Une seule chose à copier : l'adresse du serveur. Les noms des menus changent parfois d'une version à l'autre."
    >
      <div className="card mb-6 flex flex-col gap-3 p-5 sm:flex-row sm:items-center">
        <code className="min-w-0 flex-1 break-all font-mono text-sm">{MCP_URL}</code>
        <CopyButton value={MCP_URL} label="Copier l'adresse" className="justify-center" />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel id="installer-claude" title="Claude" note="claude.ai et application Claude. Le plan gratuit autorise 1 connecteur personnalisé.">
          <Steps>
            <li>Ouvrez claude.ai, puis <strong>Paramètres → Connecteurs</strong>.</li>
            <li>Cliquez sur <strong>Ajouter un connecteur personnalisé</strong>.</li>
            <li>Nom : <code>Assemblée nationale</code>. URL : collez l&apos;adresse ci-dessus.</li>
            <li>Validez : aucune connexion n&apos;est demandée.</li>
            <li>Dans une conversation, activez le connecteur avec le bouton <strong>+</strong>.</li>
          </Steps>
        </Panel>

        <Panel id="installer-chatgpt" title="ChatGPT" note="Plans payants uniquement, depuis chatgpt.com dans le navigateur.">
          <Steps>
            <li>
              <strong>Paramètres → Applications et connecteurs → Paramètres avancés</strong> : activez le{" "}
              <strong>Mode développeur</strong>.
            </li>
            <li>Revenez dans Applications et connecteurs, puis <strong>Créer</strong>.</li>
            <li>Nom : <code>Assemblée nationale</code>. URL du serveur MCP : l&apos;adresse ci-dessus. Authentification : <strong>Aucune</strong>.</li>
            <li>Cochez la case de confiance et validez.</li>
            <li>Dans une conversation : <strong>+ → Mode développeur</strong>, puis activez le connecteur.</li>
          </Steps>
          <p className="mt-3 text-xs text-muted">
            ChatGPT affiche « non vérifié » pour toute application ajoutée soi-même : c&apos;est normal.
          </p>
        </Panel>

        <Panel
          id="installer-gemini"
          title="Gemini"
          note="À notre connaissance, l'application Gemini grand public ne permet pas d'ajouter son propre serveur MCP. Gemini CLI, si."
        >
          <p className="mt-3 text-sm">
            Dans Gemini CLI, ajoutez ceci à <code>~/.gemini/settings.json</code>, puis tapez <code>/mcp</code> pour vérifier.
          </p>
          <CodeBlock code={GEMINI_CONFIG} label="Copier la configuration" />
        </Panel>

        <Panel
          id="installer-local"
          title="En local (Claude Desktop, Cursor…)"
          note="Pour faire tourner le serveur sur votre ordinateur. Demande d'installer uv."
        >
          <p className="mt-3 text-sm">
            Installez{" "}
            <a className="link" href="https://docs.astral.sh/uv/getting-started/installation/">
              uv
            </a>
            , puis ajoutez ce bloc au fichier de configuration MCP de votre application.
          </p>
          <CodeBlock code={LOCAL_CONFIG} label="Copier la configuration" />
        </Panel>
      </div>

      <div className="card mt-6 p-5 text-sm">
        <h3 className="font-semibold">Si ça ne marche pas</h3>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-muted">
          <li>Le connecteur doit être activé dans la conversation en cours, pas seulement dans les réglages.</li>
          <li>Demandez explicitement : « Utilise l&apos;outil Assemblée nationale pour… ».</li>
          <li>L&apos;adresse doit se terminer par <code>/mcp</code>, sans espace ni guillemet.</li>
        </ul>
      </div>
    </Section>
  );
};
