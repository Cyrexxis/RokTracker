import { defineStore, acceptHMRUpdate } from 'pinia'
import type { BatchAdditionalData } from 'src/schema/BatchAdditionalData'
import type { BatchGovernorData } from 'src/schema/BatchGovernorData'
import { ref } from 'vue'

export const useAllianceStore = defineStore('alliance', () => {
  const lastGovernor = ref<BatchGovernorData[]>([
    {
      name: 'Governor 1',
      img_path: '',
      score: 400,
    },
    {
      name: 'Governor 2',
      img_path: '',
      score: 400,
    },
    {
      name: 'Governor 3',
      img_path: '',
      score: 400,
    },
    {
      name: 'Governor 4',
      img_path: '',
      score: 400,
    },
    {
      name: 'Governor 5',
      img_path: '',
      score: 400,
    },
  ])

  const status = ref<BatchAdditionalData>({
    current_page: 1,
    govs_per_page: 5,
    target_governor: 20,
    remaining_sec: 0,
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
  import.meta.hot.accept(acceptHMRUpdate(useAllianceStore, import.meta.hot))
}
