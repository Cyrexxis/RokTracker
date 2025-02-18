<template>
  <div class="row col-auto no-wrap q-gutter-x-md flex-center">
    <div class="col-8 column">
      <div class="row q-gutter-x-md">
        <div class="col column">
          <q-form class="q-gutter-y-sm column">
            <div class="row q-gutter-x-sm">
              <q-input
                class="col"
                outlined
                v-model="configStore.config.scan.kingdom_name"
                label="Scan name"
                hint="This will get prepended to the file name"
                :disable="scanRunning"
              />
              <q-select
                class="col"
                v-model="selectedOutputs"
                multiple
                :options="outputFormats"
                label="Output formats"
                outlined
                hint="The format you want"
                :rules="notEmptyArrayRule"
                :disable="scanRunning"
              >
                <template v-slot:selected-item="scope">
                  <q-chip
                    removable
                    dense
                    @remove="scope.removeAtIndex(scope.index)"
                    :tabindex="scope.tabindex"
                    class="q-px-sm"
                    outline
                  >
                    {{ scope.opt.display }}
                  </q-chip>
                </template>
              </q-select>
            </div>

            <div class="row q-gutter-x-sm">
              <q-input
                class="col"
                outlined
                v-model="configStore.config.general.bluestacks.name"
                label="Emulator name"
                hint="Works only for BlueStacks"
                :disable="scanRunning"
              />
              <q-input
                class="col"
                outlined
                v-model="configStore.config.general.adb_port"
                label="ADB Port of emulator"
                :rules="intRule"
                hint="Should be autofilled if emulator is found"
                :disable="scanRunning"
              />
            </div>

            <q-input
              outlined
              v-model="configStore.config.scan.people_to_scan"
              label="How many people to scan"
              hint="The amount of people you want to scan"
              :rules="intRule"
              :disable="scanRunning"
            />

            <q-input
              outlined
              v-model="configStore.config.scan.timings.max_random"
              label="Maximum random delay (in s)"
              :rules="floatRule"
              hint="A random delay is added to the wait times, this is the maximum"
              :disable="scanRunning"
            />

            <q-btn
              :label="
                startButtonDisabled ? 'Stopping...' : scanRunning ? 'Stop Scan' : 'Start Scan'
              "
              :color="scanRunning ? 'negative' : 'primary'"
              @click="handleMainButtonClick"
              :disable="startButtonDisabled"
            />
          </q-form>
        </div>
      </div>
    </div>
    <div class="col column justify-between q-gutter-y-sm">
      <div class="row col">
        <LastBatch
          class="col"
          :batchData="honorStore.lastGovernor"
          :batchStatus="honorStore.status"
        />
      </div>
      <ScanStatus
        class="col-auto"
        :scan-id="honorStore.scanID"
        :status-message="honorStore.statusMessage"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { intRule, floatRule, notEmptyArrayRule } from 'src/util/rules'
import type { OutputFormat } from 'src/types/OutputFormats'
import ScanStatus from './ScanStatus.vue'
import { useConfigStore } from 'src/stores/config-store'
import LastBatch from './LastBatch.vue'
import type { BatchType } from 'src/schema/BatchType'
import { useHonorStore } from 'src/stores/honor-store'

const honorStore = useHonorStore()
const configStore = useConfigStore()
const { scanRunning, startButtonDisabled } = storeToRefs(honorStore)

const batchType: BatchType = { type: 'Honor' }

const outputFormats = ref([
  {
    label: 'Excel (xlsx)',
    value: 'xlsx',
    display: 'xlsx',
  },
  {
    label: 'Comma Seperated Values (csv)',
    value: 'csv',
    display: 'csv',
  },
  {
    label: 'JSON Lines (jsonl)',
    value: 'jsonl',
    display: 'jsonl',
  },
])

const selectedOutputs = ref<OutputFormat[]>([
  {
    label: 'Excel',
    value: 'xlsx',
    display: 'xlsx',
  },
])

watch(selectedOutputs, (newVal) => {
  configStore.config.scan.formats.csv = newVal.some((format) => format.value === 'csv')
  configStore.config.scan.formats.jsonl = newVal.some((format) => format.value === 'jsonl')
  configStore.config.scan.formats.xlsx = newVal.some((format) => format.value === 'xlsx')
})

const handleMainButtonClick = () => {
  if (!scanRunning.value) {
    window.pywebview.api.StartBatchScan(
      JSON.stringify(configStore.config),
      JSON.stringify(batchType),
    )

    scanRunning.value = !scanRunning.value
  } else {
    window.pywebview.api.StopBatchScan(JSON.stringify(batchType))
    startButtonDisabled.value = true
  }
}
</script>
