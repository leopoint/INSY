#include "nn.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Sigmoid wie in Python: drueckt jede Zahl in den Bereich 0..1. */
static float sigmoid(float x)
{
    return 1.0f / (1.0f + expf(-x));
}

/* Liest das naechste Wort aus der Datei und prueft, ob es das erwartete Schluesselwort ist. */
static int expect(FILE *f, const char *keyword)
{
    char word[32];
    if (fscanf(f, "%31s", word) != 1 || strcmp(word, keyword) != 0) {
        fprintf(stderr, "Formatfehler: '%s' erwartet\n", keyword);
        return 0;
    }
    return 1;
}

/* Baut das Netz aus 7seg.txt auf: Speicher mit malloc holen und Gewichte/Biases einlesen. */
int nn_load_txt(Network *net, const char *filename)
{
    FILE *f = fopen(filename, "r");
    if (f == NULL) {
        fprintf(stderr, "Datei nicht gefunden: %s\n", filename);
        return 0;
    }

    /* 1. Kopf der Datei lesen: "NN 1", "LAYERS 2", "SIZES 4 16 7" */
    int version, num_sizes, dummy;
    if (!expect(f, "NN") || fscanf(f, "%d", &version) != 1 ||
        !expect(f, "LAYERS") || fscanf(f, "%d", &net->num_layers) != 1 ||
        !expect(f, "SIZES") || net->num_layers < 1 || net->num_layers > 100) {
        fclose(f);
        return 0;
    }
    num_sizes = net->num_layers + 1;
    for (int i = 0; i < num_sizes; i++) {
        fscanf(f, "%d", &dummy); /* Groessen stehen unten bei LAYER nochmal */
    }

    /* 2. Speicher fuer alle Schichten holen (calloc = malloc, aber mit 0 gefuellt) */
    net->layers = calloc(net->num_layers, sizeof(Layer));
    for (int l = 0; l < net->num_layers; l++) {
        Layer *layer = &net->layers[l];
        /* 3. Pro Schicht: "LAYER <nr> <neuronen> <eingaenge>" lesen, dann Speicher
              fuer genau so viele Neuronen und Outputs holen */
        if (!expect(f, "LAYER") ||
            fscanf(f, "%d %d %d", &dummy, &layer->num_neurons, &layer->num_inputs) != 3) {
            fclose(f);
            return 0;
        }
        layer->neurons = calloc(layer->num_neurons, sizeof(Neuron));
        layer->outputs = calloc(layer->num_neurons, sizeof(float));

        /* 4. Pro Neuron: Speicher fuer die Gewichte holen, dann
              "NEURON <nr>", "BIAS <wert>" und "WEIGHTS <w1> <w2> ..." einlesen */
        for (int n = 0; n < layer->num_neurons; n++) {
            Neuron *neuron = &layer->neurons[n];
            neuron->num_inputs = layer->num_inputs;
            neuron->weights = malloc(layer->num_inputs * sizeof(float));
            if (!expect(f, "NEURON") || fscanf(f, "%d", &dummy) != 1 ||
                !expect(f, "BIAS") || fscanf(f, "%f", &neuron->bias) != 1 ||
                !expect(f, "WEIGHTS")) {
                fclose(f);
                return 0;
            }
            for (int w = 0; w < layer->num_inputs; w++) {
                fscanf(f, "%f", &neuron->weights[w]);
            }
        }
    }
    fclose(f);
    return 1;
}

/* Vorwaertsrechnung: Eingabe Schicht fuer Schicht durchs Netz schicken, gibt die letzten Outputs zurueck. */
const float *nn_forward(Network *net, const float *inputs)
{
    const float *current = inputs;
    for (int l = 0; l < net->num_layers; l++) {
        Layer *layer = &net->layers[l];
        /* Jedes Neuron: z = Bias + Summe(Gewicht * Eingang), dann Output = sigmoid(z) */
        for (int n = 0; n < layer->num_neurons; n++) {
            Neuron *neuron = &layer->neurons[n];
            float sum = neuron->bias;
            for (int i = 0; i < neuron->num_inputs; i++) {
                sum += neuron->weights[i] * current[i];
            }
            neuron->output = sigmoid(sum);
            layer->outputs[n] = neuron->output;
        }
        /* Die Outputs dieser Schicht sind die Eingaben der naechsten Schicht */
        current = layer->outputs;
    }
    return current;
}

/* Vorhersage: forward() und danach jede Ausgabe mit Schwelle 0,5 auf 0 oder 1 runden. */
void nn_predict(Network *net, const float *inputs, int *result)
{
    const float *out = nn_forward(net, inputs);
    Layer *last = &net->layers[net->num_layers - 1];
    for (int i = 0; i < last->num_neurons; i++) {
        result[i] = out[i] >= 0.5f ? 1 : 0;
    }
}

/* Gibt den ganzen mit malloc geholten Speicher wieder frei (in C nicht automatisch wie in Python). */
void nn_free(Network *net)
{
    for (int l = 0; l < net->num_layers; l++) {
        Layer *layer = &net->layers[l];
        for (int n = 0; n < layer->num_neurons; n++) {
            free(layer->neurons[n].weights);
        }
        free(layer->neurons);
        free(layer->outputs);
    }
    free(net->layers);
    net->layers = NULL;
    net->num_layers = 0;
}
