"use client";

import { useId, useRef, useSyncExternalStore } from "react";
import { PaletteIcon, XIcon } from "@phosphor-icons/react";
import { cn } from "@/lib/cn";
import { resolveTheme, type ThemeChoice } from "@/lib/theme";
import {
  getPrefersDarkSnapshot,
  getServerPrefersDarkSnapshot,
  getServerThemeSnapshot,
  getThemeSnapshot,
  setTheme,
  subscribePrefersDark,
  subscribeTheme,
} from "@/lib/theme-store";
import { BUTTON_SECONDARY } from "./button-styles";

type Option = { value: ThemeChoice; label: string };

const OPTIONS: readonly Option[] = [
  { value: "light", label: "Thème clair" },
  { value: "dark", label: "Thème sombre" },
  { value: "system", label: "Système" },
];

const THEME_LABELS = { light: "clair", dark: "sombre" } as const;

type ThemeSettingsProps = { variant: "header" | "footer" };

export const ThemeSettings: React.FC<ThemeSettingsProps> = ({ variant }) => {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const id = useId();
  const choice = useSyncExternalStore(subscribeTheme, getThemeSnapshot, getServerThemeSnapshot);
  const prefersDark = useSyncExternalStore(subscribePrefersDark, getPrefersDarkSnapshot, getServerPrefersDarkSnapshot);

  const onOpen = () => {
    dialogRef.current?.showModal();
  };
  const onClose = () => {
    dialogRef.current?.close();
  };
  const onBackdropClick = (event: React.MouseEvent<HTMLDialogElement>) => {
    if (event.target === event.currentTarget) {
      dialogRef.current?.close();
    }
  };
  const onDialogClose = () => {
    triggerRef.current?.focus();
  };
  const onChoose = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    const option = OPTIONS.find((item) => item.value === value);
    if (option !== undefined) {
      setTheme(option.value);
    }
  };

  const titleId = `${id}-titre`;
  const resolved = resolveTheme("system", prefersDark);

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        onClick={onOpen}
        aria-haspopup="dialog"
        className={cn(
          "inline-flex items-center gap-2 px-3 py-2 text-sm transition hover:bg-hover",
          variant === "header" ? "font-medium text-accent" : "font-bold text-accent underline underline-offset-4",
        )}
      >
        <PaletteIcon aria-hidden="true" size={20} weight="bold" />
        <span className={variant === "header" ? "max-sm:sr-only" : undefined}>Paramètres d'affichage</span>
      </button>
      <dialog
        ref={dialogRef}
        aria-labelledby={titleId}
        onClick={onBackdropClick}
        onClose={onDialogClose}
        className="m-auto w-full max-w-md rounded-lg border border-line bg-raised p-6 text-ink backdrop:bg-black/50"
      >
        <div className="flex flex-col gap-6">
          <div className="flex items-start justify-between gap-4">
            <h2 id={titleId} className="font-serif text-2xl font-bold">
              Paramètres d'affichage
            </h2>
            <button
              type="button"
              onClick={onClose}
              aria-label="Fermer"
              className="p-2 text-ink transition hover:bg-hover"
            >
              <XIcon aria-hidden="true" size={20} weight="bold" />
            </button>
          </div>
          <fieldset className="flex flex-col gap-3">
            <legend className="mb-3 text-base text-ink-soft">
              Choisissez un thème pour personnaliser l'apparence du site.
            </legend>
            {OPTIONS.map((option) => (
              <label
                key={option.value}
                htmlFor={`${id}-${option.value}`}
                className={cn(
                  "flex cursor-pointer items-start gap-3 rounded border p-3 transition hover:bg-hover",
                  choice === option.value ? "border-accent" : "border-line",
                )}
              >
                <input
                  id={`${id}-${option.value}`}
                  type="radio"
                  name={`${id}-theme`}
                  value={option.value}
                  checked={choice === option.value}
                  onChange={onChoose}
                  className="mt-1 size-4 accent-accent"
                />
                <span className="flex flex-col">
                  <span className="text-base font-medium">{option.label}</span>
                  {option.value === "system" ? (
                    <span className="text-sm text-muted">
                      Utilise le réglage de votre appareil (actuellement {THEME_LABELS[resolved]}).
                    </span>
                  ) : null}
                </span>
              </label>
            ))}
          </fieldset>
          <button type="button" onClick={onClose} className={`${BUTTON_SECONDARY} self-start`}>
            Fermer
          </button>
        </div>
      </dialog>
    </>
  );
};
