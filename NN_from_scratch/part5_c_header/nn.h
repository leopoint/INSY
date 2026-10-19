#ifndef NN_H
#define NN_H

/* Feste Obergrenzen statt malloc: der Speicher steht schon beim Kompilieren fest. */
#define NN_MAX_LAYERS 4
#define NN_MAX_NEURONS 16

/* Ein Neuron: zeigt auf seine Gewichte im Header (konstant, liegen im Flash), dazu Bias und letzter Output. */
typedef struct {
    int num_inputs;
    const float *weights;
    float bias;
    float output;
} Neuron;

/* Eine Schicht: feste Liste von Neuronen plus Array mit allen Outputs. */
typedef struct {
    int num_neurons;
    int num_inputs;
    Neuron neurons[NN_MAX_NEURONS];
    float outputs[NN_MAX_NEURONS];
} Layer;

/* Das ganze Netz: feste Liste von Schichten. */
typedef struct {
    int num_layers;
    Layer layers[NN_MAX_LAYERS];
} Network;

/* Funktionen aus nn.c (hier nur angekuendigt, damit main.c und 7seg_net.h sie aufrufen koennen) */
void nn_init_layer(Layer *layer, int num_neurons, int num_inputs,
                   const float *weights, const float *biases);
const float *nn_forward(Network *net, const float *inputs);
void nn_predict(Network *net, const float *inputs, int *result);

#endif
