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
    <div className="flex flex-col gap-2">
      <p className="tabular text-6xl font-bold text-accent">{formatNumber(scrutins)}</p>
      <p className="max-w-hero text-sm text-muted">
        scrutins sous la {legislature ?? 17}e législature. Dernier vote le{" "}
        <time dateTime={latestDate} className="font-bold text-ink">
          {formatDay(latestDate)}
        </time>
        .
      </p>
    </div>
  );
};

export const Hero: React.FC<HeroProps> = ({ counters, chat, generatedAt }) => {
  return (
    <section aria-labelledby="titre-principal" className="bg-bg pb-16 pt-12 sm:pb-24 sm:pt-16">
      <div className="mx-auto grid w-full max-w-page items-start gap-12 px-4 sm:px-6 lg:grid-cols-12">
        <div className="flex flex-col gap-6 lg:col-span-7">
          <h1 id="titre-principal" className="max-w-hero font-serif text-5xl font-bold sm:text-6xl">
            <span className="block">Sachez comment ont voté vos députés,</span>
            <span className="block">source à l'appui</span>
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
        <div className="lg:col-span-5 lg:mt-24">
          <ChatExample chat={chat} generatedAt={generatedAt} />
        </div>
      </div>
    </section>
  );
};
