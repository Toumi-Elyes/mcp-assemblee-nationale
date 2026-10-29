import { CtaLink } from "./cta-link";
import { ChatExample } from "./chat-example";
import { HeroProof } from "./hero-proof";
import type { HeroChat } from "@/lib/data/view-types";

type HeroProps = { chat: HeroChat | null; generatedAt: Date };

export const Hero: React.FC<HeroProps> = ({ chat, generatedAt }) => {
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
          <HeroProof />
        </div>
        <div className="lg:col-span-5 lg:mt-24">
          <ChatExample chat={chat} generatedAt={generatedAt} />
        </div>
      </div>
    </section>
  );
};
