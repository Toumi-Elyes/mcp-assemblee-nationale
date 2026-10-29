import { TIMEZONE } from "@/lib/config";

const MS_PER_DAY = 86_400_000;

export function dayKey(date: Date): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: TIMEZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
}

export function addDays(key: string, amount: number): string {
  const time = Date.parse(`${key}T00:00:00Z`) + amount * MS_PER_DAY;
  return new Date(time).toISOString().slice(0, 10);
}

export function daysBetween(from: string, to: string): number {
  return Math.round((Date.parse(`${to}T00:00:00Z`) - Date.parse(`${from}T00:00:00Z`)) / MS_PER_DAY);
}
