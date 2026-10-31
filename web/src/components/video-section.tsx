import { cn } from "@/lib/cn";

type VideoVersion = {
  id: string;
  src: string;
  poster: string;
  captions: string;
  descriptions: string;
  width: number;
  height: number;
  duration: string;
  label: string;
  summary: string;
  transcript: readonly string[];
  className: string;
  frameClassName: string;
};

const SUMMARY =
  "Sans voix, avec une musique originale. La vidéo explique le problème d'un assistant qui répond de mémoire, montre un exemple de réponse sur un vrai vote du 29 octobre 2026 avec sa source, puis les trois étapes pour ajouter le connecteur.";

const TRANSCRIPT = [
  "Qui a voté quoi ? Les votes des députés, dans votre assistant IA.",
  "Seul, un assistant IA répond de mémoire. Il peut se tromper sur un vote, et ne donne pas de lien pour vérifier.",
  "Avec ce connecteur gratuit, il va chercher les vrais votes de l'Assemblée nationale. Pour Claude et ChatGPT.",
  "Exemple : « Comment l'Assemblée a voté sur les accompagnants d'élèves en situation de handicap ? » Le texte a été adopté le 29 octobre 2026 (scrutin n° 9203) : 166 pour, 16 contre, 123 abstentions. Source : assemblee-nationale.fr. Il va chercher le vrai vote, et donne le lien pour vérifier.",
  "Comment l'ajouter : 1. Copiez l'adresse. 2. Collez l'adresse dans les réglages de Claude, ou de ChatGPT en formule payante. 3. Activez le connecteur, puis posez votre question en français.",
  "Gratuit. Sans inscription. Chaque réponse avec sa source. Aucun classement de députés, aucun commentaire politique.",
  "MCP Assemblée nationale. Projet indépendant et non officiel.",
] as const;

const VERSIONS: readonly VideoVersion[] = [
  {
    id: "video-paysage",
    src: "/video/presentation.mp4",
    poster: "/video/presentation.jpg",
    captions: "/video/presentation.fr.vtt",
    descriptions: "/video/presentation.descriptions.fr.vtt",
    width: 1920,
    height: 1080,
    duration: "57 secondes",
    label: "Présentation du connecteur MCP Assemblée nationale, 57 secondes",
    summary: SUMMARY,
    transcript: TRANSCRIPT,
    className: "hidden md:grid",
    frameClassName: "aspect-video",
  },
  {
    id: "video-portrait",
    src: "/video/presentation-verticale.mp4",
    poster: "/video/presentation-verticale.jpg",
    captions: "/video/presentation-verticale.fr.vtt",
    descriptions: "/video/presentation-verticale.descriptions.fr.vtt",
    width: 1080,
    height: 1920,
    duration: "57 secondes",
    label: "Présentation du connecteur MCP Assemblée nationale, 57 secondes, format vertical",
    summary: SUMMARY,
    transcript: TRANSCRIPT,
    className: "grid md:hidden",
    frameClassName: "mx-auto aspect-[9/16] w-full max-w-sm",
  },
];

const Player: React.FC<{ version: VideoVersion }> = ({ version }) => {
  const summaryId = `${version.id}-resume`;
  return (
    <div className={cn("gap-8 lg:grid-cols-12 lg:items-start lg:gap-12", version.className)}>
      <div className="lg:order-2 lg:col-span-8">
        <div className={cn("overflow-hidden border border-rule bg-surface", version.frameClassName)}>
          <video
            controls
            preload="none"
            playsInline
            poster={version.poster}
            width={version.width}
            height={version.height}
            aria-label={version.label}
            aria-describedby={summaryId}
            className="block size-full bg-surface object-contain"
          >
            <source src={version.src} type="video/mp4" />
            <track kind="captions" src={version.captions} srcLang="fr" label="Français" />
            <track kind="descriptions" src={version.descriptions} srcLang="fr" label="Description" />
            <a href={version.src}>Télécharger la vidéo ({version.duration})</a>
          </video>
        </div>
      </div>
      <div className="flex flex-col gap-4 lg:order-1 lg:col-span-4">
        <p id={summaryId} className="text-base text-ink-soft">
          {version.summary}
        </p>
        <div className="flex flex-col gap-2 border-t border-line pt-3">
          <h3 className="font-display text-base font-semibold">Le texte de la vidéo</h3>
          <ol className="flex list-decimal flex-col gap-2 pl-5 text-sm text-ink-soft">
            {version.transcript.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ol>
        </div>
        <p className="text-sm text-muted">
          {version.duration}. Vote réel lu le 31 octobre 2026 ; la conversation est un exemple. Musique originale composée pour la vidéo.
        </p>
      </div>
    </div>
  );
};

export const VideoSection: React.FC = () => {
  return (
    <section id="video" aria-labelledby="video-titre" className="border-t-2 border-rule py-14 sm:py-20">
      <div className="mx-auto flex w-full max-w-page flex-col gap-8 px-4 sm:px-6">
        <h2 id="video-titre" className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
          Le connecteur en vidéo
        </h2>
        <p className="max-w-measure text-base text-ink-soft">
          Chaque écran reste affiché le temps de le lire. Tout le texte de la vidéo est aussi écrit à côté.
        </p>
        {VERSIONS.map((version) => (
          <Player key={version.id} version={version} />
        ))}
      </div>
    </section>
  );
};
