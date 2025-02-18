interface PywebviewApi {
  WindowReady(): void
  //--------------------------------
  StartKingdomScan(full_config: string, scan_preset: string): void
  StopKingdomScan(): void
  ConfirmCallback(confirm: boolean): void
  //--------------------------------
  StartBatchScan(full_config: string, batch_type: string): void
  StopBatchScan(batch_type: string): void
  ConfirmCallbackBatch(confirm: boolean, batch_type: string): void
  //--------------------------------
  TestPython(): void
  //--------------------------------
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

interface BatchApi {
  setScanID(id: string, batchType: string): void
  batchUpdate(governorData: string, extraData: string, batchType: string): void
  stateUpdate(state: string, batchType: string): void
  askConfirm(message: string, batchType: string): void
  scanFinished(batchType: string): void
}

declare interface Window {
  pywebview: {
    api: PywebviewApi
  }
  kingdom: KingdomApi
  batch: BatchApi
}
