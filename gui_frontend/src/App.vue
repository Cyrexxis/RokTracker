<template>
  <q-layout view="hHh lpR fFf">
    <q-header class="bg-primary text-white" height-hint="98">
      <q-toolbar>
        <q-toolbar-title>
          <q-avatar>
            <img src="https://cdn.quasar.dev/logo-v2/svg/logo-mono-white.svg" />
          </q-avatar>
          RoK Tracker Suite
        </q-toolbar-title>
        <!-- <q-toggle v-model="blueModel" color="grey" unchecked-icon="clear" checked-icon="check" /> -->
        <q-btn
          round
          dense
          flat
          class="theme-toggle"
          :class="{ 'theme-toggle--toggled': darkMode }"
          size="lg"
          color="white"
          @click="toggleDarkMode"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
            width="1em"
            height="1em"
            fill="currentColor"
            stroke-linecap="round"
            class="theme-toggle__classic"
            viewBox="0 0 32 32"
            style="width: 70%; height: 100%"
          >
            <clipPath id="theme-toggle__classic__cutout">
              <path d="M0-5h30a1 1 0 0 0 9 13v24H0Z" />
            </clipPath>
            <g clip-path="url(#theme-toggle__classic__cutout)">
              <circle cx="16" cy="16" r="9.34" />
              <g stroke="currentColor" stroke-width="1.5">
                <path d="M16 5.5v-4" />
                <path d="M16 30.5v-4" />
                <path d="M1.5 16h4" />
                <path d="M26.5 16h4" />
                <path d="m23.4 8.6 2.8-2.8" />
                <path d="m5.7 26.3 2.9-2.9" />
                <path d="m5.8 5.8 2.8 2.8" />
                <path d="m23.4 23.4 2.9 2.9" />
              </g>
            </g>
          </svg>
        </q-btn>
      </q-toolbar>
    </q-header>
    <q-page-container>
      <q-splitter v-model="splitterModel" unit="px" disable>
        <template v-slot:before>
          <div class="flex-center full-height">
            <q-tabs vertical align="center">
              <q-route-tab name="scanner" to="/scanner" label="Scanners" />
              <q-route-tab name="calculator" to="/calculator" label="Calculators" />
              <q-route-tab name="settings" to="/settings" label="Settings" />
            </q-tabs>
          </div>
        </template>
        <template v-slot:after>
          <router-view v-slot="{ Component, route }">
            <!--  default mode would be better, but strange css bug  -->
            <transition
              :enter-active-class="route.meta.transitionIn as string"
              :leave-active-class="route.meta.transitionOut as string"
              mode="out-in"
            >
              <keep-alive>
                <component :is="Component" />
              </keep-alive>
            </transition>
          </router-view>
        </template>
      </q-splitter>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useConfigStore } from './stores/config-store'
import { FullConfigSchema } from './schema/FullConfig'
import { BatchGovernorDataListSchema, KingdomPresetListSchema } from './schema/SchemaUtils'
import { BatchTypeSchema } from './schema/BatchType'
import { useAllianceStore } from './stores/alliance-store'
import { BatchAdditionalDataSchema } from './schema/BatchAdditionalData'
import { useHonorStore } from './stores/honor-store'
import { useSeedStore } from './stores/seed-store'

const configStore = useConfigStore()
const allianceStore = useAllianceStore()
const honorStore = useHonorStore()
const seedStore = useSeedStore()

const $q = useQuasar()
// import themeToggleIcon from 'assets/theme-toggle.svg'
const splitterModel = ref(120)
const darkMode = ref($q.dark.isActive)

const toggleDarkMode = () => {
  darkMode.value = !darkMode.value
  $q.dark.set(darkMode.value)
}

