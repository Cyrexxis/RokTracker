import { z } from "zod";

export const BatchAdditionalDataSchema = z.object({
  current_page: z.number().int(),
  govs_per_page: z.number().int(),
  target_governor: z.number().int(),
  remaining_sec: z.number(),
  current_time: z
    .string()
    .datetime({ offset: true })
    .default("2025-01-27T22:09:30.600098+01:00"),
});
export type BatchAdditionalData = z.infer<typeof BatchAdditionalDataSchema>;
