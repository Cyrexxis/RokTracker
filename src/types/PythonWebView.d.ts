interface PywebviewApi {
  StartKingdomScan(full_config: string, scan_preset: string): void
  TestPython(): void
  ConfirmCallback(confirm: boolean): void
}

interface KingdomApi {
  setScanID(id: string): void
  governorUpdate(governorData: string): void
  stateUpdate(state: string): void
  askConfirm(message: string): void
}

declare interface Window {
  pywebview: {
    api: PywebviewApi
  }
  kingdom: KingdomApi
}
