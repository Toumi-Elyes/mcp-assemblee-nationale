"use client";

import { useState } from "react";
import { CheckIcon, CopyIcon, WarningIcon } from "@phosphor-icons/react";
import { cn } from "@/lib/cn";
import { BUTTON_PRIMARY, BUTTON_SECONDARY_SMALL } from "./button-styles";

type CopyState = "idle" | "copied" | "failed";

const RESET_DELAY_MS = 2500;

type CopyButtonProps = {
  value: string;
  label: string;
  variant?: "primary" | "secondary";
  attached?: boolean;
};

export const CopyButton: React.FC<CopyButtonProps> = ({ value, label, variant = "primary", attached = false }) => {
  const [state, setState] = useState<CopyState>("idle");

  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setState("copied");
    } catch {
      setState("failed");
    }
    window.setTimeout(() => {
      setState("idle");
    }, RESET_DELAY_MS);
  };

  const Icon = state === "copied" ? CheckIcon : state === "failed" ? WarningIcon : CopyIcon;
  const text = state === "copied" ? "Copié" : state === "failed" ? "Copie impossible" : label;

  return (
    <>
      <button
        type="button"
        onClick={onCopy}
        className={cn(
          variant === "primary" ? BUTTON_PRIMARY : BUTTON_SECONDARY_SMALL,
          attached ? "shrink-0 sm:rounded-l-none" : undefined,
        )}
      >
        <Icon aria-hidden="true" size={20} weight="bold" />
        {text}
      </button>
      <span role="status" className="sr-only">
        {state === "copied" ? "Le texte a été copié." : null}
        {state === "failed" ? "La copie a échoué. Sélectionnez le texte pour le copier à la main." : null}
      </span>
    </>
  );
};
