"""
Business Source License 1.1

Copyright (C) 2025 Raman Marozau, raman@worktif.com
Use of this software is governed by the Business Source License included in the LICENSE file and at www.mariadb.com/bsl11.

Change Date: Never
On the date above, in accordance with the Business Source License, use of this software will be governed by the open source license specified in the LICENSE file.
Additional Use Grant: Free for personal and non-commercial research use only.

SPDX-License-Identifier: BUSL-1.1
"""

import sys
import threading
import time


class Loader:
    def __init__(self, message="Downloading"):
        """
        Represents a CLI-based animation that indicates a background task.

        This class is designed to show a simple animation in the terminal
        to convey the progress of an ongoing background task. The animation
        runs in a separate thread to ensure that it does not block the main
        thread's operations.

        Attributes
        ----------
        _message : str
            The text message displayed along with the animation.
        _thread : threading.Thread
            The thread responsible for running the animation in the background.
        done : bool
            A control flag to stop the animation when set to True.

        :param message: The message to display alongside the animation. Defaults to
            "Downloading".
        """
        self._message = message
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self.done = False

    def set_message(self, message: str):
        """
        Sets the message attribute of the instance.

        :param message: A string representing the message to be assigned.
        :type message: str
        """
        self._message = message

    def start(self):
        """
        Starts the thread associated with this instance.

        This method initiates the thread's execution by invoking the `start`
        method on the `self._thread` object. It assumes that the `self._thread`
        attribute has been properly initialized and is a valid thread instance.

        :return: None
        """
        self._thread.start()

    def stop(self):
        """
        Represents a mechanism to stop a thread execution gracefully.

        This class or function provides a controlled way to stop a running thread
        by marking it as done and waiting for the thread to conclude its execution.
        It ensures the thread completes its ongoing tasks correctly before stopping.

        :attributes:
            done: Indicates whether the thread execution is flagged to stop.
            _thread: The thread instance being managed.

        :return: None
        """
        self.done = True
        self._thread.join()

    def _animate(self):
        """
        Handles the animation of a loading spinner for a CLI-based task. The animation
        displays a series of symbols in rotation while the task is ongoing. It
        continues until the flag `self.done` is set to True. Once the task is complete,
        a "done" message is displayed.

        This method is designed to provide a simple user feedback mechanism during
        long-running or background operations in command-line applications.

        :return: None
        """
        symbols = ["|", "/", "-", "\\"]
        i = 0
        while not self.done:
            sys.stdout.write(f"\r{self._message}... {symbols[i % len(symbols)]}")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
        sys.stdout.write(f"\r{self._message}... done.\n")
