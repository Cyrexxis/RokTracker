<template>
  <q-page class="column">
    <q-tabs v-model="tab" align="justify" class="col-auto">
      <q-tab name="kingdom" label="Kingdom" />
      <q-tab name="seed" label="Seed" />
      <q-tab name="honor" label="Honor" />
      <q-tab name="alliance" label="Alliance" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="tab" animated keep-alive class="col">
      <q-tab-panel name="kingdom">
        <KingdomScanner />
      </q-tab-panel>

      <q-tab-panel name="seed">
        <SeedScanner />
      </q-tab-panel>

      <q-tab-panel name="honor">
        <HonorScanner />
      </q-tab-panel>

      <q-tab-panel name="alliance">
        <AllianceScanner />
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import KingdomScanner from 'src/components/KingdomScanner.vue'
import AllianceScanner from 'src/components/AllianceScanner.vue'
import HonorScanner from 'src/components/HonorScanner.vue'
import SeedScanner from 'src/components/SeedScanner.vue'

const tab = ref('kingdom')
</script>
