OBR
===


**NAME**


``OBR`` - object runtime


**SYNOPSIS**

::


    >>> from obr.event import Event
    >>> from obr.handler import Handler
    >>>
    >>> def hello(event):
    >>>     event.reply("hello!")
    >>>     event.ready()
    >>>
    >>> hdl = Handler()
    >>> hdl.register("hello", hello)
    >>> hdl.start()
    >>>
    >>> e = Event()
    >>> e.type = "hello"
    >>> hdl.put(e)
    >>> e.wait()


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
