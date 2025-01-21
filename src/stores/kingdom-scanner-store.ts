import { defineStore, acceptHMRUpdate } from 'pinia'
import type { KingdomGovernorResult } from 'src/types/GovernorResult'
import type { ScanStatus } from 'src/types/ScanStatus'
import { ref } from 'vue'

export const useKingdomStore = defineStore('kingdom', () => {
  const lastGovernor = ref<KingdomGovernorResult>({
    name: 'Super Awsome Governor',
    id: 123456,
    power: 1000000,
    killpoints: 1000000,
    alliance: 'Greatest Alliance Ever',
    t1Kills: 1000000,
    t2Kills: 1000000,
    t3Kills: 1000000,
    t4Kills: 1000000,
    t5Kills: 1000000,
    rangedPoints: 1000000,
    deaths: 1000000,
    assists: 1000000,
    gathered: 1000000,
    helps: 1000000,
  })

  const status = ref<ScanStatus>({
    currentGovernor: 20,
    maxGovernor: 200,
    skippedGovernors: 3,
    lastUpdate: new Date(),
    expectedFinish: new Date(),
  })

  const scanID = ref('Scan id')

  const statusMessage = ref('Not yet started')

  return {
    lastGovernor,
    status,
    statusMessage,
    scanID,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useKingdomStore, import.meta.hot))
}
