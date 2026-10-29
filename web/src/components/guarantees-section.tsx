import { CodeIcon, CoinsIcon, EyeIcon, UserMinusIcon } from "@phosphor-icons/react/dist/ssr";
import { GITHUB_URL } from "@/lib/config";
import { LINK_TEXT } from "./button-styles";
import { Reveal } from "./reveal";
import { Section } from "./section";

export const GuaranteesSection: React.FC = () => {
  const items = [
    { Icon: CoinsIcon, title: "Gratuit", text: "Le connecteur, l'accès aux données et l'hébergement ne coûtent rien." },
    { Icon: UserMinusIcon, title: "Sans compte ni clé", text: "Aucune inscription, aucune clé à générer, aucun cookie." },
    { Icon: EyeIcon, title: "Lecture seule", text: "L'assistant peut consulter les données, jamais rien modifier." },
  ];
  return (
    <Section
      id="garanties"
      eyebrow="Sans risque"
      title="Vous ne risquez rien à essayer"
      intro="Pas d'abonnement à résilier, pas de carte bancaire, pas de période d'essai : le projet est simplement ouvert à tous."
      tone="surface"
    >
      <ul className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {items.map((item, index) => (
          <li key={item.title}>
            <Reveal delay={index * 80} className="h-full">
              <article className="flex h-full flex-col gap-3 rounded-2xl border border-line bg-raised p-6">
                <item.Icon aria-hidden="true" size={32} weight="bold" />
                <h3 className="text-xl font-semibold">{item.title}</h3>
                <p className="text-base text-muted">{item.text}</p>
              </article>
            </Reveal>
          </li>
        ))}
        <li>
          <Reveal delay={240} className="h-full">
            <article className="flex h-full flex-col gap-3 rounded-2xl border border-line bg-raised p-6">
              <CodeIcon aria-hidden="true" size={32} weight="bold" />
              <h3 className="text-xl font-semibold">Code ouvert</h3>
              <p className="text-base text-muted">
                Chacun peut lire le code, sous licence MIT.{" "}
                <a href={GITHUB_URL} className={LINK_TEXT}>
                  Voir sur GitHub
                </a>
                .
              </p>
            </article>
          </Reveal>
        </li>
      </ul>
    </Section>
  );
};
