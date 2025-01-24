import { z } from "zod";

export const FullConfigSchema = z.object({
  scan: z.object({
    kingdom_name: z.string().default(""),
    people_to_scan: z.number().int().default(300),
    resume: z.boolean().default(false),
    advanced_scroll: z.boolean().default(true),
    track_inactives: z.boolean().default(false),
    validate_power: z.boolean().default(false),
    power_threshold: z.number().int().default(100000),
    validate_kills: z.boolean().default(true),
    reconstruct_kills: z.boolean().default(true),
    timings: z.object({
      gov_open: z.number().default(2),
      copy_wait: z.number().default(0.2),
      kills_open: z.number().default(1),
      info_open: z.number().default(1),
      info_close: z.number().default(0.5),
      gov_close: z.number().default(1),
      max_random: z.number().default(0.5),
    }),
    formats: z.object({
      xlsx: z.boolean().default(true),
      csv: z.boolean().default(false),
      jsonl: z.boolean().default(false),
    }),
  }),
  general: z.object({
    emulator: z.string().default("bluestacks"),
    bluestacks: z.object({
      name: z.string().default("RoK Tracker"),
      config: z
        .string()
        .default("C:\\ProgramData\\BlueStacks_nxt\\bluestacks.conf"),
    }),
    adb_port: z.number().int().default(5555),
  }),
});
export type FullConfig = z.infer<typeof FullConfigSchema>;
