const BASE =
  "inline-flex items-center justify-center gap-2 rounded-lg px-3 py-2 font-semibold transition hover:-translate-y-0.5 active:translate-y-px active:scale-98 motion-reduce:hover:translate-y-0";

export const BUTTON_PRIMARY = `${BASE} bg-accent text-base text-on-accent hover:bg-accent-hover`;
export const BUTTON_PRIMARY_SMALL = `${BASE} bg-accent text-sm text-on-accent hover:bg-accent-hover`;
export const BUTTON_SECONDARY = `${BASE} border border-line bg-raised text-base text-ink hover:bg-hover`;
export const BUTTON_SECONDARY_SMALL = `${BASE} border border-line bg-raised text-sm text-ink hover:bg-hover`;

export const LINK_TEXT =
  "underline decoration-line underline-offset-4 transition hover:decoration-ink";
