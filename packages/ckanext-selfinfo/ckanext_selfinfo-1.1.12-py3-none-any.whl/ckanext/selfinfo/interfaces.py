from __future__ import annotations

from ckan.plugins import Interface


class ISelfinfo(Interface):
    """Implement custom Selfinfo response modification."""

    def selfinfo_after_prepared(self, data):
        """Return selinfo data.

        :returns: dictonary
        :rtype: dict

        """

        return data
