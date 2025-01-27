<template>
  <q-card bordered flat>
    <q-card-section horizontal>
      <q-card-section> {{ scanId }} </q-card-section>

      <q-separator vertical inset />
      <q-card-section> {{ statusMessage }} </q-card-section>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
defineProps<{
  scanId: string
  statusMessage: string
}>()
</script>
