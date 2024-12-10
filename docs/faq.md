## **FAQ** <!-- {docsify-ignore} -->

###### How do I reconfigure Natlink after installation?

- After install natlink can be reconfigured Using `Configure Natlink via GUI` or `Configure Natlink via CLI` Natlink start menu.

###### How can I install other Python packages with Natlink?

- Natlink requires a specific Python interpreter. You can access the Python environment via `Natlink Python Environment` from the natlink start menu

###### Where are natlink configuration files located?

- The natlinkconfig_gui or natlinkconfig_cli creates configuration files in`%UserProfile%\.natlink` as `natlink.ini`.

###### Can I change the default location for natlink configuration files?

- Yes! Set an environmental variable `NATLINK_SETTINGSDIR` to your desired location. For example `%UserProfile%\Documents\.natlink`.

(Note: for versions of natlinkcore up to 5.3.13 (July 31, 2024) this option was `NATLINK_USERDIR`. If you used this setting, please change the environmental variable to `NATLINK_SETTINGSDIR`.)

###### Can I change the logging level of natlink?

- You can set the log level with the following option (DEBUG, INFO, WARNING) with `Natlink via GUI` or `Configure Natlink via CLI` from the natlink start menu.

###### Can Natlink utilize Python 64-bit?

- Currently Dragon NaturallySpeaking (up to version 16) is itself a 32-bit application and it is therefore not possible for it to directly call a 64-bit .pyd.
  - This may be possible with a future contributor. Please open up pull request.