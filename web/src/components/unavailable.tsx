import { WarningCircleIcon } from "@phosphor-icons/react/dist/ssr";

type UnavailableProps = { title?: string; detail?: string };

export const Unavailable: React.FC<UnavailableProps> = ({
  title = "Données momentanément indisponibles",
  detail = "La source des données ne répond pas pour le moment. Réessayez dans quelques minutes : cette page se met à jour toute seule.",
}) => {
  return (
    <div role="status" className="flex max-w-hero flex-col gap-2 rounded-2xl border border-line bg-raised p-6">
      <WarningCircleIcon aria-hidden="true" size={24} weight="bold" />
      <p className="text-lg font-semibold">{title}</p>
      <p className="text-base text-muted">{detail}</p>
    </div>
  );
};
