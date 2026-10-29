"use client";

import { useState } from "react";
import { ASSISTANTS, type AssistantId } from "@/content/install";
import { cn } from "@/lib/cn";
import { CopyButton } from "./copy-button";
import { CopyField } from "./copy-field";
import { Section } from "./section";

const Stop: React.FC<{ index: number; title: string; last?: boolean; children: React.ReactNode }> = ({
  index,
  title,
  last = false,
  children,
}) => {
  return (
    <li className="grid grid-cols-[auto_minmax(0,1fr)] gap-x-5">
      <div aria-hidden="true" className="flex flex-col items-center">
        <span className="grid size-8 shrink-0 place-items-center rounded-full border-2 border-rule bg-bg font-display text-base font-bold">
          {index}
        </span>
        {last ? null : <span className="w-0.5 flex-1 bg-rule" />}
      </div>
      <div className={cn("flex min-w-0 flex-col gap-4", last ? "pb-0" : "pb-12")}>
        <h3 className="pt-0.5 font-display text-2xl font-semibold tracking-tight">
          <span className="sr-only">Étape {index} : </span>
          {title}
        </h3>
        {children}
      </div>
    </li>
  );
};

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
      title="Ajoutez le connecteur en deux minutes"
      intro="Copiez l'adresse, puis suivez les étapes de votre assistant. Aucun compte à créer chez nous, aucune clé à générer."
    >
      <ol className="flex flex-col">
        <Stop index={1} title="L'adresse du connecteur">
          <CopyField id="adresse-connecteur-installation" className="max-w-2xl" />
        </Stop>

        <Stop index={2} title="Votre assistant">
          <div role="tablist" aria-label="Assistant" className="flex max-w-full gap-x-1 self-start overflow-x-auto border-b border-line">
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
                  "-mb-px shrink-0 whitespace-nowrap border-b-2 px-3 py-2 font-display text-lg font-semibold transition-colors",
                  item.id === selected ? "border-rule text-ink" : "border-transparent text-muted hover:text-accent",
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
            className="flex max-w-3xl flex-col gap-5 pt-2"
          >
            <p className="text-sm text-muted">{guide.availability}</p>
            <ol className="flex flex-col text-base">
              {guide.steps.map((step, index) => (
                <li key={step} className="flex gap-4 border-b border-line py-3">
                  <span className="tabular w-5 shrink-0 font-display font-semibold text-muted">{index + 1}</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
            {guide.sample !== undefined ? (
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-bold">{guide.sample.label}</p>
                  <CopyButton value={guide.sample.code} label="Copier" variant="secondary" />
                </div>
                <pre className="overflow-x-auto rounded-sm bg-surface p-4 font-mono text-sm">
                  <code>{guide.sample.code}</code>
                </pre>
              </div>
            ) : null}
            <p className="text-sm text-ink-soft">{guide.note}</p>
          </div>
        </Stop>

        <Stop index={3} title="Demandez" last>
          <p className="max-w-measure text-base text-ink-soft">
            Activez le connecteur dans la conversation, puis écrivez par exemple : « Utilise l'outil Assemblée nationale
            pour me dire comment a voté ma députée sur le budget. » Citer l'outil évite que l'assistant réponde de mémoire.
          </p>
        </Stop>
      </ol>
    </Section>
  );
};
