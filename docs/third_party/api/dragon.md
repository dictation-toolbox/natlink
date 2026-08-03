# Dragon API

These functions, callbacks, objects, and exceptions make up natlink's
Dragon-facing public API.  The original C extension API is documented in
[natlink.txt](../../natlink.txt)
([upstream](https://github.com/dictation-toolbox/natlink/blob/master/NatlinkSource/natlink.txt)).

## Connection And Lifecycle

### `natConnect`

::: natlink_compat.natConnect

### `natDisconnect`

::: natlink_compat.natDisconnect

### `waitForSpeech`

::: natlink_compat.waitForSpeech

### `isNatSpeakRunning`

::: natlink_compat.isNatSpeakRunning

## Callbacks

### `setBeginCallback`

::: natlink_compat.setBeginCallback

### `setChangeCallback`

::: natlink_compat.setChangeCallback

### `setTimerCallback`

::: natlink_compat.setTimerCallback

### `getCallbackDepth`

::: natlink_compat.getCallbackDepth

## Speech And Input

### `playString`

::: natlink_compat.playString

### `playEvents`

::: natlink_compat.playEvents

### `execScript`

::: natlink_compat.execScript

### `recognitionMimic`

::: natlink_compat.recognitionMimic

### `inputFromFile`

::: natlink_compat.inputFromFile

## System Information

### `getCurrentModule`

::: natlink_compat.getCurrentModule

### `getCurrentUser`

::: natlink_compat.getCurrentUser

### `getMicState`

::: natlink_compat.getMicState

### `setMicState`

::: natlink_compat.setMicState

### `getClipboard`

::: natlink_compat.getClipboard

### `getCursorPos`

::: natlink_compat.getCursorPos

### `getScreenSize`

::: natlink_compat.getScreenSize

## Display And UI

### `displayText`

::: natlink_compat.displayText

### `setMessageWindow`

::: natlink_compat.setMessageWindow

## Objects

### `GramObj`

::: natlink_compat.GramObj

### `ResObj`

::: natlink_compat.ResObj

### `DictObj`

::: natlink_compat.DictObj

## Users And Vocabulary

### User Profiles

::: natlink_compat.getAllUsers

::: natlink_compat.createUser

::: natlink_compat.openUser

::: natlink_compat.saveUser

### Training

::: natlink_compat.getUserTraining

::: natlink_compat.getTrainingMode

::: natlink_compat.startTraining

::: natlink_compat.finishTraining

### Vocabulary

::: natlink_compat.getWordInfo

::: natlink_compat.addWord

::: natlink_compat.deleteWord

::: natlink_compat.setWordInfo

::: natlink_compat.getWordProns

### Extended Vocabulary

::: natlink_compat.enumerateWords

::: natlink_compat.enumeratePrefixWords

::: natlink_compat.getWordFromPrefix

::: natlink_compat.getWordFromPron

## Exceptions

### `NatError`

::: natlink_compat.NatError

### `InvalidWord`

::: natlink_compat.InvalidWord

### `UnknownName`

::: natlink_compat.UnknownName

### `OutOfRange`

::: natlink_compat.OutOfRange

### `MimicFailed`

::: natlink_compat.MimicFailed

### `BadGrammar`

::: natlink_compat.BadGrammar

### `WrongState`

::: natlink_compat.WrongState

### `BadWindow`

::: natlink_compat.BadWindow

### `SyntaxError`

::: natlink_compat.SyntaxError

### `UserExists`

::: natlink_compat.UserExists

### `ValueError`

::: natlink_compat.ValueError

### `DataMissing`

::: natlink_compat.DataMissing

### `WrongType`

::: natlink_compat.WrongType
