import { z } from "zod";

export const ScanPresetSchema = z.object({
  name: z.string(),
  selections: z.array(
    z.enum([
      "ID",
      "Name",
      "Power",
      "Killpoints",
      "Alliance",
      "T1 Kills",
      "T2 Kills",
      "T3 Kills",
      "T4 Kills",
      "T5 Kills",
      "Ranged",
      "Deaths",
      "Assistance",
      "Gathered",
      "Helps",
    ]),
  ),
});
export type ScanPreset = z.infer<typeof ScanPresetSchema>;
