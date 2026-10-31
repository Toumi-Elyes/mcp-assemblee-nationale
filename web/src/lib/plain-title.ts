import { capitalize, fold } from "./text";

/** Titre d'un scrutin reformulé pour un public non spécialiste : ce qui a été voté, et sur quel texte. */
export type PlainTitle = { what: string; about: string | null };

const WHAT_RULES: readonly [RegExp, string | ((found: RegExpMatchArray) => string)][] = [
  [/^l ensemble/, "Vote sur le texte entier"],
  [/^le sous amendement/, "Vote sur la modification d'un amendement"],
  [/^(?:l amendement|les amendements) n° ?(\d+)/, (found) => `Vote sur une modification (amendement n° ${found[1]})`],
  [/^(l amendement|les amendements)/, "Vote sur une modification (amendement)"],
  [/^l article (\S+)/, (found) => `Vote sur l'article ${found[1] === "premier" ? "1er" : found[1]}`],
  [/^la motion de censure/, "Motion de censure : vote pour renverser le Gouvernement"],
  [/^la motion de rejet/, "Motion pour rejeter le texte avant son examen"],
  [/^la motion de renvoi/, "Motion pour renvoyer le texte en commission"],
  [/^la declaration du gouvernement/, "Vote sur une déclaration du Gouvernement"],
  [/^la proposition de resolution/, "Vote sur une résolution"],
];

const TEXT_NAME = /(projet|proposition) de loi( organique| constitutionnelle)?|proposition de résolution/gi;

const BUDGETS: readonly [RegExp, (year: string) => string][] = [
  [/^de finances rectificative pour (\d{4})/i, (year) => `Budget rectificatif de l'État pour ${year}`],
  [/^de finances pour (\d{4})/i, (year) => `Budget de l'État pour ${year}`],
  [/^de financement de la sécurité sociale pour (\d{4})/i, (year) => `Budget de la Sécurité sociale pour ${year}`],
];

const LEADING_WORDS = /^(visant à |visant au |visant aux |tendant à |relatif à |relative à |relatif au |relative au |relatif aux |relative aux |portant |pour |sur |de |d')/i;

function what(title: string): string {
  const folded = fold(title).trim();
  for (const [pattern, label] of WHAT_RULES) {
    const found = folded.match(pattern);
    if (found !== null) {
      return typeof label === "string" ? label : label(found);
    }
  }
  return "Vote";
}

function about(title: string): string | null {
  const names = [...title.matchAll(TEXT_NAME)];
  const last = names.at(-1);
  if (last?.index === undefined) {
    return null;
  }
  let rest = title.slice(last.index + last[0].length).trim();
  rest = rest.replace(/\s*\.+\s*$/, "").replace(/\s*\([^()]*\)\s*$/, "").trim();
  for (const [pattern, name] of BUDGETS) {
    const found = rest.match(pattern);
    if (found?.[1] !== undefined) {
      return name(found[1]);
    }
  }
  rest = rest.replace(LEADING_WORDS, "").trim();
  return rest === "" ? null : capitalize(rest);
}

export function plainTitle(title: string): PlainTitle {
  return { what: what(title), about: about(title) };
}
