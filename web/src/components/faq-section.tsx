import { PlusIcon } from "@phosphor-icons/react/dist/ssr";
import { FAQ } from "@/content/faq";

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
    <section id="faq" aria-labelledby="faq-titre" className="py-16 sm:py-20">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: faqJsonLd() }} />
      <div className="mx-auto grid w-full max-w-page gap-8 px-4 sm:px-6 lg:grid-cols-12 lg:gap-12">
        <h2 id="faq-titre" className="font-display text-4xl font-semibold tracking-tight sm:text-5xl lg:col-span-4">
          Les réponses aux questions qu'on nous pose le plus
        </h2>
        <ul className="border-t-2 border-rule lg:col-span-8">
          {FAQ.map((item) => (
            <li key={item.question} className="border-b border-line">
              <details className="group">
                <summary className="flex cursor-pointer list-none items-start justify-between gap-6 py-4 font-display text-xl font-semibold leading-snug transition-colors hover:text-accent">
                  {item.question}
                  <PlusIcon
                    aria-hidden="true"
                    size={20}
                    weight="bold"
                    className="mt-1 shrink-0 transition-transform duration-200 group-open:rotate-45"
                  />
                </summary>
                <p className="max-w-measure pb-5 text-base text-ink-soft">{item.answer}</p>
              </details>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};
