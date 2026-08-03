"""_vocabulary.py - Dragon vocabulary/lexicon functions."""

from typing import List, Optional, Union

from ._helpers import _require_connected, com_call
from ._state import _state


def getWordInfo(word: str, flags: int = 0) -> Optional[int]:
    """Look up a word in the vocabulary and return its formatting properties.

    Returns an integer bit vector of word formatting flags, or ``None`` if
    the word is not in the vocabulary.

    Args:
        word: The word to look up.
        flags: Optional combination of lookup flags:

            - ``1`` — consider inactive words (backup dictionary)
            - ``2`` — consider active non-dictation words
            - ``4`` — case insensitive match

    Returns:
        Bit vector of formatting flags, or ``None``. Key flags include:

        - ``0x00000001`` — word was added by the user
        - ``0x00000010`` — capitalize the next word (like period)
        - ``0x00000100`` — no space following this word (like left paren)
        - ``0x00000200`` — two spaces following (like period)
        - ``0x00200000`` — no space preceding (like comma)
        - ``0x00800000`` — follow with one newline (New-Line)
        - ``0x01000000`` — follow with two newlines (New-Paragraph)
        - ``0x40000000`` — word was added by the vocabulary builder

    Raises:
        InvalidWord: If the word is invalid.
        ValueError: If the flags are invalid.
    """
    _require_connected()
    result = com_call("getWordInfo", _state.backend.get_word_info, word, flags)
    return result


def addWord(word: str, wordInfo: int = 1,
            pronList: Union[str, List[str]] = None) -> int:
    """Add a word to the active vocabulary.

    The word may be completely new or already in the backup dictionary.
    Pronunciations use Dragon's pronunciation alphabet.  You can add
    pronunciations to an existing word but cannot delete them.

    Returns 1 if the word was added or a pronunciation was provided.
    Returns 0 if no pronunciations were given and the word already exists
    (in which case wordInfo is ignored).

    To change the wordInfo of an existing word, pass in a pronunciation::

        prons = natlink.getWordProns(word)
        natlink.addWord(word, newInfo, prons[0])

    Args:
        word: The word to add.
        wordInfo: Formatting bit flags (default ``0x01`` = user-added).
            Use ``0`` for words from the backup dictionary.
            Add ``0x40000000`` for batch-imported words (vocabulary builder).
        pronList: Optional pronunciation string or list of pronunciations.

    Raises:
        InvalidWord: If the word is invalid.
    """
    _require_connected()
    if pronList is None:
        added = com_call("addWord", _state.backend.add_word, word, "", wordInfo)
        return 1 if added else 0
    elif isinstance(pronList, str):
        com_call("addWord", _state.backend.add_word, word, pronList, wordInfo)
    else:
        for pron in pronList:
            com_call("addWord", _state.backend.add_word, word, pron, wordInfo)
    return 1


def deleteWord(word: str) -> None:
    """Remove a word from the active vocabulary.

    The word will still be in the backup dictionary.

    Raises:
        InvalidWord: If the word is invalid.
        UnknownName: If the word is not in the active vocabulary.
    """
    _require_connected()
    com_call("deleteWord", _state.backend.delete_word, word)


def setWordInfo(word: str, wordInfo: int) -> None:
    """Change the formatting properties for a word in the active vocabulary.

    Raises:
        InvalidWord: If the word is invalid.
        UnknownName: If the word is not in the active vocabulary.
    """
    _require_connected()
    com_call("setWordInfo", _state.backend.set_word_info, word, wordInfo)


def getWordProns(wordName: str) -> Optional[List[str]]:
    """Return the pronunciations for a word.

    Each pronunciation is a string in Dragon's pronunciation alphabet.
    Returns ``None`` if the word does not exist.

    Note:
        Cross-process pronunciation retrieval is broken in Dragon 13's
        proxy/stub DLL (``ILexPronounceW::Get`` returns empty buffers).
        Natlink falls back to ``IDgnLexWordW`` which works reliably
        cross-bitness.

    Raises:
        InvalidWord: If the word is invalid.
    """
    _require_connected()
    prons = com_call("getWordProns", _state.backend.get_word_prons, wordName)
    return prons


def enumerateWords() -> List[str]:
    """Enumerate vocabulary words exposed by Dragon's Unicode lexicon."""
    _require_connected()
    return com_call("enumerateWords", _state.backend.enumerate_words)


def enumeratePrefixWords(prefix: str) -> List[str]:
    """Enumerate vocabulary words matching a prefix."""
    _require_connected()
    return com_call("enumeratePrefixWords",
                    _state.backend.enumerate_prefix_words, prefix)


def getWordFromPrefix(prefix: str, flags: int = 0, index: int = 0) -> str:
    """Get a single vocabulary word match for a prefix lookup."""
    _require_connected()
    return com_call("getWordFromPrefix",
                    _state.backend.get_word_from_prefix, prefix, flags, index)


def getWordFromPron(pronunciation: str, flags: int = 0, index: int = 0) -> str:
    """Get a single vocabulary word match for a pronunciation lookup."""
    _require_connected()
    return com_call("getWordFromPron",
                    _state.backend.get_word_from_pron,
                    pronunciation, flags, index)
