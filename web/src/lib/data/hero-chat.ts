import "server-only";
import { cache } from "react";
import { getScrutinVotes } from "@/lib/civix/api";
import { toPosition, toResult } from "@/lib/civix/mappers";
import { firstAssembleeUrl, safeUrl } from "@/lib/civix/urls";
import { CIVIX_SITE } from "@/lib/config";
import { cleanTitle } from "@/lib/text";
import { getFinalVotes, getSuggestions } from "./home";
import type { HeroChat } from "./view-types";

const QUESTION_TOPIC_LIMIT = 90;
const GENERIC_SUBJECT = "le dernier texte voté en entier";

export const getHeroChat = cache(async (): Promise<HeroChat | null> => {
  const [finals, suggestions] = await Promise.all([getFinalVotes(), getSuggestions()]);
  const latest = finals[0];
  const depute = suggestions.deputes[0];
  if (latest === undefined || depute === undefined) {
    return null;
  }
  const response = await getScrutinVotes(latest.uid);
  const attributes = response.data.attributes;
  const vote = attributes.votes.find((item) => item.deputy_uid === depute.uid);
  if (vote === undefined) {
    return null;
  }
  const topic = latest.dossier?.label ?? latest.title;
  const assembleeUrl = firstAssembleeUrl(response.source?.source_urls ?? []);
  const cleanTopic = cleanTitle(topic);
  const subject = cleanTopic.length <= QUESTION_TOPIC_LIMIT && !cleanTopic.endsWith("…") ? cleanTopic : GENERIC_SUBJECT;
  return {
    question: `Comment a voté ${depute.fullName} sur ${subject} ?`,
    depute,
    position: toPosition(vote.position),
    result: toResult(attributes.scrutin.sort_code, attributes.scrutin.is_adopted),
    date: latest.date,
    scrutinTitle: latest.title,
    scrutinUid: latest.uid,
    counts: attributes.results_global ?? null,
    civixUrl: safeUrl(response.source?.civix_urls["page"], `${CIVIX_SITE}/votes/${latest.uid}`),
    assembleeUrl,
  };
});
