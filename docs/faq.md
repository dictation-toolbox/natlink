# FAQ

###### Does Natlink support 64-bit Python?

- Yes. Natlink connects to Dragon as an out-of-process COM client, so 64-bit Python is fully supported and recommended. Cross-bitness marshaling is handled by custom marshal DLLs shipped with the `natlink_com` package.

###### How can I install other Python packages with Natlink?

- Install into the same environment as natlink. For example: `uv pip install dragonfly2`.

###### Are there known limitations on Windows 11?

- Yes. In particular, keystroke playback behavior differs by Dragon version and Windows security restrictions can affect input injection. See [Technical Limitations](technical-limitations.md) for details.

###### Can `recognitionMimic` fail intermittently even when grammars are loaded?

- Yes. Consecutive mimic calls can still hit Dragon-side timing limitations while the microphone is active. See [Technical Limitations](technical-limitations.md#consecutive-recognitionmimic-with-active-microphone) for details.

###### Are there Dragon-version-specific limitations or behavior differences?

- Yes. Natlink handles several differences between Dragon 13-14 and 15-16, but some behaviors still vary by version. See [Technical Limitations](technical-limitations.md) for details.

###### Where should I look for configuration, logging, or loader setup?

- Use [Configuration Overview](configuration/index.md) for config file locations, [Settings Reference](configuration/settings.md) for `natlink.ini`, [Logging Reference](configuration/logging.md) for log tuning, and the [Integration Guide](third_party/index.md) for loader behavior and public extension points.
