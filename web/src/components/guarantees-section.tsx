import { GITHUB_URL } from "@/lib/config";
import { LINK_TEXT } from "./button-styles";

const ITEMS = [
  { title: "Gratuit", text: "Le connecteur, l'accès aux données et l'hébergement ne coûtent rien." },
  { title: "Sans inscription", text: "Aucun compte à créer, aucun mot de passe, aucun cookie." },
  { title: "Rien ne peut être modifié", text: "L'assistant peut seulement lire les votes, jamais rien changer." },
] as const;

export const GuaranteesSection: React.FC = () => {
  return (
    <section id="garanties" aria-labelledby="garanties-titre" className="border-t border-line py-16 sm:py-20">
      <div className="mx-auto grid w-full max-w-page gap-8 px-4 sm:px-6 lg:grid-cols-12 lg:gap-12">
        <div className="flex flex-col gap-3 lg:col-span-4">
          <h2 id="garanties-titre" className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
            Vous ne risquez rien à essayer
          </h2>
          <p className="text-base text-ink-soft">
            Pas d'abonnement à résilier, pas de carte bancaire, pas de période d'essai : le projet est simplement ouvert à
            tous.
          </p>
        </div>
        <dl className="grid gap-x-8 sm:grid-cols-2 lg:col-span-8">
          {ITEMS.map((item) => (
            <div key={item.title} className="flex flex-col gap-1 border-t border-rule py-4">
              <dt className="font-display text-xl font-semibold">{item.title}</dt>
              <dd className="text-base text-ink-soft">{item.text}</dd>
            </div>
          ))}
          <div className="flex flex-col gap-1 border-t border-rule py-4">
            <dt className="font-display text-xl font-semibold">Code ouvert</dt>
            <dd className="text-base text-ink-soft">
              Le code du projet est public : chacun peut vérifier ce qu'il fait.{" "}
              <a href={GITHUB_URL} className={LINK_TEXT}>
                Voir sur GitHub
              </a>
              .
            </dd>
          </div>
        </dl>
      </div>
    </section>
  );
};
