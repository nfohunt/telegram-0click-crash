# Telegram Emoji Interaction — Client-Side OOB PoC

**Discovered by nfosecurity**

A Proof of Concept (PoC) for investigating a potential **out-of-bounds (OOB)** condition in Telegram's emoji interaction handling.

> **Status:** Security Research / Proof of Concept
> **Researcher:** nfosecurity

## Overview

This PoC uses [Telethon](https://github.com/LonamiWebs/Telethon) to construct and send a custom `SendMessageEmojiInteraction` action.

The test focuses on how the Telegram client processes the interaction payload:

```json
{"v":1,"a":[{"i":0,"t":0.5}]}
```

The research hypothesis is that the interaction index may be interpreted incorrectly by the receiving client, potentially resulting in an out-of-bounds access.

## Technical Details

The PoC manually implements two Telegram TL objects:

### `DataJSON`

A custom implementation of the Telegram `DataJSON` TL object used to serialize the interaction payload.

### `SendMessageEmojiInteraction`

A custom TL object containing:

* `emoticon` — the emoji associated with the interaction.
* `msg_id` — the target message ID.
* `interaction` — the serialized `DataJSON` payload.

The objects are serialized using their corresponding Telegram TL constructor IDs.

## Payload

The interaction payload used by the PoC is:

```json
{
  "v": 1,
  "a": [
    {
      "i": 0,
      "t": 0.5
    }
  ]
}
```

The relevant condition is:

```text
i = 0
```

The PoC investigates whether this value can eventually be interpreted as an index before the beginning of the expected interaction list.

Conceptually:

```text
i = 0
    ↓
index calculation
    ↓
index = -1
    ↓
potential out-of-bounds access
```

Whether this actually results in an OOB condition depends on the implementation and version of the Telegram client being tested.

## Requirements

* Python 3.9+
* A Telegram test account
* Telegram `api_id`
* Telegram `api_hash`
* [Telethon](https://github.com/LonamiWebs/Telethon)

Install the dependency:

```bash
pip install telethon
```

## Configuration

Set the Telegram API credentials in the PoC:

```python
API_ID = ...
API_HASH = "..."
```

Set the test target:

```python
TARGET = "@test_user"
```

Alternatively, environment variables can be used:

```text
TG_API_ID
TG_API_HASH
TARGET
```

Example:

```powershell
$env:TG_API_ID="123456"
$env:TG_API_HASH="your_api_hash"
$env:TARGET="@test_user"
```

## Running the PoC

```bash
python poc.py
```

On the first execution, Telethon will request the required authentication information.

A local session file named:

```text
attacker.session
```

may be created by Telethon.

## Expected Output

The PoC prints information about each stage of the test:

```text
[.] logged in as: id=... @...
[.] resolved peer: ...
[.] sending message '❤️' ...
[.] message sent, id = ...
[.] sending action: interaction={"v":1,"a":[{"i":0,"t":0.5}]}
[.] server response: ...
[.] sent.
```

A successful server response **does not by itself confirm a client-side vulnerability**.

Confirmation requires observing the receiving client and determining whether the interaction results in an invalid memory access, crash, exception, or other unexpected behavior.

## Research Flow

The investigated flow can be summarized as:

```text
Telegram Client A
       |
       | Message + Emoji
       v
Telegram Server
       |
       | Emoji Interaction
       v
Telegram Client B
       |
       | Parse Interaction
       v
Interaction List
       |
       | Unexpected Index
       v
Potential OOB Access
```

## Validation

To determine whether the suspected condition is actually present, testing should be performed against an isolated test environment while monitoring:

* Client crashes
* Access violations
* AddressSanitizer reports
* UndefinedBehaviorSanitizer reports
* Exceptions
* Stack traces
* Unexpected memory access
* Differences between affected and patched versions

The exact Telegram client version and platform should be recorded for every test.

## Limitations

This PoC does **not automatically prove exploitability**.

Acceptance of the action by the Telegram server does not necessarily indicate that the receiving client performs an invalid memory access.

The final behavior depends on factors including:

* Telegram client version
* Operating system
* Client implementation
* Interaction parsing logic
* Bounds validation
* Index handling
* Existing mitigations

## Responsible Use

This PoC is intended for authorized security research and controlled testing.

Only test accounts, clients, and environments for which you have permission should be used.

Do not use this PoC to:

* Target unauthorized users
* Cause intentional service disruption
* Perform mass testing
* Attempt to access third-party data
* Deploy the behavior against production users without authorization

## Responsible Disclosure

If the behavior is confirmed as a security vulnerability, the recommended disclosure process is to provide the vendor with:

* Affected client versions
* Fixed versions, if available
* Minimal reproduction steps
* Relevant logs
* Stack traces
* Crash information
* Technical root-cause analysis
* Security impact assessment

Additional exploitation details should be withheld until an appropriate fix or mitigation is available.

## Credits

**Discovered by nfosecurity**

Security research and PoC development by **nfosecurity**.

## License

This project is provided for security research and educational purposes only.
