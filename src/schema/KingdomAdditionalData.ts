import { z } from "zod";

export const KingdomAdditionalDataSchema = z.object({
  current_governor: z.number().int(),
  target_governor: z.number().int(),
  skipped_governors: z.number().int(),
  power_ok: z.union([z.boolean(), z.string()]),
  kills_ok: z.union([z.boolean(), z.string()]),
  reconstruction_success: z.union([z.boolean(), z.string()]),
  remaining_sec: z.number(),
  current_time: z
    .string()
    .datetime({ offset: true })
    .default("2025-01-23T15:04:12.742202"),
});
export type KingdomAdditionalData = z.infer<typeof KingdomAdditionalDataSchema>;
