"""Trainiert den 7-Segment-Decoder (4-16-7) mit TensorFlow/Keras."""

from time import perf_counter

import numpy as np
import tensorflow as tf


# Gleiche Einstellungen wie beim eigenen Netz, damit der Vergleich fair ist.
SEED = 42
EPOCHS = 20_000
LEARNING_RATE = 0.1
STEPS_PER_EPOCH = 10           # 10 Ziffern pro Epoche, je ein Update (SGD)
STEPS_PER_EXECUTION = 10_000   # TensorFlow rechnet 10000 Updates am Stück -> viel schneller,
                               # am Ergebnis ändert das nichts

# Trainingsdaten wie in train_7seg.py: 4 Bits pro Ziffer -> 7 Segmente a..g.
INPUTS = np.array(
    [
        [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 0, 1, 1], [0, 1, 0, 0],
        [0, 1, 0, 1], [0, 1, 1, 0], [0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 1],
    ],
    dtype=np.float32,
)
TARGETS = np.array(
    [
        [1, 1, 1, 1, 1, 1, 0], [0, 1, 1, 0, 0, 0, 0], [1, 1, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 0, 0, 1], [0, 1, 1, 0, 0, 1, 1], [1, 0, 1, 1, 0, 1, 1],
        [1, 0, 1, 1, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 1],
    ],
    dtype=np.float32,
)


class LossPrinter(tf.keras.callbacks.Callback):
    """Zeigt nach je 1000 Epochen den mittleren Fehler an."""

    def __init__(self):
        super().__init__()
        self.completed_steps = 0

    def on_train_batch_end(self, batch, logs=None):
        del batch, logs
        self.completed_steps += STEPS_PER_EXECUTION
        if self.completed_steps % (1000 * STEPS_PER_EPOCH) == 0:
            loss = tf.reduce_mean(tf.square(self.model(INPUTS) - TARGETS))
            completed_epochs = self.completed_steps // STEPS_PER_EPOCH
            print(f"  Epoche {completed_epochs:6d} | Loss: {loss.numpy():.6f}")


def render_digit(segments):
    """Zeigt die sieben Segmentwerte als ASCII-Ziffer an."""
    a, b, c, d, e, f, g = segments
    on = lambda value: "---" if value else "   "
    side = lambda value: "|" if value else " "
    return "\n".join(
        [
            f" {on(a)} ",
            f"{side(f)}   {side(b)}",
            f" {on(g)} ",
            f"{side(e)}   {side(c)}",
            f" {on(d)} ",
        ]
    )


def main():
    """Trainiert das 4-16-7-Netz und prueft alle zehn Ziffern."""
    np.random.seed(SEED)
    tf.keras.utils.set_random_seed(SEED)
    tf.random.set_seed(SEED)

    # Netz aufbauen: 4 Eingänge -> 16 Hidden -> 7 Ausgänge, überall Sigmoid.
    # 16 statt "e.g. 10" aus dem PDF, damit es genau so groß ist wie unser eigenes Netz.
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(4,)),
            tf.keras.layers.Dense(16, activation="sigmoid"),
            tf.keras.layers.Dense(7, activation="sigmoid"),
        ]
    )
    # Lernverfahren: SGD mit Lernrate 0,1 und MSE; Backpropagation macht TensorFlow selbst.
    model.compile(
        optimizer=tf.keras.optimizers.SGD(learning_rate=LEARNING_RATE),
        loss="mean_squared_error",
        steps_per_execution=STEPS_PER_EXECUTION,
    )
    # Datenstrom: mischen, endlos wiederholen, ein Beispiel pro Update (= SGD).
    dataset = (
        tf.data.Dataset.from_tensor_slices((INPUTS, TARGETS))
        .shuffle(len(INPUTS), seed=SEED, reshuffle_each_iteration=True)
        .repeat()
        .batch(1)
    )

    # Training mit Zeitmessung (für den Vergleich in vergleich.md).
    print("TensorFlow 7-Segment-Netz (4-16-7)")
    start = perf_counter()
    model.fit(
        dataset,
        epochs=1,
        steps_per_epoch=EPOCHS * STEPS_PER_EPOCH,
        shuffle=False,
        verbose=0,
        callbacks=[LossPrinter()],
    )
    training_seconds = perf_counter() - start

    # Test: alle 10 Ziffern vorhersagen, mit 0,5 runden, Endfehler (MSE) berechnen
    # und richtige Segmente/Ziffern zählen.
    predictions = model.predict(INPUTS, verbose=0)
    rounded = (predictions >= 0.5).astype(int)
    final_loss = float(np.mean((predictions - TARGETS) ** 2))
    correct_segments = int(np.sum(rounded == TARGETS))
    correct_digits = 0
    for digit, (result, target) in enumerate(zip(rounded, TARGETS)):
        ok = result.tolist() == target.astype(int).tolist()
        correct_digits += ok
        print(f"\nZiffer {digit}: {'OK' if ok else 'FALSCH'}")
        print(f"  Ausgabe: {result.tolist()}")
        print(render_digit(result))

    print(f"\nZiffern richtig: {correct_digits}/10")
    print(f"Segment-Genauigkeit: {correct_segments}/{TARGETS.size}")
    print(f"End-Loss: {final_loss:.6f}")
    print(f"Trainingszeit: {training_seconds:.2f} s")


if __name__ == "__main__":
    main()
