<template>
  <q-page>
    <q-tabs v-model="tab" align="justify">
      <q-tab name="kingdom" label="Kingdom" />
      <q-tab name="seed" label="Seed" />
      <q-tab name="honor" label="Honor" />
      <q-tab name="alliance" label="Alliance" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="tab" animated keep-alive>
      <q-tab-panel name="kingdom">
        <KingdomScanner />
      </q-tab-panel>

      <q-tab-panel name="seed">
        <div class="text-h6">Alarms</div>
        Lorem ipsum dolor sit amet consectetur adipisicing elit.
      </q-tab-panel>

      <q-tab-panel name="honor">
        <div class="text-h6">Movies</div>
        Lorem ipsum dolor sit amet consectetur adipisicing elit.
      </q-tab-panel>

      <q-tab-panel name="alliance">
        <div class="text-h6">Movies</div>
        Lorem ipsum dolor sit amet consectetur adipisicing elit.
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import KingdomScanner from 'src/components/KingdomScanner.vue'

const tab = ref('kingdom')
</script>
