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

const MUSIC_CREDIT = "Musique : Sascha Ende, ende.app (CC BY 4.0), extrait mis en boucle";

const VERSIONS: readonly VideoVersion[] = [
  {
    id: "video-paysage",
    src: "/video/presentation.mp4",
    poster: "/video/presentation.jpg",
    captions: "/video/presentation.fr.vtt",
    descriptions: "/video/presentation.descriptions.fr.vtt",
    width: 1920,
    height: 1080,
    duration: "50 secondes",
    label: "Présentation du connecteur MCP Assemblée nationale, 50 secondes",
    summary:
      "Sans voix, avec une musique. On y voit le nombre de votes enregistrés depuis 2024, les votes de la semaine, un exemple de réponse d'un assistant sur un vote du 29 octobre 2026, puis l'adresse à copier.",
    transcript: [
      "8 741 scrutins enregistrés sous la 17e législature.",
      "Demandez à Claude, ChatGPT ou Gemini comment ont voté les députés.",
      "Un connecteur gratuit : votre assistant lit les vrais scrutins et donne le lien.",
      "Cette semaine à l'Assemblée : 15 scrutins.",
      "Exemple : le texte a été adopté le 29 octobre 2026 (scrutin n° 9203), 166 pour, 16 contre, 123 abstentions. Sources : assemblee-nationale.fr, civix.fr.",
      "Gratuit. Sans compte. Sans clé. Copier l'adresse.",
      "25 outils en lecture seule, chaque réponse sourcée.",
      "MCP Assemblée nationale, projet indépendant et non officiel.",
    ],
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
    duration: "47 secondes",
    label: "Présentation du connecteur MCP Assemblée nationale, 47 secondes, format vertical",
    summary:
      "Sans voix, avec une musique. On y voit la question « Qui a voté quoi ? », les votes de la semaine, un exemple de réponse d'un assistant sur un vote du 29 octobre 2026, puis l'adresse à copier.",
    transcript: [
      "Qui a voté quoi ?",
      "Les votes des députés à l'Assemblée nationale, scrutin par scrutin.",
      "Cette semaine à l'Assemblée : 15 scrutins.",
      "Exemple : le texte a été adopté le 29 octobre 2026 (scrutin n° 9203), 166 pour, 16 contre, 123 abstentions, sources citées.",
      "Les données brutes, source à l'appui. Comprenez. Vérifiez. Faites-vous votre propre avis.",
      "Gratuit. Sans compte. Sans clé. Copier l'adresse, puis la coller dans Claude, ChatGPT ou Gemini.",
      "MCP Assemblée nationale. Vérifiez par vous-même.",
    ],
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
          {version.duration}. Données réelles lues le 30 octobre 2026 ; la réponse d'assistant est un exemple. {MUSIC_CREDIT}.
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
