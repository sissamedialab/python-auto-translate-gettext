po-translate
============

Documentation
-------------

This tool will translate a gettext .po file using `DeepL <https://www.deepl.com/>`__ and save the translated strings to that same file.

Before sending the message string (``msgstr``) to DeepL, variables eventually present in the message are replace by placeholders. This avoids the variable names beeing translated (sometimes it happened) and reduces the number of billed-chars. Both f-strings and %-interpolated variables are managed.

Here we just expand on |cone| Compliance.One's `python-auto-translate-gettext <https://github.com/confdnt/python-auto-translate-gettext>`__

.. |cone|  image:: https://avatars.githubusercontent.com/u/74371330?s=20&v=4
  :width: 20px
  :align: middle



Install
-------

Install with ``pip`` or ``pipx`` from our internal registry. E.g.

::

   pipx install -i https://gitlab.sissamedialab.it/api/v4/projects/60/packages/pypi/simple po-translate

Add you DeepL authentication token to a ``config.ini`` file of this form:

::

    [deepL]
    api_token = your_deepl_api_token_here


Usage
-----

Call ``po-translate`` indicating the target language and the .po file to process:

::

   po-translate -l PT-BR -f mymessages.po --config .../config.ini


Licensing
---------

python-auto-translate-gettext is licensed under the terms of the MIT License (see
`License <LICENSE>`__).
