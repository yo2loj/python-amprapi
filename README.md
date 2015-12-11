AMPR Portal API and RouterOS API Python bindings
================================================

Install Dependencies
--------------------

    sudo pip install requests

Usage
-----

    ampr = AMPRAPI()
    result = ampr.endpoint

Example (with "encap" endpoint)
-------------------------------

    >>> import amprapi
    >>> ampr = amprapi.AMPRAPI()
    >>> for entry in ampr.encap:
    ...     print "%(network)s/%(netmask)s via %(gatewayIP)s" % entry
    ...
    44.151.22.22/32 via 2.10.28.74
    44.182.69.0/24 via 5.15.186.251
    44.133.30.64/32 via 5.57.28.49
    ...


Settings
========

To use the AMPR Portal API, you need to set an API key via your AMPR Portal
Profile. Once you have set your API key, save your username and API key in
`settings.py`.

rosapi.py
=========
Based on the RouterOS API access provided by Mikrotik on its wiki page.
Access credentials are set in 'settings.py'.
For more details check http://wiki.mikrotik.com/wiki/Manual:API

updateros.py
=============

Requests the list of encap routes from the AMPR Portal API, then updates the
target Mikrotik router with new, removed, or changed routes using the RouterOS API.
Router settings are defines in 'settings.py'

Usage
-----

	./updateros.py [-v] [-f]

`-f` force. Continue even when sanity check fails.

`-v` verbose mode. Commands to target router will be printed.
