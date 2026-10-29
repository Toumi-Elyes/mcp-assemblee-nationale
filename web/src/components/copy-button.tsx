"use client";

import { Check, Copy } from "lucide-react";
import { useState } from "react";

const RESET_DELAY_MS = 2000;

type CopyButtonProps = { value: string; label?: string; className?: string };

export const CopyButton: React.FC<CopyButtonProps> = ({ value, label = "Copier", className }) => {
  const [copied, setCopied] = useState(false);

  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => {
        setCopied(false);
      }, RESET_DELAY_MS);
    } catch {
      setCopied(false);
    }
  };

  return (
    <button type="button" onClick={onCopy} className={`btn ${className ?? ""}`}>
      {copied ? <Check aria-hidden className="size-4" /> : <Copy aria-hidden className="size-4" />}
      <span aria-live="polite">{copied ? "Copié" : label}</span>
    </button>
  );
};
