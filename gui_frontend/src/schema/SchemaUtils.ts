import { z } from 'zod'
import { ScanPresetSchema } from './ScanPreset'
import { BatchGovernorDataSchema } from './BatchGovernorData'

export const KingdomPresetListSchema = z.array(ScanPresetSchema)
export type KingdomPresetList = z.infer<typeof KingdomPresetListSchema>

export const BatchGovernorDataListSchema = z.array(BatchGovernorDataSchema)
export type BatchGovernorDataList = z.infer<typeof BatchGovernorDataListSchema>
