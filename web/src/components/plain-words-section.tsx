import { EN_CLAIR, GLOSSARY } from "@/content/faq";

export const PlainWordsSection: React.FC = () => {
  return (
    <section id="en-clair" aria-labelledby="en-clair-titre" className="border-t-2 border-rule py-16 sm:py-20">
      <div className="mx-auto grid w-full max-w-page gap-12 px-4 sm:px-6 lg:grid-cols-12">
        <div className="flex flex-col gap-8 lg:col-span-8">
          <h2 id="en-clair-titre" className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">
            En clair
          </h2>
          <dl className="grid gap-x-10 sm:grid-cols-2">
            {EN_CLAIR.map((item) => (
              <div key={item.question} className="flex flex-col gap-2 border-t border-line py-5">
                <dt className="font-display text-2xl font-semibold leading-tight tracking-tight">{item.question}</dt>
                <dd className="text-base text-ink-soft">{item.answer}</dd>
              </div>
            ))}
          </dl>
        </div>
        <aside aria-labelledby="lexique-titre" className="flex flex-col gap-4 lg:col-span-4">
          <h3 id="lexique-titre" className="border-b-2 border-rule pb-3 font-display text-xl font-semibold tracking-tight">
            Les mots que vous croiserez sur ce site
          </h3>
          <dl className="flex flex-col">
            {GLOSSARY.map((item) => (
              <div key={item.term} className="flex flex-col gap-1 border-b border-line py-3">
                <dt className="font-display text-lg font-semibold">{item.term}</dt>
                <dd className="text-sm text-ink-soft">{item.definition}</dd>
              </div>
            ))}
          </dl>
        </aside>
      </div>
    </section>
  );
};
