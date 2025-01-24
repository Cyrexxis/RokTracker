import { defineStore, acceptHMRUpdate } from 'pinia'
import type { KingdomAdditionalData } from 'src/schema/KingdomAdditionalData'
import type { KingdomGovernorData } from 'src/schema/KingdomGovernorData'
import { ref } from 'vue'

export const useKingdomStore = defineStore('kingdom', () => {
  const lastGovernor = ref<KingdomGovernorData>({
    name: 'Super Awesome Governor',
    id: 123456,
    power: 1000000,
    killpoints: 1000000,
    alliance: 'Greatest Alliance Ever',
    t1_kills: 1000000,
    t2_kills: 1000000,
    t3_kills: 1000000,
    t4_kills: 1000000,
    t5_kills: 1000000,
    t1_kp: 200000, // 20% of t1 kills
    t2_kp: 2000000, // 2x t2 kills
    t3_kp: 4000000, // 4x t3 kills
    t4_kp: 10000000, // 10x t4 kills
    t5_kp: 20000000, // 20x t5 kills
    t45_kills: 2000000, // t4 + t5 kills
    total_kills: 5000000, // sum of all kills
    ranged_points: 1000000,
    dead: 1000000,
    rss_assistance: 1000000,
    rss_gathered: 1000000,
    helps: 1000000,
  })

  const status = ref<KingdomAdditionalData>({
    current_governor: 150,
    target_governor: 300,
    skipped_governors: 10,
    power_ok: 'Not Checked',
    kills_ok: 'Not Checked',
    reconstruction_success: 'Not Checked',
    remaining_sec: 300,
    current_time: new Date().toISOString(),
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
