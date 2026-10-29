import { PlusIcon } from "@phosphor-icons/react/dist/ssr";
import { FAQ } from "@/content/faq";
import { Section } from "./section";

function faqJsonLd(): string {
  const data = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: FAQ.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  };
  return JSON.stringify(data).replace(/</g, "\\u003c");
}

export const FaqSection: React.FC = () => {
  return (
    <Section split
 id="faq" eyebrow="Questions fréquentes" title="Les réponses aux questions qu'on nous pose le plus">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: faqJsonLd() }} />
      <ul className="flex flex-col gap-3">
        {FAQ.map((item) => (
          <li key={item.question}>
            <details className="group rounded-lg border border-line bg-raised transition hover:bg-hover">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 rounded-lg p-4 text-lg font-bold">
                {item.question}
                <PlusIcon
                  aria-hidden="true"
                  size={20}
                  weight="bold"
                  className="shrink-0 transition group-open:rotate-45"
                />
              </summary>
              <p className="px-4 pb-4 text-base text-muted">{item.answer}</p>
            </details>
          </li>
        ))}
      </ul>
    </Section>
  );
};
