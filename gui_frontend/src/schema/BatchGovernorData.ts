import { z } from "zod";

export const BatchGovernorDataSchema = z.object({
  img_path: z.string(),
  name: z.string(),
  score: z.union([z.number().int(), z.string()]),
});
export type BatchGovernorData = z.infer<typeof BatchGovernorDataSchema>;
