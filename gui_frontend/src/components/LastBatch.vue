<template>
  <q-card bordered flat>
    <q-card-section>
      <div class="text-h6">Screen {{ allianceStore.status.current_page }}</div>
      <div class="text-subtitle2">
        of {{ allianceStore.status.target_governor / allianceStore.status.govs_per_page }}
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section>
      <q-list dense>
        <q-item v-for="gov in allianceStore.lastGovernor" :key="gov.img_path">
          <q-item-section>{{ gov.name }}</q-item-section>
          <q-item-section side>{{ formatNumber(gov.score) }}</q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
    <q-separator />
    <q-card-section>
      <div class="column">
        <div class="row justify-between">
          <div class="column">
            <div class="text-left">Last Update</div>
            <div class="text-left">
              <q-tooltip anchor="bottom left" self="top left" :offset="[10, 10]">
                {{ lastUpdateFormatted }} </q-tooltip
              ><UseTimeAgo v-slot="{ timeAgo }" :time="lastUpdate">
                {{ timeAgo }}
              </UseTimeAgo>
            </div>
          </div>
          <div class="column justify-center">
            <div class="text-center col-auto">
              {{ allianceStore.status.current_page * allianceStore.status.govs_per_page }} of
              {{ allianceStore.status.target_governor }}
            </div>
          </div>
          <div class="column">
            <div class="text-right">Expected Finish</div>
            <div class="text-right">
              <q-tooltip anchor="bottom right" self="top right" :offset="[10, 10]">
                {{ expectedFinishFormatted }} </q-tooltip
              ><UseTimeAgo
                v-slot="{ timeAgo }"
                :time="expectedFinish"
                :show-second="true"
                :update-interval="1000"
              >
                {{ timeAgo }}
              </UseTimeAgo>
            </div>
          </div>
        </div>
        <q-linear-progress
          :value="
            (allianceStore.status.current_page * allianceStore.status.govs_per_page) /
            allianceStore.status.target_governor
          "
          rounded
          class="q-mt-sm"
        />
      </div>
    </q-card-section>
  </q-card>
</template>
<script setup lang="ts">
import { UseTimeAgo } from '@vueuse/components'
import { useDateFormat } from '@vueuse/core'
import { useAllianceStore } from 'src/stores/alliance-store'
import { computed } from 'vue'

const allianceStore = useAllianceStore()

const lastUpdate = computed(() => new Date(allianceStore.status.current_time))
const expectedFinish = computed(
  () => new Date(lastUpdate.value.getTime() + allianceStore.status.remaining_sec * 1000),
)

const lastUpdateFormatted = useDateFormat(lastUpdate, 'HH:mm:ss')
const expectedFinishFormatted = useDateFormat(expectedFinish, 'HH:mm:ss')

const formatNumber = (value: number | string) => {
  return isNaN(Number(value)) ? (value as string) : Intl.NumberFormat().format(value as number)
}
</script>

<style scoped>
.q-item {
  min-height: 24px;
}

.q-list .q-separator {
  margin: 3px 0;
}
</style>
