import { defineStore, acceptHMRUpdate } from 'pinia'
import type { FullConfig } from 'src/schema/FullConfig'
import type { ScanPreset } from 'src/schema/ScanPreset'
import { ref } from 'vue'

export const useConfigStore = defineStore('configStore', () => {
  const config = ref<FullConfig>({
    scan: {
      kingdom_name: '',
      people_to_scan: 300,
      resume: false,
      advanced_scroll: true,
      track_inactives: false,
      validate_power: false,
      power_threshold: 100000,
      validate_kills: true,
      reconstruct_kills: true,
      timings: {
        gov_open: 2,
        copy_wait: 0.2,
        kills_open: 1,
        info_open: 1,
        info_close: 0.5,
        gov_close: 1,
        max_random: 0.5,
      },
      formats: {
        xlsx: true,
        csv: false,
        jsonl: false,
      },
    },
    general: {
      emulator: 'bluestacks',
      bluestacks: {
        name: 'RoK Tracker',
        config: 'C:\\ProgramData\\BlueStacks_nxt\\bluestacks.conf',
      },
      adb_port: 5555,
    },
  })

  const selectedKingdomOptions = ref<ScanPreset>({
    name: 'Full',
    selections: [
      'ID',
      'Name',
      'Power',
      'Killpoints',
      'Alliance',
      'T1 Kills',
      'T2 Kills',
      'T3 Kills',
      'T4 Kills',
      'T5 Kills',
      'Ranged',
      'Deaths',
      'Assistance',
      'Gathered',
      'Helps',
    ],
  })

  return {
    config,
    selectedKingdomOptions,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useConfigStore, import.meta.hot))
}
