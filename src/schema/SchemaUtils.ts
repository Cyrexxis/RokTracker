import { z } from 'zod'
import { ScanPresetSchema } from './ScanPreset'

export const KingdomPresetListSchema = z.array(ScanPresetSchema)
export type KingdomPresetList = z.infer<typeof KingdomPresetListSchema>
