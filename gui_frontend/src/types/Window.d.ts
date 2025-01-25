interface PywebviewApi {
  WindowReady(): void
  StartKingdomScan(full_config: string, scan_preset: string): void
  StopKingdomScan(): void
  TestPython(): void
  ConfirmCallback(confirm: boolean): void
  LoadFullConfig(): Promise<string>
  LoadScanPresets(): Promise<string>
  SaveScanPresets(presets: string): void
}

interface KingdomApi {
  setScanID(id: string): void
  governorUpdate(governorData: string, extraData: string): void
  stateUpdate(state: string): void
  askConfirm(message: string): void
  scanFinished(): void
}

declare interface Window {
  pywebview: {
    api: PywebviewApi
  }
  kingdom: KingdomApi
}
