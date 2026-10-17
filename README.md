# a02 declarations file

Copyright (c) 2026 CYBERINE LLC. All rights reserved.

This repository publishes one public, signed data file for the a02 privacy monitoring app:
what other apps declare about their data on the Play Store (the Data safety section) and where
their privacy policies are. The app compares each installed app's permissions with its entry here.

## The promise this repository keeps

- **Nothing from the phone.** The app downloads `declarations.json` and `declarations.json.sig`
  only when the user presses Update. The request carries no identifier and nothing about the phone.
  Every user receives the same file, so the download reveals nothing about which apps are installed.
- **No CYBERINE server.** The file is served by GitHub. CYBERINE operates nothing that the phone
  talks to.
- **Readable by anyone.** The file, its history and the script that builds it are public, so
  anyone can check what the app compares against.
- **Signed.** The app checks the signature against the public key it ships with before using a
  downloaded file. A file that does not verify is discarded.

## Files

| Path | What it is |
|---|---|
| `declarations.json` | The data file. Format described below and in `schema/declarations.schema.json` |
| `declarations.json.sig` | Signature over the exact bytes of `declarations.json` (ECDSA P-256, SHA-256, base64) |
| `keys/declarations-public.pem` | The public key the app ships with. The private key is never in this repository |
| `tools/build_declarations.py` | Builds `declarations.json` from `sources/` |
| `tools/sign.py`, `tools/verify.py` | Sign and verify the file |
| `tools/make_key.py` | Makes a new key pair. Run once, on the signing machine, by the key holder |
| `sources/packages.txt` | The apps the file covers, one package name per line |
| `sources/overrides.json` | Declarations read from each app's store page, one page at a time in a browser, until an automatic source is settled |
| `tools/read_datasafety_page.js` | Pasted into the browser on a Data safety page, returns that app's entry as JSON |

## Format of `declarations.json`

```json
{
  "format": 1,
  "generatedAt": "2026-10-17T23:00:00Z",
  "sdk": 37,
  "source": { "declarations": "manual", "note": "..." },
  "dataTypesByGroup": { "LOCATION": ["Location"], "MICROPHONE": ["Audio"], "...": [] },
  "apps": {
    "com.example.app": {
      "name": "Example",
      "developer": "Example Ltd",
      "policyUrl": "https://example.com/privacy",
      "readAt": "2026-10-17",
      "versionCode": 12345,
      "declared": {
        "collected": ["Location", "Personal info"],
        "shared": ["Device or other IDs"]
      }
    }
  }
}
```

- `readAt` is the date the entry was read from the store. On the phone, an app that was installed
  or updated after that date counts as "not on file for this version" until the next read.
- `dataTypesByGroup` maps each Android permission group the app reads to the Play Store data types
  that would cover it. It lives in the file so the mapping can change without an app update.
- Data type names are the Play Store's own: Location, Personal info, Financial info, Health and
  fitness, Messages, Photos and videos, Audio, Files and docs, Calendar, Contacts, App activity,
  Web browsing, App info and performance, Device or other IDs.
- An app with no entry is "not on file". An app whose entry has `"declared": null` was looked up
  and had no Data safety section.

## Building and publishing

```
python tools/build_declarations.py            # writes declarations.json
python tools/sign.py --key <private key>      # writes declarations.json.sig
python tools/verify.py                        # checks the pair against keys/declarations-public.pem
git commit -am "Declarations as of <date>" && git push
```

The app fetches the raw files from the `main` branch.

## Open

- **Source for the declarations.** Reading Data safety sections from Play Store pages with a crawler
  is against Google's terms of service. Until that is settled with counsel, or a licensed dataset
  is used, entries come from a person's browser, one page at a time, with
  `tools/read_datasafety_page.js` turning the page into the JSON entry.
- **Key holder.** Who holds the private key and where it is kept.
- **Licence for this data.**
