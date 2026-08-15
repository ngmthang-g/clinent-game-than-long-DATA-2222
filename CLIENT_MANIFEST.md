# Client Manifest

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`
Branch: `main`

This file identifies the exact client build used by the research knowledge base. Binary-dependent conclusions should always be tied to this manifest.

## Client identity

- Client name: Than Long
- Build/version: `PENDING`
- Capture date: `PENDING`
- Source/install package: `PENDING`
- Architecture: `PENDING`
- Unity version: `PENDING`
- IL2CPP version/metadata version: `PENDING`

## Important source files

Known files currently relevant to analysis include:

- `Game/GameAssembly.dll`
- `Game/UnityPlayer.dll`
- `Game/baselib.dll`
- `Game/D3D12/D3D12Core.dll`
- game executable under `Game/`
- `global-metadata.dat` under the game's `il2cpp_data/Metadata/` tree
- native plugins under the game's `Plugins/x86_64/` tree
- `Host.exe`
- `Launcher.exe`

The repository also contains supporting resources and configuration files. Do not assume every file is analysis-relevant; document relevance as it is established.

## SHA-256 fingerprints

Populate these from the local original files. Do not use Git LFS pointer hashes as binary SHA-256 fingerprints.

| File | SHA-256 | Status |
|---|---|---|
| `Game/GameAssembly.dll` | `PENDING` | required |
| `Game/UnityPlayer.dll` | `PENDING` | required |
| `global-metadata.dat` | `PENDING` | required |
| `Game/baselib.dll` | `PENDING` | recommended |
| game executable | `PENDING` | recommended |
| `Host.exe` | `PENDING` | optional |
| `Launcher.exe` | `PENDING` | optional |

## Version-change rule

Before reusing offsets, native addresses, metadata layouts, method mappings, or binary-specific conclusions:

1. Compare current local SHA-256 values with this manifest.
2. If `GameAssembly.dll` or `global-metadata.dat` changes, mark binary-specific conclusions for re-validation.
3. Preserve old findings instead of overwriting history when a new client build is introduced.
4. Add the new build identifier and clearly state which findings were re-verified.

## Recommended local hash command

PowerShell example:

```powershell
Get-FileHash -Algorithm SHA256 ".\Game\GameAssembly.dll"
```

For the metadata file, use the exact local path shown by the client installation.

## Notes

- Files managed by Git LFS may appear as small pointer files through some GitHub APIs. That pointer content is not the original binary.
- Deep analysis should use the original binary bytes, not the LFS pointer text.
