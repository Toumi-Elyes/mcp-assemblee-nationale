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
    <Section id="faq" eyebrow="Questions fréquentes" title="Les réponses aux questions qu'on nous pose le plus">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: faqJsonLd() }} />
      <ul className="flex max-w-3xl flex-col gap-3">
        {FAQ.map((item) => (
          <li key={item.question}>
            <details className="group rounded-2xl border border-line bg-surface transition hover:bg-hover">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 rounded-2xl p-4 text-lg font-semibold">
                {item.question}
                <PlusIcon
                  aria-hidden="true"
                  size={20}
                  weight="bold"
                  className="shrink-0 transition duration-500 group-open:rotate-45"
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
