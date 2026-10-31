import { describe, expect, it } from "vitest";
import { plainTitle } from "@/lib/plain-title";

describe("plainTitle", () => {
  it("reformule un vote sur l'ensemble d'une proposition de loi", () => {
    expect(
      plainTitle(
        "l'ensemble de la proposition de loi visant à créer un corps de fonctionnaires de catégorie B pour les accompagnants d’élèves en situation de handicap (première lecture).",
      ),
    ).toEqual({
      what: "Vote sur le texte entier",
      about: "Créer un corps de fonctionnaires de catégorie B pour les accompagnants d’élèves en situation de handicap",
    });
  });

  it("nomme le budget de l'État au lieu du projet de loi de finances", () => {
    expect(
      plainTitle(
        "l'amendement n° 3138 de Mme Bellay après l'article 15 (examen prioritaire) du projet de loi de finances pour 2027 (première lecture).",
      ),
    ).toEqual({ what: "Vote sur une modification (amendement n° 3138)", about: "Budget de l'État pour 2027" });
  });

  it("reconnaît un article, un sous amendement et le budget de la Sécurité sociale", () => {
    expect(plainTitle("l'article premier du projet de loi de financement de la sécurité sociale pour 2027 (première lecture).")).toEqual({
      what: "Vote sur l'article 1er",
      about: "Budget de la Sécurité sociale pour 2027",
    });
    expect(
      plainTitle(
        "le sous-amendement n° 128 de Mme Fiol à l'amendement n° 4 de Mme Blanc à l'article premier de la proposition de loi pour protéger durablement les jeunes majeurs de l'aide sociale à l'enfance (première lecture).",
      ).what,
    ).toBe("Vote sur la modification d'un amendement");
  });

  it("explique les motions", () => {
    expect(plainTitle("la motion de censure déposée en application de l'article 49, alinéa 3, de la Constitution").what).toBe(
      "Motion de censure : vote pour renverser le Gouvernement",
    );
    expect(plainTitle("la motion de rejet préalable du projet de loi relatif à la sécurisation de l'emploi.")).toEqual({
      what: "Motion pour rejeter le texte avant son examen",
      about: "La sécurisation de l'emploi",
    });
  });

  it("ne devine pas de sujet quand le titre ne nomme aucun texte", () => {
    expect(plainTitle("la déclaration du Gouvernement sur la situation au Proche-Orient.")).toEqual({
      what: "Vote sur une déclaration du Gouvernement",
      about: null,
    });
  });
});
