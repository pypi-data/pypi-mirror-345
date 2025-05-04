``planetcasio`` -- Utilities for interacting with Planète Casio
===============================================================

This project is a Python module for interacting with `Planète Casio`_
programmatically.

For example, you can use this module to post a message on the shoutbox:

.. code-block:: python

    import asyncio

    from planetcasio.client import Client

    async def main():
        async with Client(auth=("my_username", "my_password")) as client:
            channel = await client.shout.get_channel("hs")
            await channel.post("Hello, world!")

    asyncio.run(main())

The project is present at the following locations:

* `Official website and documentation at planetcasio.touhey.pro <Website_>`_;
* `thomas.touhey/planetcasio repository on Gitlab <Gitlab repository_>`_;
* `planetcasio project on PyPI <PyPI project_>`_.

.. _Planète Casio: https://www.planet-casio.com/Fr
.. _Website: https://planetcasio.touhey.pro/
.. _Gitlab repository: https://gitlab.com/thomas.touhey/planetcasio
.. _PyPI project: https://pypi.org/project/planetcasio/
