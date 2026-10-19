#ifndef NN_H
#define NN_H

/* Ein Neuron: eigene Gewichte (eins pro Eingang), ein Bias und der letzte Output. */
typedef struct {
    int num_inputs;
    float *weights;
    float bias;
    float output;
} Neuron;

/* Eine Schicht: Liste von Neuronen plus Array mit allen Outputs (Eingabe fuer die naechste Schicht). */
typedef struct {
    int num_neurons;
    int num_inputs;
    Neuron *neurons;
    float *outputs;
} Layer;

/* Das ganze Netz: Liste von Schichten. */
typedef struct {
    int num_layers;
    Layer *layers;
} Network;

/* Funktionen aus nn.c (hier nur angekuendigt, damit main.c sie aufrufen kann) */
int nn_load_txt(Network *net, const char *filename);
const float *nn_forward(Network *net, const float *inputs);
void nn_predict(Network *net, const float *inputs, int *result);
void nn_free(Network *net);

#endif
