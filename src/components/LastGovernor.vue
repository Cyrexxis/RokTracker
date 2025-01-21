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
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.power)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Killpoints</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.killpoints)
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
            Intl.NumberFormat().format(kingdomStore.lastGovernor.t1Kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>T2 Kills</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.t2Kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>T3 Kills</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.t3Kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>T4 Kills</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.t4Kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>T5 Kills</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.t5Kills)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Ranged Points</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.rangedPoints)
          }}</q-item-section>
        </q-item>
        <q-separator />
        <q-item>
          <q-item-section>Deaths</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.deaths)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Assisted</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.assists)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Gathered</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.gathered)
          }}</q-item-section>
        </q-item>
        <q-item>
          <q-item-section>Helps</q-item-section>
          <q-item-section side>{{
            Intl.NumberFormat().format(kingdomStore.lastGovernor.helps)
          }}</q-item-section>
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
              ><UseTimeAgo v-slot="{ timeAgo }" :time="kingdomStore.status.lastUpdate">
                {{ timeAgo }}
              </UseTimeAgo>
            </div>
          </div>
          <div class="column">
            <div class="text-center">
              {{ kingdomStore.status.currentGovernor }} of {{ kingdomStore.status.maxGovernor }}
            </div>
            <div class="text-center">
              {{ kingdomStore.status.skippedGovernors }}
              {{ kingdomStore.status.skippedGovernors === 1 ? 'skip' : 'skips' }}
            </div>
          </div>
          <div class="column">
            <div class="text-right">Expected Finish</div>
            <div class="text-right">
              <q-tooltip anchor="bottom right" self="top right" :offset="[10, 10]">
                {{ expectedFinishFormatted }} </q-tooltip
              ><UseTimeAgo v-slot="{ timeAgo }" :time="kingdomStore.status.expectedFinish">
                {{ timeAgo }}
              </UseTimeAgo>
            </div>
          </div>
        </div>
        <q-linear-progress
          :value="kingdomStore.status.currentGovernor / kingdomStore.status.maxGovernor"
          rounded
          class="q-mt-sm"
        />
      </div>
    </q-card-section>
  </q-card>
</template>
<script setup lang="ts">
import { useKingdomStore } from 'src/stores/kingdom-scanner-store'

import { UseTimeAgo } from '@vueuse/components'
import { useDateFormat } from '@vueuse/core'

const kingdomStore = useKingdomStore()

const lastUpdateFormatted = useDateFormat(kingdomStore.status.lastUpdate, 'HH:mm:ss')
const expectedFinishFormatted = useDateFormat(kingdomStore.status.expectedFinish, 'HH:mm:ss')
</script>

<style scoped>
.q-item {
  min-height: 24px;
}

.q-list .q-separator {
  margin: 3px 0;
}
</style>
