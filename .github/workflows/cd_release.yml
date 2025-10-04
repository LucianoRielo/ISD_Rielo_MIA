name: CD Release Pipeline

on:
  create:
    tags:
      - 'v*.*.*' # Trigger cuando se crea un tag que comienza con 'v' (ej. v1.0.0)

jobs:
  create-github-release:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Create Release
      id: create_release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }} # Token automático para interactuar con la API de GitHub
      with:
        tag_name: ${{ github.ref_name }}
        release_name: Release ${{ github.ref_name }}
        body: |
          Nueva versión liberada: ${{ github.ref }}
          Este release fue generado automáticamente por el pipeline de CD.
        draft: false
        prerelease: false
