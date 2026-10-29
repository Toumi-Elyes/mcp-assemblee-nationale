import { WarningCircleIcon } from "@phosphor-icons/react/dist/ssr";

type UnavailableProps = { title?: string; detail?: string };

export const Unavailable: React.FC<UnavailableProps> = ({
  title = "Données momentanément indisponibles",
  detail = "La source des données ne répond pas pour le moment. Réessayez dans quelques minutes : cette page se met à jour toute seule.",
}) => {
  return (
    <div role="status" className="flex max-w-measure gap-3 border-y border-line py-5">
      <WarningCircleIcon aria-hidden="true" size={24} weight="bold" className="mt-0.5 shrink-0" />
      <div className="flex flex-col gap-1">
        <p className="text-lg font-bold">{title}</p>
        <p className="text-base text-ink-soft">{detail}</p>
      </div>
    </div>
  );
};
