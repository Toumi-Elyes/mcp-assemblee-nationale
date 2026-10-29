import { ArrowDownIcon } from "@phosphor-icons/react/dist/ssr";
import { CTA_LABEL, INSTALL_HREF } from "@/lib/config";
import { BUTTON_PRIMARY } from "./button-styles";

export const CtaLink: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <a href={INSTALL_HREF} className={className !== undefined ? `${BUTTON_PRIMARY} ${className}` : BUTTON_PRIMARY}>
      {CTA_LABEL}
      <ArrowDownIcon aria-hidden="true" size={20} weight="bold" />
    </a>
  );
};
