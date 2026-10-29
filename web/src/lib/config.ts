export const MCP_URL =
  process.env.NEXT_PUBLIC_MCP_URL ?? "https://mcp-assemblee-nationale.vercel.app/mcp";

export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL ??
  (process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : "http://localhost:3000")
).replace(/\/$/, "");

export const GITHUB_URL = "https://github.com/Toumi-Elyes/mcp-assemblee-nationale";
export const GITHUB_ISSUES_URL = `${GITHUB_URL}/issues`;
export const CIVIX_SITE = "https://www.civix.fr";
export const ASSEMBLEE_SITE = "https://www.assemblee-nationale.fr";
export const DATA_GOUV_URL = "https://www.data.gouv.fr/dataservices/api-publique-civix";
export const LICENCE_URL = "https://www.etalab.gouv.fr/licence-ouverte-open-licence/";
export const TIMEZONE = "Europe/Paris";

export const REVALIDATE_SECONDS = 1800;

export const SITE_NAME = "MCP Assemblée nationale";
export const INSTALL_HREF = "#installer";
export const CTA_LABEL = "Ajouter à mon assistant";
