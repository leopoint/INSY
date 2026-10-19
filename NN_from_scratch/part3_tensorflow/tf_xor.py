"""Trainiert ein XOR-Netz mit TensorFlow/Keras."""

from time import perf_counter

import numpy as np
import tensorflow as tf


# Gleiche Einstellungen wie beim eigenen Netz, damit der Vergleich fair ist.
SEED = 42
EPOCHS = 20_000
LEARNING_RATE = 0.1
STEPS_PER_EPOCH = 4          # 4 Beispiele pro Epoche, je ein Update (SGD)
STEPS_PER_EXECUTION = 4_000  # TensorFlow rechnet 4000 Updates am Stück -> viel schneller,
                             # am Ergebnis ändert das nichts
INPUTS = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float32)
TARGETS = np.array([[0], [1], [1], [0]], dtype=np.float32)


class LossPrinter(tf.keras.callbacks.Callback):
    """Zeigt nach je 1000 Trainingsrunden den mittleren Fehler an."""

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


def main():
    """Trainiert das 2-2-1-Netz und prueft alle vier XOR-Eingaben."""
    np.random.seed(SEED)
    tf.keras.utils.set_random_seed(SEED)
    tf.random.set_seed(SEED)

    # Netz aufbauen: 2 Eingänge -> 2 Hidden-Neuronen -> 1 Ausgang, überall Sigmoid.
    # "Dense" = jedes Neuron ist mit jedem Eingang verbunden (wie unser eigenes Layer).
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(2,)),
            tf.keras.layers.Dense(2, activation="sigmoid"),
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ]
    )
    # Lernverfahren festlegen: SGD mit Lernrate 0,1 und MSE als Fehlermaß.
    # Die Backpropagation rechnet TensorFlow automatisch, die müssen wir nicht selbst schreiben.
    model.compile(
        optimizer=tf.keras.optimizers.SGD(learning_rate=LEARNING_RATE),
        loss="mean_squared_error",
        steps_per_execution=STEPS_PER_EXECUTION,
    )
    # Datenstrom: Beispiele mischen, endlos wiederholen, immer nur EIN Beispiel pro Update
    # (batch(1)) -> genau wie Stochastic Gradient Descent im eigenen Netz.
    dataset = (
        tf.data.Dataset.from_tensor_slices((INPUTS, TARGETS))
        .shuffle(len(INPUTS), seed=SEED, reshuffle_each_iteration=True)
        .repeat()
        .batch(1)
    )

    # Training mit Zeitmessung (für den Vergleich in vergleich.md).
    print("TensorFlow XOR-Netz (2-2-1)")
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

    # Test: alle 4 Eingaben vorhersagen, mit 0,5 runden und mit dem Ziel vergleichen.
    predictions = model.predict(INPUTS, verbose=0).ravel()
    rounded = (predictions >= 0.5).astype(int)
    correct = int(np.sum(rounded == TARGETS.ravel()))
    for inputs, output, result, target in zip(INPUTS, predictions, rounded, TARGETS):
        print(f"  {inputs.astype(int).tolist()} -> {output:.3f} "
              f"(gerundet {result}, erwartet {int(target[0])})")

    print(f"Genauigkeit: {correct}/{len(INPUTS)}")
    print(f"Trainingszeit: {training_seconds:.2f} s")
    if correct != len(INPUTS):
        raise RuntimeError(
            "XOR wurde mit Seed 42 nicht vollstaendig gelernt; "
            "fuer einen weiteren Versuch den Seed aendern."
        )


if __name__ == "__main__":
    main()
