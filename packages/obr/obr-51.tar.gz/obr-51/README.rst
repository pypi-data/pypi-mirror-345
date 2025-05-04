OBR
===


**NAME**


``obr`` - OBR


**SYNOPSIS**

::

    >>> from obr import Client, Event
    >>> def hello(event):
    ...     event.reply("hello!")
    ... 
    >>> clt = Client()
    >>> clt.register("hello", hello)
    >>> clt.start()
    >>> 
    >>> e = Event()
    >>> e.type = "hello"
    >>> clt.put(e)
    >>> e.display(print)
    hello!


**DESCRIPTION**


``OBR`` is a runtime that provides thread support and an event handler
to handle (threaded) callbacks.


**INSTALL**

::

    $ pip install obr


**SOURCE**


source is at https://github.com/bthate/obr


**AUTHOR**


Bart Thate <bthate@dds.nl>


**COPYRIGHT**


``OBR`` is Public Domain.
