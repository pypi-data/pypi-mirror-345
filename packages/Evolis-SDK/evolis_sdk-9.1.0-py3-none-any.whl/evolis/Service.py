# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from evolis import Model, Evolis
from evolis.Connection import _inbuf

from typing import Optional


class Service:
    def select(model: Model, url: Optional[str] = None) -> bool:
        """
        Set the supervision service information.
        If no url is provided the service name and url are retrieved from the defaults of the provided model.
        If an url is provided it will override the default value.

        Parameters
        ----------
        model: Model
            The target model

        url: str
            Override the service URL if defined

        Returns
        -------
        bool
            True in case of success
        """
        if url:
            return Evolis.wrapper.evolis_service_select_with_url(model.value, _inbuf(url))
        return Evolis.wrapper.evolis_service_select(model.value)

    def start() -> bool:
        """
        Start the evolis supervision provider service.

        Returns
        -------
        bool
            True in case of success
        """
        return Evolis.wrapper.evolis_service_start()

    def restart() -> bool:
        """
        Restart the evolis supervision provider service.
        If it's not running, start it.

        Returns
        -------
        bool
            True in case of success
        """
        return Evolis.wrapper.evolis_service_restart()

    def stop() -> bool:
        """
        Stop the evolis supervision provider service.

        Returns
        -------
        bool
            True in case of success
        """
        return Evolis.wrapper.evolis_service_stop()

    def is_running() -> bool:
        """
        Check if the service is running or not.

        Returns
        -------
        bool
            True if the service is running
        """
        return Evolis.wrapper.evolis_service_is_running()
