import { ArrowUpRightIcon } from "@phosphor-icons/react/dist/ssr";
import { EN_CLAIR, EXAMPLE_QUESTIONS, GLOSSARY } from "@/content/faq";
import { LINK_TEXT } from "./button-styles";
import { CopyButton } from "./copy-button";

const FIND_DEPUTE_URL = "https://www.assemblee-nationale.fr/dyn/vos-deputes";

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
          <div className="flex flex-col gap-4">
            <h3 className="border-b-2 border-rule pb-3 font-display text-2xl font-semibold tracking-tight">
              Des questions à copier pour commencer
            </h3>
            <ul className="flex flex-col">
              {EXAMPLE_QUESTIONS.map((question) => (
                <li
                  key={question}
                  className="flex flex-col gap-2 border-b border-line py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-6"
                >
                  <p className="text-lg">«&nbsp;{question}&nbsp;»</p>
                  <div className="shrink-0 self-start sm:self-auto">
                    <CopyButton value={question} label="Copier" variant="secondary" />
                  </div>
                </li>
              ))}
            </ul>
            <p className="max-w-measure text-sm text-ink-soft">
              Vous ne connaissez pas le nom de votre député ? Cherchez votre département sur la page{" "}
              <a href={FIND_DEPUTE_URL} className={LINK_TEXT}>
                « Vos députés » de l'Assemblée nationale{" "}
                <ArrowUpRightIcon aria-hidden="true" size={14} weight="bold" className="inline" />
              </a>
              , puis remplacez le texte entre crochets.
            </p>
          </div>
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
