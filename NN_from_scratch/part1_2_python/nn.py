"""

Neuronales Netz from Scratch – 4AHITS
 
Teil 1, Step 1-3: Neuron, Layer, NeuralNetwork mit forward, predict,

                  backward und train, Speichern/Laden (JSON, TXT, C-Header)

Trainiert wird in train_xor.py und train_7seg.py.

"""

import json

import numpy as np
 
 
# Sigmoid und ihre Ableitung (bekommt z, den Wert VOR der Aktivierung)

# Sigmoid drückt jede Zahl in den Bereich 0..1: sigmoid(-5)=0,007, sigmoid(0)=0,5, sigmoid(5)=0,993.
# Dadurch kann man die Ausgabe wie "wie sehr ist das Segment an?" lesen.
def sigmoid(x):

    return 1.0 / (1.0 + np.exp(-x))
 
 
# Ableitung = Steigung der Sigmoid-Kurve. Sie sagt beim Lernen, wie stark eine kleine
# Änderung von z den Output verändert (Teil der Kettenregel in der Backpropagation).
def sigmoid_ableitung(x):

    s = sigmoid(x)

    return s * (1.0 - s)
 
 
# ------------------------------------------------------------------

# Step 1: Neuron

# ------------------------------------------------------------------

# Ein Neuron = kleinste Recheneinheit: gewichtete Summe der Eingänge + Bias, dann Sigmoid.
# Die Gewichte sind das "Wissen" des Neurons; beim Training werden sie Schritt für Schritt angepasst.
class Neuron:

    def __init__(self, num_inputs):

        # Zufällige Startwerte in [-1, 1]. Mit sehr kleinen Werten (* 0.01)

        # lernt XOR mit nur 2 Hidden-Neuronen in 20000 Epochen kaum.

        self.weights = np.random.uniform(-1.0, 1.0, num_inputs)

        self.bias = np.random.uniform(-1.0, 1.0)
 
        # Werte für die Rückwärtsrechnung

        self.last_inputs = None

        self.last_z = None

        self.last_output = None
 
    # Step 2: Vorwärtsrechnung eines Neurons
    # Beispiel: Eingabe [0,1], Gewichte [0,5, -0,3], Bias 0,1
    #   -> z = 0*0,5 + 1*(-0,3) + 0,1 = -0,2 -> sigmoid(-0,2) = 0,45
    # Eingabe, z und Output werden gemerkt, weil update() sie später zum Lernen braucht.

    def activate(self, inputs):

        inputs = np.asarray(inputs, dtype=float)

        self.last_inputs = inputs

        # Skalarprodukt + Bias

        self.last_z = np.dot(inputs, self.weights) + self.bias

        self.last_output = sigmoid(self.last_z)

        return self.last_output
 
    # Step 3: Gewichte und Bias anpassen
    # Idee: Das Neuron bekommt gesagt, wie falsch sein Output war (dL_dout).
    # Daraus rechnet es aus, in welche Richtung jedes Gewicht verschoben werden muss,
    # damit der Fehler kleiner wird, und geht ein kleines Stück (Lernrate) in diese Richtung.
    # Zusätzlich gibt es den Fehler an die Schicht davor weiter (Backpropagation).

    def update(self, dL_dout, learning_rate):

        """

        dL_dout: dJ/dA dieses Neurons

        Rückgabe: dJ/dinputs (Fehler für die vorherige Schicht)

        """

        # dJ/dZ = dJ/dA * dA/dZ

        dL_dz = dL_dout * sigmoid_ableitung(self.last_z)
 
        # Fehler für die vorherige Schicht mit den ALTEN Gewichten berechnen

        dL_dinputs = dL_dz * self.weights
 
        # Gradientenabstieg: dZ/dW = inputs, dZ/db = 1

        self.weights = self.weights - learning_rate * dL_dz * self.last_inputs

        self.bias = self.bias - learning_rate * dL_dz
 
        return dL_dinputs
 
 
# ------------------------------------------------------------------

# Step 1: Layer

# ------------------------------------------------------------------

