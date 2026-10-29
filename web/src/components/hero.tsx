import { CtaLink } from "./cta-link";
import { ChatExample } from "./chat-example";
import { formatDay, formatNumber } from "@/lib/format";
import type { HeroChat, HeroCounters } from "@/lib/data/view-types";

type HeroProps = { counters: HeroCounters; chat: HeroChat | null; generatedAt: Date };

const ProofLine: React.FC<{ counters: HeroCounters }> = ({ counters }) => {
  const { scrutins, legislature, latestDate } = counters;
  if (scrutins === null || latestDate === null) {
    return <p className="text-sm text-muted">Chiffres en direct momentanément indisponibles.</p>;
  }
  return (
    <p className="text-sm text-muted">
      <span className="tabular font-mono font-semibold text-ink">{formatNumber(scrutins)}</span> scrutins sous la{" "}
      {legislature ?? 17}e législature, dernier vote le{" "}
      <time dateTime={latestDate} className="font-semibold text-ink">
        {formatDay(latestDate)}
      </time>
      .
    </p>
  );
};

export const Hero: React.FC<HeroProps> = ({ counters, chat, generatedAt }) => {
  return (
    <section aria-labelledby="titre-principal" className="pb-16 pt-24 sm:pb-24 sm:pt-24">
      <div className="mx-auto grid w-full max-w-page items-center gap-12 px-4 sm:px-6 lg:grid-cols-2">
        <div className="flex flex-col gap-6">
          <h1 id="titre-principal" className="hero-title max-w-hero text-5xl font-semibold tracking-tight sm:text-6xl">
            Sachez comment ont voté
            <br className="hidden sm:block" /> vos députés, source à l'appui
          </h1>
          <p className="max-w-hero text-lg text-muted">
            Ajoutez un connecteur gratuit à votre assistant IA. Il va chercher les vrais scrutins de l'Assemblée
            nationale au lieu de répondre de mémoire, et il cite le lien de chacun.
          </p>
          <div className="flex flex-col items-start gap-3">
            <CtaLink />
            <p className="text-sm text-muted">Gratuit, sans compte, sans clé. Pour Claude et ChatGPT.</p>
          </div>
          <ProofLine counters={counters} />
        </div>
        <ChatExample chat={chat} generatedAt={generatedAt} />
      </div>
    </section>
  );
};
