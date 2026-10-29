import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/config";
import { getHomeView } from "@/lib/data/home-view";
import { settle } from "@/lib/data/result";

export const revalidate = 1800;

const SCRUTIN_LIMIT = 30;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages: MetadataRoute.Sitemap = [
    { url: SITE_URL, changeFrequency: "daily", priority: 1 },
    { url: `${SITE_URL}/confidentialite`, changeFrequency: "yearly", priority: 0.3 },
    { url: `${SITE_URL}/mentions`, changeFrequency: "yearly", priority: 0.3 },
  ];
  const loaded = await settle(getHomeView());
  if (!loaded.ok) {
    return pages;
  }
  const uids = new Set<string>();
  for (const group of loaded.data.week?.groups ?? []) {
    for (const scrutin of group.scrutins) {
      uids.add(scrutin.uid);
    }
  }
  for (const scrutin of loaded.data.trends?.finalVotes ?? []) {
    uids.add(scrutin.uid);
  }
  const scrutins = [...uids].slice(0, SCRUTIN_LIMIT).map((uid) => ({
    url: `${SITE_URL}/scrutins/${uid}`,
    changeFrequency: "monthly" as const,
    priority: 0.5,
  }));
  return [...pages, ...scrutins];
}
