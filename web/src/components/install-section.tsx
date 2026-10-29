"use client";

import { useState } from "react";
import { ASSISTANTS, type AssistantId } from "@/content/install";
import { cn } from "@/lib/cn";
import { CopyButton } from "./copy-button";
import { CopyField } from "./copy-field";
import { Section } from "./section";

export const InstallSection: React.FC = () => {
  const [selected, setSelected] = useState<AssistantId>("claude");
  const guide = ASSISTANTS.find((item) => item.id === selected) ?? ASSISTANTS[0];

  const onTabKey = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    const index = ASSISTANTS.findIndex((item) => item.id === selected);
    const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (step === 0) {
      return;
    }
    event.preventDefault();
    const next = ASSISTANTS[(index + step + ASSISTANTS.length) % ASSISTANTS.length];
    if (next !== undefined) {
      setSelected(next.id);
      document.getElementById(`assistant-${next.id}`)?.focus();
    }
  };

  if (guide === undefined) {
    return null;
  }

  return (
    <Section
      id="installer"
      eyebrow="Installer"
      title="Ajoutez le connecteur en deux minutes"
      intro="Copiez l'adresse, puis suivez les étapes de votre assistant. Aucun compte à créer chez nous, aucune clé à générer."
    >
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-3">
          <p className="text-sm font-semibold">Étape 1. L'adresse du connecteur</p>
          <CopyField />
        </div>

        <div className="flex flex-col gap-4">
          <p className="text-sm font-semibold">Étape 2. Votre assistant</p>
          <div
            role="tablist"
            aria-label="Assistant"
            className="flex flex-wrap gap-1 self-start rounded-xl border border-line bg-surface p-1"
          >
            {ASSISTANTS.map((item) => (
              <button
                key={item.id}
                type="button"
                role="tab"
                id={`assistant-${item.id}`}
                aria-selected={item.id === selected}
                aria-controls="assistant-panneau"
                tabIndex={item.id === selected ? 0 : -1}
                onClick={() => {
                  setSelected(item.id);
                }}
                onKeyDown={onTabKey}
                className={cn(
                  "rounded-lg px-3 py-2 text-base font-semibold transition active:scale-98",
                  item.id === selected ? "bg-raised text-ink" : "text-muted hover:bg-hover hover:text-ink",
                )}
              >
                {item.name}
              </button>
            ))}
          </div>

          <div
            id="assistant-panneau"
            role="tabpanel"
            aria-labelledby={`assistant-${guide.id}`}
            className="flex flex-col gap-6 rounded-2xl border border-line bg-surface p-6"
          >
            <p className="text-sm text-muted">{guide.availability}</p>
            <ol className="flex flex-col gap-3 text-base">
              {guide.steps.map((step, index) => (
                <li key={step} className="flex gap-3">
                  <span className="tabular w-6 shrink-0 font-mono text-muted">{index + 1}.</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
            {guide.sample !== undefined ? (
              <div className="flex flex-col gap-2 rounded-lg bg-raised p-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold">{guide.sample.label}</p>
                  <CopyButton value={guide.sample.code} label="Copier" variant="secondary" />
                </div>
                <pre className="overflow-x-auto rounded-sm bg-surface p-3 font-mono text-sm">
                  <code>{guide.sample.code}</code>
                </pre>
              </div>
            ) : null}
            <p className="text-sm text-muted">{guide.note}</p>
          </div>
        </div>

        <div className="flex max-w-hero flex-col gap-2 rounded-2xl border border-line bg-raised p-6">
          <p className="text-base font-semibold">Étape 3. Demandez</p>
          <p className="text-base text-muted">
            Activez le connecteur dans la conversation, puis écrivez par exemple : « Utilise l'outil Assemblée nationale
            pour me dire comment a voté ma députée sur le budget. » Citer l'outil évite que l'assistant réponde de mémoire.
          </p>
        </div>
      </div>
    </Section>
  );
};
