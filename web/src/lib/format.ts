import { TIMEZONE } from "@/lib/config";
import type { Position, VoteResult } from "@/lib/civix/types";

const numberFormat = new Intl.NumberFormat("fr-FR");
const percentFormat = new Intl.NumberFormat("fr-FR", { style: "percent", maximumFractionDigits: 0 });
const dayFormat = new Intl.DateTimeFormat("fr-FR", {
  day: "numeric",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});
const shortDayFormat = new Intl.DateTimeFormat("fr-FR", {
  day: "numeric",
  month: "short",
  timeZone: "UTC",
});
const longDayFormat = new Intl.DateTimeFormat("fr-FR", {
  weekday: "long",
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "UTC",
});
const timestampFormat = new Intl.DateTimeFormat("fr-FR", {
  day: "numeric",
  month: "long",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: TIMEZONE,
});

function parseDay(day: string): Date {
  return new Date(`${day}T00:00:00Z`);
}

export function formatNumber(value: number): string {
  return numberFormat.format(value);
}

export function formatPercent(value: number): string {
  return percentFormat.format(value);
}

export function formatDay(day: string | null): string {
  return day === null ? "Date inconnue" : dayFormat.format(parseDay(day));
}

export function formatShortDay(day: string): string {
  return shortDayFormat.format(parseDay(day));
}

export function formatLongDay(day: string | null): string {
  return day === null ? "Date inconnue" : longDayFormat.format(parseDay(day));
}

export function formatTimestamp(date: Date): string {
  return timestampFormat.format(date);
}

export const POSITION_LABELS: Record<Position, string> = {
  pour: "Pour",
  contre: "Contre",
  abstention: "Abstention",
  non_votant: "Non-votant",
  unknown: "Position inconnue",
};

export const RESULT_LABELS: Record<VoteResult, string> = {
  adopte: "Adopté",
  rejete: "Rejeté",
  inconnu: "Résultat inconnu",
};

export function pluralize(count: number, singular: string, plural: string = `${singular}s`): string {
  return `${formatNumber(count)} ${count === 1 || count === 0 ? singular : plural}`;
}
