import type { MetadataRoute } from "next";
import { listScrutins } from "@/lib/civix";
import { SITE_URL } from "@/lib/config";

export const revalidate = 3600;

const sitemap = async (): Promise<MetadataRoute.Sitemap> => {
  const entries: MetadataRoute.Sitemap = [{ url: SITE_URL, changeFrequency: "daily", priority: 1 }];
  try {
    const { scrutins } = await listScrutins({ pageSize: 50 });
    for (const scrutin of scrutins) {
      entries.push({
        url: `${SITE_URL}/scrutins/${scrutin.uid}`,
        lastModified: scrutin.date ?? undefined,
        changeFrequency: "monthly",
        priority: 0.5,
      });
    }
  } catch {
    return entries;
  }
  return entries;
};

export default sitemap;
