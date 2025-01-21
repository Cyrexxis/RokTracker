<template>
  <q-card bordered flat>
    <q-card-section horizontal>
      <q-card-section> {{ kingdomStore.scanID }} </q-card-section>

      <q-separator vertical inset />
      <q-card-section> {{ kingdomStore.statusMessage }} </q-card-section>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { useKingdomStore } from 'src/stores/kingdom-scanner-store'

const kingdomStore = useKingdomStore()
</script>
