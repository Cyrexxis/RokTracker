import { z } from "zod";

export const KingdomGovernorDataSchema = z.object({
  id: z.union([z.number().int(), z.string()]).default("Skipped"),
  name: z.string().default("Skipped"),
  power: z.union([z.number().int(), z.string()]).default("Skipped"),
  killpoints: z.union([z.number().int(), z.string()]).default("Skipped"),
  alliance: z.string().default("Skipped"),
  t1_kills: z.union([z.number().int(), z.string()]).default("Skipped"),
  t1_kp: z.union([z.number().int(), z.string()]).default("Skipped"),
  t2_kills: z.union([z.number().int(), z.string()]).default("Skipped"),
  t2_kp: z.union([z.number().int(), z.string()]).default("Skipped"),
  t3_kills: z.union([z.number().int(), z.string()]).default("Skipped"),
  t3_kp: z.union([z.number().int(), z.string()]).default("Skipped"),
  t4_kills: z.union([z.number().int(), z.string()]).default("Skipped"),
  t4_kp: z.union([z.number().int(), z.string()]).default("Skipped"),
  t5_kills: z.union([z.number().int(), z.string()]).default("Skipped"),
  t5_kp: z.union([z.number().int(), z.string()]).default("Skipped"),
  ranged_points: z.union([z.number().int(), z.string()]).default("Skipped"),
  dead: z.union([z.number().int(), z.string()]).default("Skipped"),
  rss_assistance: z.union([z.number().int(), z.string()]).default("Skipped"),
  rss_gathered: z.union([z.number().int(), z.string()]).default("Skipped"),
  helps: z.union([z.number().int(), z.string()]).default("Skipped"),
  t45_kills: z.union([z.number().int(), z.string()]).readonly(),
  total_kills: z.union([z.number().int(), z.string()]).readonly(),
});
export type KingdomGovernorData = z.infer<typeof KingdomGovernorDataSchema>;