# Eine Schicht = mehrere Neuronen nebeneinander, die alle dieselben Eingänge sehen.
# Beispiel 7-Segment: Hidden-Schicht mit 16 Neuronen, jedes bekommt die 4 Eingabebits.
class Layer:

    def __init__(self, num_neurons, num_inputs_per_neuron):

        self.num_inputs = num_inputs_per_neuron

        self.neurons = [Neuron(num_inputs_per_neuron) for _ in range(num_neurons)]
 
    # Step 2: Jedes Neuron rechnet seinen Output; zusammen ergeben sie den Output der Schicht
    # (z. B. 16 Werte), der dann die Eingabe für die nächste Schicht ist.

    def forward(self, inputs):

        return np.array([n.activate(inputs) for n in self.neurons])
 
    # Step 3: Jedes Neuron lernt aus seinem Fehler. Weil jeder Eingang an ALLE Neuronen
    # dieser Schicht geht, werden die zurückgegebenen Fehler aller Neuronen aufsummiert.

    def backward(self, errors, learning_rate):

        """

        errors[i] = dJ/dA_i (ein Wert pro Neuron dieser Schicht)

        Rückgabe:   dJ/dinputs, über alle Neuronen summiert

        """

        prev_errors = np.zeros(self.num_inputs)

        for neuron, err in zip(self.neurons, errors):

            prev_errors += neuron.update(err, learning_rate)

        return prev_errors
 
 
# ------------------------------------------------------------------

# Step 1: NeuralNetwork

# ------------------------------------------------------------------