window.addEventListener('pywebviewready', async () => {
  try {
    const loadedConfig = await window.pywebview.api.LoadFullConfig()
    console.log(loadedConfig)
    const parsedConfig = FullConfigSchema.safeParse(JSON.parse(loadedConfig))

    if (parsedConfig.success) {
      configStore.config = parsedConfig.data
    }

    const loadedPresets = await window.pywebview.api.LoadScanPresets()
    console.log(loadedPresets)
    const parsedPresets = KingdomPresetListSchema.safeParse(JSON.parse(loadedPresets))

    if (parsedPresets.success && parsedPresets.data.length > 0) {
      configStore.availableScanPresets = parsedPresets.data
    }
  } catch (e) {
    console.error(e)
  } finally {
    window.pywebview.api.WindowReady()
  }
})

const setScanId = (id: string, batchType: string) => {
  const parsedBatchType = BatchTypeSchema.safeParse(JSON.parse(batchType))

  if (parsedBatchType.success) {
    switch (parsedBatchType.data.type) {
      case 'Alliance':
        allianceStore.scanID = id
        break
      case 'Honor':
        honorStore.scanID = id
        break
      case 'Seed':
        seedStore.scanID = id
        break
      default:
        break
    }
  }
}

const governorUpdate = (governorData: string, extraData: string, batchType: string) => {
  const parsedBatchType = BatchTypeSchema.safeParse(JSON.parse(batchType))
  if (parsedBatchType.success) {
    switch (parsedBatchType.data.type) {
      case 'Alliance':
        allianceStore.lastGovernor = BatchGovernorDataListSchema.parse(JSON.parse(governorData))
        allianceStore.status = BatchAdditionalDataSchema.parse(JSON.parse(extraData))
        break
      case 'Honor':
        honorStore.lastGovernor = BatchGovernorDataListSchema.parse(JSON.parse(governorData))
        honorStore.status = BatchAdditionalDataSchema.parse(JSON.parse(extraData))
        break
      case 'Seed':
        seedStore.lastGovernor = BatchGovernorDataListSchema.parse(JSON.parse(governorData))
        seedStore.status = BatchAdditionalDataSchema.parse(JSON.parse(extraData))
        break
      default:
        break
    }
  }
}

const stateUpdate = (state: string, batchType: string) => {
  const parsedBatchType = BatchTypeSchema.safeParse(JSON.parse(batchType))

  if (parsedBatchType.success) {
    switch (parsedBatchType.data.type) {
      case 'Alliance':
        allianceStore.statusMessage = state
        break
      case 'Honor':
        honorStore.statusMessage = state
        break
      case 'Seed':
        seedStore.statusMessage = state
        break
      default:
        break
    }
  }
}

const askConfirm = (message: string, batchType: string) => {
  const parsedBatchType = BatchTypeSchema.safeParse(JSON.parse(batchType))

  if (parsedBatchType.success) {
    $q.dialog({
      title: 'Confirm',
      message,
      ok: 'Yes',
      cancel: 'No',
      persistent: true,
    })
      .onOk(() => {
        window.pywebview.api.ConfirmCallbackBatch(true, JSON.stringify(parsedBatchType.data))
      })
      .onCancel(() => {
        window.pywebview.api.ConfirmCallbackBatch(false, JSON.stringify(parsedBatchType.data))
      })
  }
}

const scanFinished = (batchType: string) => {
  const parsedBatchType = BatchTypeSchema.safeParse(JSON.parse(batchType))

  if (parsedBatchType.success) {
    switch (parsedBatchType.data.type) {
      case 'Alliance':
        allianceStore.scanRunning = false
        allianceStore.startButtonDisabled = false
        break
      case 'Honor':
        honorStore.scanRunning = false
        honorStore.startButtonDisabled = false
        break
      case 'Seed':
        seedStore.scanRunning = false
        seedStore.startButtonDisabled = false
        break
      default:
        break
    }
  }
}

window.batch = {
  setScanID: setScanId,
  batchUpdate: governorUpdate,
  stateUpdate: stateUpdate,
  askConfirm: askConfirm,
  scanFinished: scanFinished,
}
</script>

<style lang="css" scoped></style>
