<template>
  <q-page class="column">
    <q-tabs v-model="tab" align="justify" class="col-auto">
      <q-tab name="basic" label="Basic" />
      <q-tab name="advanced" label="Advanced" />
    </q-tabs>

    <q-separator />

    <q-tab-panels v-model="tab" animated class="col column justify-center">
      <q-tab-panel name="basic" class="col column flex-center">
        <PlaceholderComponent />
      </q-tab-panel>

      <q-tab-panel name="advanced" class="col column flex-center">
        <PlaceholderComponent />
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import PlaceholderComponent from 'src/components/PlaceholderComponent.vue'
import { ref } from 'vue'

const tab = ref('basic')
</script>
