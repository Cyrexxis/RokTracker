<template>
  <div class="row no-wrap q-gutter-x-md">
    <div class="col-8 column">
      <div class="row q-gutter-x-md">
        <div class="col-4 q-gutter-y-sm column">
          <q-select
            outlined
            v-model="selectedPreset"
            :options="configStore.availableScanPresets"
            label="Scan Preset"
            stack-label
            :display-value="selectedPreset?.name ?? ''"
            @update:model-value="
              configStore.selectedKingdomOptions.selections = selectedPreset?.selections ?? []
            "
            :disable="scanRunning"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>{{ scope.opt.name }}</q-item-section>
              </q-item>
            </template>

            <template v-slot:append>
              <q-icon
                v-if="selectedPreset !== undefined"
                class="cursor-pointer"
                name="delete_forever"
                color="negative"
                @click.stop.prevent="handelDeletePreset"
              />
            </template>
          </q-select>
          <q-tree
            :nodes="computedInfoToScan"
            v-model:ticked="configStore.selectedKingdomOptions.selections"
            node-key="label"
            tick-strategy="leaf"
            default-expand-all
            dense
            :disable="scanRunning"
          />
          <q-btn
            label="Save as Preset"
            color="primary"
            @click="handeSavePreset"
            :disable="scanRunning"
          />
          <div class="row column">
            <q-btn
              :label="
                startButtonDisabled ? 'Stopping...' : scanRunning ? 'Stop Scan' : 'Start Scan'
              "
              :color="scanRunning ? 'negative' : 'primary'"
              @click="handleMainButtonClick"
              :disable="startButtonDisabled"
            />
          </div>
        </div>
        <div class="col column">
          <q-form class="q-gutter-y-sm">
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
            <q-toggle
              v-model="configStore.config.scan.resume"
              label="Start at 4th governor"
              :disable="scanRunning"
            />
            <q-toggle
              v-model="configStore.config.scan.advanced_scroll"
              label="Better Scrolling"
              :disable="scanRunning"
            />
            <q-toggle
              v-model="configStore.config.scan.track_inactives"
              label="Track inactives"
              :disable="scanRunning"
            />
            <q-toggle
              v-model="configStore.config.scan.validate_kills"
              label="Validate kills"
              :disable="scanRunning"
            />
            <q-toggle
              v-model="configStore.config.scan.reconstruct_kills"
              label="Reconstruct kills"
              :disable="scanRunning || !configStore.config.scan.validate_kills"
            />
            <div class="row q-gutter-x-sm">
              <q-toggle
                class="col"
                v-model="configStore.config.scan.validate_power"
                label="Validate Power"
                :disable="scanRunning"
              />
              <q-input
                class="col-8"
                outlined
                v-model="configStore.config.scan.power_threshold"
                label="Power tolarance"
                :rules="floatRule"
                hint="Acceptable power in wrong direction"
                :disable="scanRunning || !configStore.config.scan.validate_power"
              />
            </div>

            <div class="row q-gutter-x-sm">
              <q-input
                class="col"
                outlined
                v-model="configStore.config.scan.timings.info_close"
                label="Wait after more close (in s)"
                :rules="floatRule"
                hint="Delay after exiting more info"
                :disable="scanRunning"
              />
              <q-input
                class="col"
                outlined
                v-model="configStore.config.scan.timings.gov_close"
                label="Wait after governor close (in s)"
                :rules="floatRule"
                hint="Delay after exiting governor"
                :disable="scanRunning"
              />
            </div>

            <q-input
              outlined
              v-model="configStore.config.scan.timings.max_random"
              label="Maximum random delay (in s)"
              :rules="floatRule"
              hint="A random delay is added to the wait times, this is the maximum"
              :disable="scanRunning"
            />
          </q-form>
        </div>
      </div>
    </div>
    <div class="col column justify-between q-gutter-y-sm">
      <div class="row col">
        <LastGovernor class="col" />
      </div>
      <ScanStatus
        class="col-auto"
        :scan-id="kingdomStore.scanID"
        :status-message="kingdomStore.statusMessage"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import LastGovernor from './LastGovernor.vue'
