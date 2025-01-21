interface PywebviewApi {
  TestPython(): void
  // Add other pywebview methods here as needed
}

declare interface Window {
  pywebview: {
    api: PywebviewApi
  }
}
