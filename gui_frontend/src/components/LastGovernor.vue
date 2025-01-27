<template>
  <q-card bordered flat>
    <q-card-section>
      <div class="text-h6">{{ kingdomStore.lastGovernor.name }}</div>
      <div class="text-subtitle2">with id {{ kingdomStore.lastGovernor.id }}</div>
    </q-card-section>

    <q-separator />

    <q-card-section>
      <q-list dense>
        <q-item>
          <q-item-section>Power</q-item-section>
          <q-item-section side>{{ formatNumber(kingdomStore.lastGovernor.power) }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Killpoints</q-item-section>
          <q-item-section side>{{
            formatNumber(kingdomStore.lastGovernor.killpoints)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Alliance</q-item-section>
          <q-item-section side>{{ kingdomStore.lastGovernor.alliance }}</q-item-section>
        </q-item>
        <q-separator />
        <q-item>
          <q-item-section>T1 Kills</q-item-section>
          <q-item-section side>{{
            formatNumber(kingdomStore.lastGovernor.t1_kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>T2 Kills</q-item-section>
          <q-item-section side>{{
            formatNumber(kingdomStore.lastGovernor.t2_kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>T3 Kills</q-item-section>
          <q-item-section side>{{
            formatNumber(kingdomStore.lastGovernor.t3_kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>T4 Kills</q-item-section>
          <q-item-section side>{{
            formatNumber(kingdomStore.lastGovernor.t4_kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>T5 Kills</q-item-section>
          <q-item-section side>{{
            formatNumber(kingdomStore.lastGovernor.t5_kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Ranged Points</q-item-section>
          <q-item-section side>{{
            formatNumber(kingdomStore.lastGovernor.ranged_points)
          }}</q-item-section>
        </q-item>
        <q-separator />
        <q-item>
          <q-item-section>Deaths</q-item-section>
          <q-item-section side>{{ formatNumber(kingdomStore.lastGovernor.dead) }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Assisted</q-item-section>
          <q-item-section side>{{
            formatNumber(kingdomStore.lastGovernor.rss_assistance)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Gathered</q-item-section>
          <q-item-section side>{{
            formatNumber(kingdomStore.lastGovernor.rss_gathered)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Helps</q-item-section>
          <q-item-section side>{{ formatNumber(kingdomStore.lastGovernor.helps) }}</q-item-section>
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
          <div class="column">
            <div class="text-center">
              {{ kingdomStore.status.current_governor }} of
              {{ kingdomStore.status.target_governor }}
            </div>
            <div class="text-center">
              {{ kingdomStore.status.skipped_governors }}
              {{ kingdomStore.status.skipped_governors === 1 ? 'skip' : 'skips' }}
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
          :value="kingdomStore.status.current_governor / kingdomStore.status.target_governor"
          rounded
          class="q-mt-sm"
        />
      </div>
    </q-card-section>
  </q-card>
</template>
<script setup lang="ts">
import { useKingdomStore } from 'src/stores/kingdom-store'

import { UseTimeAgo } from '@vueuse/components'
import { useDateFormat } from '@vueuse/core'
import { computed } from 'vue'

const kingdomStore = useKingdomStore()

const lastUpdate = computed(() => new Date(kingdomStore.status.current_time))
const expectedFinish = computed(
  () => new Date(lastUpdate.value.getTime() + kingdomStore.status.remaining_sec * 1000),
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
