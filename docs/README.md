# Natlink 

Natlink is a compatibility module for [Dragon NaturallySpeaking (DNS/DPI)](https://www.nuance.com/dragon.html) v13-v16 on Windows that allows the user to run Python scripts that interact with DNS on Windows OS.

## Introduction <!-- {docsify-ignore} -->

Natlink can be used as a library for low-level access Dragon engine with a framework for writing grammars and macros.

Grammars can be used to insert text boilerplate, operate the menus of programs, or otherwise control a computer. They can even be used to help
write computer programs. A grammar specifies what will happen when certain words are dictated with grammar rules. For example, a hypothetical grammar could have a very simple rule `american date today` which prints the current date out in a format `mm/dd/yyyy`.

<div align="center">

[![matrix](https://img.shields.io/gitter/room/dictation-toolbox/natlink)](https://matrix.to/#/#dictation-toolbox_natlink:gitter.im) [![view - Documentation](https://img.shields.io/badge/view-Documentation-blue?)](https://dictation-toolbox.github.io/natlink/#/) [![GitHub Release](https://img.shields.io/github/v/release/dictation-toolbox/natlink?include_prereleases)](https://github.com/dictation-toolbox/natlink/releases)

</div>

## **Ecosystem**

There are different projects that utilize natlink to build your own grammar/scripts:

[Natlink](https://github.com/dictation-toolbox/natlink) is this repository. Natlink is an C++ extension module for Dragon NaturallySpeaking (DNS/DPI). Natlink C++ is installed only by the Natlink's installer and not through PyPI.

[Natlink Core](https://github.com/dictation-toolbox/natlinkcore): Provides the Python interface to this repositories C++ extension and loads native Natlink grammars. The Natlink installer installs natlink core to the correct python site-packages. All natlink based projects depend on natlinkcore which is required For the following projects to function with Dragon NaturallySpeaking

[Dragonfly](https://github.com/dictation-toolbox/dragonfly) is speech recognition framework for Python that makes it convenient to create custom commands to use with speech recognition software that can be cross-platform and supports multiple speech recognition engines.

[Unimacro](https://github.com/dictation-toolbox/unimacro): project aims to provide a rich set of command grammars, that can be configured by the users without programming knowledge.

[Caster](https://github.com/dictation-toolbox/Caster) Caster extends Dragonfly for features like CCR (continuous command recogntion) aand provides a set of commands and grammars for programming and general computer use.


