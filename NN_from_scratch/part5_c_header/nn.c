#include "nn.h"

#include <math.h>

/* Sigmoid wie in Python: drueckt jede Zahl in den Bereich 0..1. */
static float sigmoid(float x)
{
    return 1.0f / (1.0f + expf(-x));
}

/* Verbindet eine Schicht mit den konstanten Gewichten/Biases aus dem Header (nichts wird kopiert). */
void nn_init_layer(Layer *layer, int num_neurons, int num_inputs,
                   const float *weights, const float *biases)
{
    layer->num_neurons = num_neurons;
    layer->num_inputs = num_inputs;
    for (int n = 0; n < num_neurons; n++) {
        layer->neurons[n].num_inputs = num_inputs;
        /* Die Gewichte liegen im Header als eine lange Zahlenreihe: Neuron 0 hat die
           ersten num_inputs Werte, Neuron 1 die naechsten usw. -> Zeiger auf "seine" Zeile */
        layer->neurons[n].weights = &weights[n * num_inputs];
        layer->neurons[n].bias = biases[n];
        layer->neurons[n].output = 0.0f;
    }
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