# Das ganze Netz = Schichten hintereinander. Es kann vorhersagen (forward/predict),
# lernen (backward/train) und sich speichern/laden (JSON, TXT, C-Header).
class NeuralNetwork:

    def __init__(self, layer_sizes, learning_rate=0.1):

        """

        layer_sizes: z. B. [2, 2, 1] -> 2 Inputs, 2 Hidden-Neuronen, 1 Output

        """

        self.layer_sizes = list(layer_sizes)

        self.learning_rate = learning_rate

        self.layers = [

            Layer(layer_sizes[i], layer_sizes[i - 1])

            for i in range(1, len(layer_sizes))

        ]
 
    # Step 2: forward und predict
    # Die Eingabe läuft von vorne nach hinten durch alle Schichten:
    # 4 Bits -> Hidden-Schicht (16 Werte) -> Ausgabeschicht (7 Segmentwerte).

    def forward(self, inputs):

        output = np.asarray(inputs, dtype=float)

        for layer in self.layers:

            output = layer.forward(output)

        return output
 
    # Vorhersage = nur vorwärts rechnen, ohne zu lernen (wird nach dem Training benutzt).
    def predict(self, inputs):

        return self.forward(inputs)
 
    # Step 3: backward und train
    # Backpropagation: Fehler an der Ausgabe bestimmen und dann von HINTEN nach VORNE
    # durch alle Schichten zurückreichen; jede Schicht passt dabei ihre Gewichte an.
    # Beispiel: Ausgabe 0,8, Ziel 1 -> Fehler 0,8 - 1 = -0,2 -> Gewichte werden so
    # verschoben, dass die Ausgabe beim nächsten Mal etwas größer wird.

    def backward(self, outputs, targets):

        # Kostenfunktion J = 1/2 * (A - Y)^2  ->  dJ/dA = A - Y

        errors = outputs - np.asarray(targets, dtype=float)

        for layer in reversed(self.layers):

            errors = layer.backward(errors, self.learning_rate)
 
    def train(self, inputs, targets, epochs=20000, print_every=2000):

        """Stochastischer Gradientenabstieg: ein Update pro Trainingsbeispiel."""

        X = np.asarray(inputs, dtype=float)

        Y = np.asarray(targets, dtype=float)
 
        # Eine Epoche = jedes Trainingsbeispiel einmal gesehen. Die Reihenfolge wird jedes
        # Mal gemischt, damit das Netz nicht die Reihenfolge auswendig lernt.
        # Pro Beispiel: vorwärts rechnen -> Fehler messen (Loss) -> rückwärts lernen.
        for epoch in range(1, epochs + 1):

            loss = 0.0

            for i in np.random.permutation(len(X)):

                out = self.forward(X[i])

                loss += 0.5 * np.sum((out - Y[i]) ** 2)

                self.backward(out, Y[i])

            loss /= len(X)

            # Mittleren Fehler regelmäßig ausgeben: Er sollte immer kleiner werden.
            if epoch == 1 or epoch % print_every == 0:

                print(f"  Epoche {epoch:6d} | Loss: {loss:.6f}")

    def to_dict(self):
        """Wandelt die Netzstruktur und alle Parameter in JSON-Daten um."""
        return {
            "layer_sizes": self.layer_sizes,
            "learning_rate": self.learning_rate,
            "layers": [
                {
                    "weights": [neuron.weights.tolist() for neuron in layer.neurons],
                    "biases": [float(neuron.bias) for neuron in layer.neurons],
                }
                for layer in self.layers
            ],
        }

    def dump_json(self, filename):
        """Speichert das trainierte Netz dauerhaft als JSON-Datei."""
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2)

    @classmethod
    def load(cls, filename):
        """Laedt ein Netz aus einer zuvor gespeicherten JSON-Datei."""
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Zuerst ein leeres Netz mit derselben Größe bauen (hat Zufallsgewichte),
        # dann die Zufallswerte mit den gespeicherten Gewichten überschreiben.
        network = cls(data["layer_sizes"], data.get("learning_rate", 0.1))
        for layer, layer_data in zip(network.layers, data["layers"]):
            for neuron, weights, bias in zip(
                layer.neurons, layer_data["weights"], layer_data["biases"]
            ):
                neuron.weights = np.asarray(weights, dtype=float)
                neuron.bias = float(bias)
        return network

    def dump_txt(self, filename):
        """Speichert Gewichte in einem lesbaren, einfachen Zeilenformat."""
        # Jede Zeile beginnt mit einem Schlüsselwort (LAYERS, LAYER, NEURON, BIAS, WEIGHTS).
        # Vor jeder Liste steht ihre Größe -> das C-Programm (Part 4) weiß, wie viel
        # Speicher es braucht, und kann die Datei einfach Wort für Wort einlesen.
        # 17 Stellen Genauigkeit, damit beim Speichern nichts verloren geht.
        with open(filename, "w", encoding="utf-8") as file:
            file.write("NN 1\n")
            file.write(f"LAYERS {len(self.layers)}\n")
            file.write("SIZES " + " ".join(map(str, self.layer_sizes)) + "\n")
            for layer_index, layer in enumerate(self.layers):
                file.write(
                    f"LAYER {layer_index} {len(layer.neurons)} {layer.num_inputs}\n"
                )
                for neuron_index, neuron in enumerate(layer.neurons):
                    file.write(f"NEURON {neuron_index}\n")
                    file.write(f"BIAS {neuron.bias:.17g}\n")
                    file.write(
                        "WEIGHTS "
                        + " ".join(f"{weight:.17g}" for weight in neuron.weights)
                        + "\n"
                    )

    def dump_initfile(self, filename, model_name="network"):
        """Erzeugt einen C-Header mit den festen Netzparametern."""
        # Python schreibt hier C-Code: Die Gewichte werden zu "static const float"-Arrays,
        # die der Compiler direkt ins Programm (beim ESP32 in den Flash) einbaut.
        # Der Include-Guard (#ifndef/#define) verhindert, dass der Header doppelt eingebunden wird.
        prefix = "NN_" + "".join(char if char.isalnum() else "_" for char in model_name.upper())
        guard = f"{prefix}_H"
        with open(filename, "w", encoding="ascii") as file:
            file.write(f"#ifndef {guard}\n#define {guard}\n\n")
            file.write(f"#define {prefix}_NUM_LAYERS {len(self.layers)}\n")
            file.write(
                f"static const int {prefix}_LAYER_SIZES[] = "
                + "{" + ", ".join(map(str, self.layer_sizes)) + "};\n\n"
            )
            for layer_index, layer in enumerate(self.layers):
                file.write(
                    f"static const float {prefix}_BIASES_{layer_index}[] = {{\n    "
                    + ", ".join(f"{neuron.bias:.9g}f" for neuron in layer.neurons)
                    + "\n};\n"
                )
                file.write(
                    f"static const float {prefix}_WEIGHTS_{layer_index}[]["
                    f"{layer.num_inputs}] = {{\n"
                )
                for neuron in layer.neurons:
                    values = ", ".join(f"{weight:.9g}f" for weight in neuron.weights)
                    file.write(f"    {{{values}}},\n")
                file.write("};\n\n")
            # Init-Funktion: verbindet ein C-Netz (Structs aus nn.h) mit den Konstanten.
            # nn.h muss vor diesem Header eingebunden sein.
            file.write(f"static void {prefix.lower()}_init(Network *net)\n{{\n")
            file.write(f"    net->num_layers = {prefix}_NUM_LAYERS;\n")
            for layer_index, layer in enumerate(self.layers):
                file.write(
                    f"    nn_init_layer(&net->layers[{layer_index}], "
                    f"{len(layer.neurons)}, {layer.num_inputs}, "
                    f"&{prefix}_WEIGHTS_{layer_index}[0][0], "
                    f"{prefix}_BIASES_{layer_index});\n"
                )
            file.write("}\n\n")
            file.write(f"#endif  // {guard}\n")
