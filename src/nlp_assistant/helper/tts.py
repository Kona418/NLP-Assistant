import pyttsx3

# Engine initialisieren
engine = pyttsx3.init()

# Optional: Eigenschaften anpassen (Geschwindigkeit, Lautstärke)
engine.setProperty('rate', 150)    # Standard ist oft zu schnell
engine.setProperty('volume', 0.9)  # 0.0 bis 1.0
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Text sprechen
engine.say("Ich schalte die Deckenlampe an!")

# Wichtig: Blockiert das Skript, bis das Sprechen fertig ist
engine.runAndWait()