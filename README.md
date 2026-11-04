# a02 detection model

Copyright (c) 2026 CYBERINE LLC. All rights reserved.

This repository publishes one public, signed file for the a02 privacy monitoring app: the
on-device model that estimates which app most likely used the microphone or camera.

## The promise this repository keeps

- **Nothing from the phone.** The app downloads `model.json` and `model.json.sig` only when the
  user taps *Update detection model*. The request carries no identifier and nothing about the
  phone. Every user receives the same file.
- **No CYBERINE server.** The file is served by GitHub. CYBERINE operates nothing that the phone
  talks to.
- **Readable by anyone.** The file and its history are public, so anyone can check what the app
  downloads.
- **Signed.** The app checks the signature against the public key it ships with before using a
  downloaded file. A file that does not verify is discarded. A file with a version equal to or
  lower than the one in use, or an unknown feature set, is refused.

## Files

| Path | What it is |
|---|---|
| `model.json` | The model: `format`, `version`, `date`, `features`, `classes`, `weights` |
| `model.json.sig` | Signature over the exact bytes of `model.json` (ECDSA P-256, SHA-256, base64) |

The private signing key is never in this repository. The app ships with a copy of every model
it needs; this download only brings a newer one between app updates.
