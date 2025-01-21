export interface KingdomScanSettings {
  scanName: string
  emulatorName: string
  adbPort: string
  scanAmount: string
  continuedScan: boolean
  betterScroll: boolean
  trackInactives: boolean
  validateKills: boolean
  reconstructKills: boolean
  validatePower: boolean
  powerTolerance: string
  moreInfoWait: string
  governorWait: string
  governorRandom: string
  outputFormatsSelected: { label: string; value: string; display: string }[]
  selectedInfo: string[]
}
