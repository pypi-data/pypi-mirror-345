from pynput import keyboard


class HWButton:
    """
    A class to monitor a specific hardware button press using `pynput`.

    Attributes:
        _key_to_monitor (str): The key to monitor for presses.
        _callback (function): The callback function to call on key press.
        _listener (Listener): The keyboard listener object.
    """

    def __init__(self, key_to_monitor):
        """
        Initializes the HWButton class with the key to monitor and starts the listener.

        Args:
            key_to_monitor (str): The key to monitor for presses.
        """
        self._key_to_monitor = key_to_monitor
        self._callback = self._initial_callback  # Set a default callback
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()

    def _initial_callback(self):
        """
        Default callback function that prints a message.
        """
        print("No callback function set yet!")
        return self._initial_callback  # Return itself to avoid further errors

    def _on_press(self, key):
        """
        Method called on key press.

        Args:
            key (Key): The key that was pressed.
        """
        try:
            if key.char == self._key_to_monitor:
                self._callback()
        except AttributeError:
            pass

    def _on_release(self, key):
        """
        Method called on key release.

        Args:
            key (Key): The key that was released.
        """
        if key == keyboard.Key.esc:
            self._stop()

    def _stop(self):
        """
        Stops the keyboard listener.
        """
        self._listener.stop()
        self._listener.join()

    @property
    def callback(self):
        """
        Property to get the current callback function.

        Returns:
            function: The current callback function.
        """
        return self._callback

    @callback.setter
    def callback(self, new_callback):
        """
        Property to set a new callback function.

        Args:
            new_callback (function): The new callback function to set.
        """
        if not callable(new_callback):
            raise ValueError("Callback must be a callable function")
        self._callback = new_callback

    def stop_callback(self):
        """
        Sets the callback to a no-op function.
        """
        self._callback = self._no_callback

    def _no_callback(self):
        """
        A no-op callback function that prints a message.
        """
        print("No operation callback.")


# Example callback method in a different class
class AnotherClass:
    """
    A class to demonstrate callback functionality.
    """

    def __init__(self):
        pass

    def callback_method(self):
        """
        Example callback method.
        """
        print(f"Callback method in AnotherClass was pressed")

    def newcallback_method(self):
        """
        Another example callback method.
        """
        print(f"A New Callback method in AnotherClass was pressed")


# Example usage:
if __name__ == "__main__":
    another_instance = AnotherClass()
    button_monitor = HWButton("1")  # Pass method reference

    try:
        button_monitor.callback = another_instance.callback_method
        print("Press Enter to change callback function to AnotherClass.callback_method...\n")
        input()
        button_monitor.callback = another_instance.newcallback_method  # Change callback to method in AnotherClass

        print("Press Enter to set stop callback...\n")
        input()
        button_monitor.stop_callback  # Set the callback to a no-op function

        print("Press Enter to exit...\n")
        input()
    except KeyboardInterrupt:
        button_monitor._stop()
