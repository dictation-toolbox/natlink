### Migrating from Natlink 2.7: <!-- {docsify-ignore} -->

1. Natlink 3 utilizes Python 3:
    - Porting resources: [The Conservative Python 3 Porting Guide](https://portingguide.readthedocs.io/en/latest/)

2. Use qualified imports:
   
    ```python
    prev: from natlinkutils import *
    now: from natlink.natlinkutils import *
    ```

3.  API changes:
    - `natlink.playString` obsolete, use `sendkeys` from `dtactions` module
   
    ```python
    # Previously
    import natlink
    natlink.playString('test string')
    ```
   
    ```python
    # Now
    from dtactions.sendkeys import sendkeys as playString
    playString('test string')
    ```