# Natlink

Natlink is a Python interface for Dragon NaturallySpeaking on Windows. It
provides a 64-bit Python integration layer over Dragon's COM interfaces so
grammars, macros, and custom integrations can run outside the original C
extension model.

Natlink connects to Dragon as an out-of-process COM client. Cross-bitness
communication between 64-bit Python and 32-bit Dragon is handled by the
marshal DLLs shipped in `natlink_com`, so modern Python versions can integrate
with Dragon without the old in-process C extension model.

Grammars can insert boilerplate, drive application menus, automate workflows,
or help with coding and dictation. Natlink provides the Python bridge; loaders
and downstream projects such as natlinkcore or Dragonfly build the higher-level
command ecosystems on top of it.

## Choose A Path

- New user:
  start with [Install](install.md), then read
  [Configuration Overview](configuration/index.md) and [FAQ](faq.md).
- Contributor:
  read [Contributing](contributing.md), then [Testing](testing.md) and
  [Developer Debugging](developer-debugging.md).
- Maintainer or code reader:
  use [Architecture](architecture.md), [Program Flow](program_flow.md), and
  [Project Structure](structure.md).

## Key References

- [Technical Limitations](technical-limitations.md) for Dragon and Windows
  behavior constraints
- [Settings Reference](configuration/settings.md) for `natlink.ini`
- [Logging Reference](configuration/logging.md) for log categories and levels
- [Grammar Binary Format](grammar_binary_format.md) for low-level compiler and
  interoperability work

## Ecosystem

- [Natlink](https://github.com/dictation-toolbox/natlink): this repository and
  the public Python API into Dragon
- [Natlink Core](https://github.com/dictation-toolbox/natlinkcore): grammar
  loader integration for natlink
- [Dragonfly](https://github.com/dictation-toolbox/dragonfly): higher-level
  speech framework built on multiple recognition engines
- [Unimacro](https://github.com/dictation-toolbox/unimacro): configurable
  grammar collection for Natlink and Dragon
- [Caster](https://github.com/dictation-toolbox/Caster): Dragonfly-based voice
  coding and command environment
