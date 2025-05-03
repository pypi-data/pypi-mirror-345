# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Threading helper functions."""

# Standard Library
import threading
import time
from typing import Any, Callable


class PreciseRepeatedTimer:
    """A timer that repeatedly calls a function at a fixed interval.

    This class is a wrapper around a threading.Timer that allows ensuring consistent timing
    regardless of the function's execution time.

    If the function takes longer than the interval, a warning is printed.
    """

    def __init__(self, interval: float, function: Callable, *args: Any, **kwargs: Any):
        """Initialize the `PreciseRepeatedTimer` instance.

        Args:
            interval: Time between function calls in seconds.
            function: The function to call.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
        """
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True

    def _run(self) -> None:
        """Internal method that runs the timer loop, calling the function at fixed intervals."""
        next_time = time.time()
        while not self._stop_event.wait(max(0, next_time - time.time())):
            start_time = time.time()
            self._function(*self._args, **self._kwargs)
            elapsed = time.time() - start_time

            if elapsed > self._interval:
                print(
                    f"[WARNING] Function execution ({elapsed:.3f}s) exceeded interval"
                    f" ({self._interval:.3f}s)"
                )

            next_time += self._interval

    def start(self) -> None:
        """Start the timer. If the timer is already running, this does nothing."""
        if not self.is_running():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run)
            self._thread.daemon = True
            self._thread.start()

    def stop(self) -> None:
        """Stop the timer. This will stop any further function calls."""
        self._stop_event.set()

    def is_running(self) -> bool:
        """Check if the timer is currently running.

        Returns:
            bool: True if the timer thread is alive and the stop event is not set.
        """
        return self._thread.is_alive() and not self._stop_event.is_set()
