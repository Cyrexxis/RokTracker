<template>
  <div class="row no-wrap q-gutter-x-md">
    <div class="col-8 column">
      <div class="row q-gutter-x-md">
        <div class="col-4 q-gutter-y-sm column">
          <q-select
            outlined
            v-model="selectedPreset"
            :options="scanPresets"
            label="Scan Preset"
            stack-label
            :display-value="selectedPreset!.name"
            @update:model-value="settings.selectedInfo = selectedPreset?.selections ?? []"
            :disable="scanRunning"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>{{ scope.opt.name }}</q-item-section>
              </q-item>
            </template>
          </q-select>
          <q-tree
            :nodes="computedInfoToScan"
            v-model:ticked="settings.selectedInfo"
            node-key="label"
            tick-strategy="leaf"
            default-expand-all
            dense
            :disable="scanRunning"
          />
          <q-btn
            label="Save as Preset"
            color="primary"
            @click="handleClick"
            :disable="scanRunning"
          />
          <div class="row column">
            <q-btn
              :label="scanRunning ? 'Stop Scan' : 'Start Scan'"
              :color="scanRunning ? 'negative' : 'primary'"
              @click="handleMainButtonClick"
            />
          </div>
        </div>
        <div class="col column">
          <q-form class="q-gutter-y-sm">
            <div class="row q-gutter-x-sm">
              <q-input
                class="col"
                outlined
                v-model="settings.scanName"
                label="Scan name"
                hint="This will get prepended to the file name"
                :disable="scanRunning"
              />
              <q-select
                class="col"
                v-model="settings.outputFormatsSelected"
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
                v-model="settings.emulatorName"
                label="Emulator name"
                hint="Works only for BlueStacks"
                :disable="scanRunning"
              />
              <q-input
                class="col"
                outlined
                v-model="settings.adbPort"
                label="ADB Port of emulator"
                :rules="intRule"
                hint="Should be autofilled if emulator is found"
                :disable="scanRunning"
              />
            </div>

            <q-input
              outlined
              v-model="settings.scanAmount"
              label="How many people to scan"
              hint="The amount of people you want to scan"
              :rules="intRule"
              :disable="scanRunning"
            />
            <q-toggle
              v-model="settings.continuedScan"
              label="Start at 4th governor"
              :disable="scanRunning"
            />
            <q-toggle
              v-model="settings.betterScroll"
              label="Better Scrolling"
              :disable="scanRunning"
            />
            <q-toggle
              v-model="settings.trackInactives"
              label="Track inactives"
              :disable="scanRunning"
            />
            <q-toggle
              v-model="settings.validateKills"
              label="Validate kills"
              :disable="scanRunning"
            />
            <q-toggle
              v-model="settings.reconstructKills"
              label="Reconstruct kills"
              :disable="scanRunning || !settings.validateKills"
            />
            <div class="row q-gutter-x-sm">
              <q-toggle
                class="col"
                v-model="settings.validatePower"
                label="Validate Power"
                :disable="scanRunning"
              />
              <q-input
                class="col-8"
                outlined
                v-model="settings.powerTolerance"
                label="Power tolarance"
                :rules="floatRule"
                hint="Acceptable power in wrong direction"
                :disable="scanRunning || !settings.validatePower"
              />
            </div>

            <div class="row q-gutter-x-sm">
              <q-input
                class="col"
                outlined
                v-model="settings.moreInfoWait"
                label="Wait after more info (in s)"
                :rules="floatRule"
                hint="Delay after clicking more info"
                :disable="scanRunning"
              />
              <q-input
                class="col"
                outlined
                v-model="settings.governorWait"
                label="Wait after governor open (in s)"
                :rules="floatRule"
                hint="Delay after opening governor"
                :disable="scanRunning"
              />
            </div>

            <q-input
              outlined
              v-model="settings.governorRandom"
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
      <ScanStatus class="col-auto" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import LastGovernor from './LastGovernor.vue'
import { intRule, floatRule, notEmptyArrayRule } from 'src/util/rules'
import type { KingdomScanSettings } from 'src/types/KingdomScanSettings'
import type { KingdomPreset } from 'src/types/KingdomPreset'
import ScanStatus from './ScanStatus.vue'
import { useKingdomStore } from 'src/stores/kingdom-scanner-store'
import { useQuasar } from 'quasar'

const $q = useQuasar()

const kingdomStore = useKingdomStore()

const scanRunning = ref(false)

const scanPresets: KingdomPreset[] = [
  {
    name: 'Full',
    selections: [
      'ID',
      'Name',
      'Power',
      'Killpoints',
      'Alliance',
      'T1 Kills',
      'T2 Kills',
      'T3 Kills',
      'T4 Kills',
      'T5 Kills',
      'Ranged',
      'Deaths',
      'Assistance',
      'Gathered',
      'Helps',
    ],
  },
  { name: 'Seed', selections: ['ID', 'Name', 'Power', 'Killpoints', 'Alliance'] },
]

const handleClick = () => {
  console.log('clicked')
  console.log(JSON.stringify(settings.value))
}

const selectedPreset = ref(scanPresets[0])

const settings = ref<KingdomScanSettings>({
  scanName: '',
  emulatorName: '',
  adbPort: '5555',
  scanAmount: '',
  continuedScan: false,
  betterScroll: true,
  trackInactives: true,
  validateKills: true,
  reconstructKills: true,
  validatePower: true,
  powerTolerance: '1000000',
  moreInfoWait: '1',
  governorWait: '1',
  governorRandom: '0.5',
  outputFormatsSelected: [
    {
      label: 'Excel',
      value: 'xlsx',
      display: 'xlsx',
    },
  ],
  selectedInfo: scanPresets[0]?.selections ?? [],
})

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
  scanRunning.value = !scanRunning.value
  console.log('clicked')
  window.pywebview.api.TestPython()
}

const setScanId = (id: string) => {
  settings.value.scanName = id
}

const governorUpdate = (governorData: string) => {
  console.log(governorData)
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

window.kingdom = {
  setScanID: setScanId,
  governorUpdate: governorUpdate,
  stateUpdate: stateUpdate,
  askConfirm: askConfirm,
}
</script>
