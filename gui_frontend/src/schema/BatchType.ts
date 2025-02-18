import { z } from "zod";

export const BatchTypeSchema = z.object({
  type: z.enum(["Alliance", "Honor", "Seed"]),
});
export type BatchType = z.infer<typeof BatchTypeSchema>;
