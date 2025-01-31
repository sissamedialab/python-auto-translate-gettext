po-translate
============

What is it?
-----------

This tool will translate a gettext .po file using `DeepL <https://www.deepl.com/>`__ and save the translated strings to that same file.

Here we just expand on `python-auto-translate-gettext https://github.com/confdnt/python-auto-translate-gettext`_

Documentation
-------------

Install with ``pip`` or ``pipx`` from out internal registry. E.g.
``pipx install -i https://gitlab.sissamedialab.it/api/v4/projects/60/packages/pypi/simple po-translate``

Add you DeepL authentication token to a ``config.ini`` file of this form:

    [deepL]
    api_token = your_deepl_api_token_here

and call ``po-translate`` indicating the target language and the .po file to process:
``po-translate -l PT-BR -f mymessages.po --config .../config.ini``

Licensing
---------

python-auto-translate-gettext is licensed under the terms of the MIT License (see
`License <LICENSE>`__).