import { intRule, floatRule, notEmptyArrayRule } from 'src/util/rules'
import type { OutputFormat } from 'src/types/OutputFormats'
import ScanStatus from './ScanStatus.vue'
import { useKingdomStore } from 'src/stores/kingdom-store'
import { useQuasar } from 'quasar'
import { useConfigStore } from 'src/stores/config-store'
import { KingdomGovernorDataSchema } from 'src/schema/KingdomGovernorData'
import { KingdomAdditionalDataSchema } from 'src/schema/KingdomAdditionalData'
import type { ScanPreset } from 'src/schema/ScanPreset'

const $q = useQuasar()

const kingdomStore = useKingdomStore()
const configStore = useConfigStore()

const scanRunning = ref(false)
const startButtonDisabled = ref(false)

const handeSavePreset = () => {
  $q.dialog({
    title: 'Save Preset',
    message: 'Enter a name for the preset',
    prompt: {
      model: '',
      type: 'text',
      isValid: (val) => val.length > 0,
    },
    cancel: true,
    persistent: true,
  }).onOk((val) => {
    const newPreset: ScanPreset = {
      name: val,
      selections: configStore.selectedKingdomOptions.selections,
    }

    configStore.availableScanPresets.push(newPreset)
    selectedPreset.value = newPreset

    window.pywebview.api.SaveScanPresets(JSON.stringify(configStore.availableScanPresets))
  })
}

const handelDeletePreset = () => {
  $q.dialog({
    title: 'Delete Preset',
    message: `Do you really want to delete the ${selectedPreset.value?.name} preset?`,
    ok: 'Yes',
    cancel: 'No',
    persistent: true,
  }).onOk(() => {
    configStore.availableScanPresets = configStore.availableScanPresets.filter(
      (preset) => preset.name !== selectedPreset.value?.name,
    )

    selectedPreset.value = undefined

    window.pywebview.api.SaveScanPresets(JSON.stringify(configStore.availableScanPresets))
  })
}

const selectedPreset = ref(configStore.availableScanPresets[0])

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

const infoToScan = [
  {
    label: 'Everything',
    children: [
      {
        label: 'First Screen',
        children: [
          { label: 'ID' },
          { label: 'Name' },
          { label: 'Power' },
          { label: 'Killpoints' },
          { label: 'Alliance' },
        ],
      },
      {
        label: 'Second Screen',
        children: [
          { label: 'T1 Kills' },
          { label: 'T2 Kills' },
          { label: 'T3 Kills' },
          { label: 'T4 Kills' },
          { label: 'T5 Kills' },
          { label: 'Ranged' },
        ],
      },
      {
        label: 'Third Screen',
        children: [
          { label: 'Deaths' },
          { label: 'Assistance' },
          { label: 'Gathered' },
          { label: 'Helps' },
        ],
      },
    ],
  },
]

const computedInfoToScan = computed(() => {
  interface Node {
    label: string
    disabled?: boolean
    children?: Node[]
  }

  const addDisabledState = (nodes: Node[]): Node[] => {
    return nodes.map((node) => ({
      ...node,
      disabled: scanRunning.value,
      children: node.children ? addDisabledState(node.children) : [],
    }))
  }

  return addDisabledState(infoToScan)
})

const handleMainButtonClick = () => {
  if (!scanRunning.value) {
    window.pywebview.api.StartKingdomScan(
      JSON.stringify(configStore.config),
      JSON.stringify(selectedPreset.value),
    )

    scanRunning.value = !scanRunning.value
  } else {
    window.pywebview.api.StopKingdomScan()
    startButtonDisabled.value = true
  }
}

const setScanId = (id: string) => {
  kingdomStore.scanID = id
}

const governorUpdate = (governorData: string, extraData: string) => {
  kingdomStore.lastGovernor = KingdomGovernorDataSchema.parse(JSON.parse(governorData))
  kingdomStore.status = KingdomAdditionalDataSchema.parse(JSON.parse(extraData))
}

const stateUpdate = (state: string) => {
  kingdomStore.statusMessage = state
}

const askConfirm = (message: string) => {
  $q.dialog({
    title: 'Confirm',
    message,
    ok: 'Yes',
    cancel: 'No',
    persistent: true,
  })
    .onOk(() => {
      window.pywebview.api.ConfirmCallback(true)
    })
    .onCancel(() => {
      window.pywebview.api.ConfirmCallback(false)
    })
}

const scanFinished = () => {
  scanRunning.value = false
  startButtonDisabled.value = false
}

window.kingdom = {
  setScanID: setScanId,
  governorUpdate: governorUpdate,
  stateUpdate: stateUpdate,
  askConfirm: askConfirm,
  scanFinished: scanFinished,
}
</script>
