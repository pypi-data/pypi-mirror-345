# src/detection/typing_activity.py

import time
import threading
from pynput import keyboard

class TypingActivityDetector:
    """
    Détecte l’activité de frappe au clavier en écoutant
    les événements système via pynput.
    """

    def __init__(self, display_timeout: float = 1.0):
        """
        :param display_timeout: durée (en s) pendant laquelle
                                on considère qu'on tape après une touche
        """
        self.display_timeout = display_timeout
        self._last_event = 0.0
        self._lock = threading.Lock()
        # Listener non-bloquant
        self.listener = keyboard.Listener(on_press=self._on_key_press)

    def _on_key_press(self, key):
        """Callback appelé à chaque pression de touche."""
        with self._lock:
            self._last_event = time.time()

    def start(self):
        """Lance l'écoute en arrière-plan."""
        self.listener.start()

    def stop(self):
        """Arrête l'écoute."""
        self.listener.stop()

    def is_typing(self) -> bool:
        """
        True si une touche a été pressée il y a moins de display_timeout secondes.
        """
        with self._lock:
            return (time.time() - self._last_event) < self.display_timeout
