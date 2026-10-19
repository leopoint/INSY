#include <stdio.h>

#include "nn.h"

/* Testdaten: die 10 Ziffern als 4 Bits und die erwarteten Segmente a..g (gleiche Tabelle wie in Python) */
static const float INPUTS[10][4] = {
    {0, 0, 0, 0}, {0, 0, 0, 1}, {0, 0, 1, 0}, {0, 0, 1, 1}, {0, 1, 0, 0},
    {0, 1, 0, 1}, {0, 1, 1, 0}, {0, 1, 1, 1}, {1, 0, 0, 0}, {1, 0, 0, 1},
};
static const int EXPECTED[10][7] = {
    {1, 1, 1, 1, 1, 1, 0}, {0, 1, 1, 0, 0, 0, 0}, {1, 1, 0, 1, 1, 0, 1},
    {1, 1, 1, 1, 0, 0, 1}, {0, 1, 1, 0, 0, 1, 1}, {1, 0, 1, 1, 0, 1, 1},
    {1, 0, 1, 1, 1, 1, 1}, {1, 1, 1, 0, 0, 0, 0}, {1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 0, 1, 1},
};

/* Zeichnet die 7 Segmente (a b c d e f g) als ASCII-Ziffer. */
static void render_digit(const int *s)
{
    printf(" %s \n", s[0] ? "---" : "   ");
    printf("%c   %c\n", s[5] ? '|' : ' ', s[1] ? '|' : ' ');
    printf(" %s \n", s[6] ? "---" : "   ");
    printf("%c   %c\n", s[4] ? '|' : ' ', s[2] ? '|' : ' ');
    printf(" %s \n", s[3] ? "---" : "   ");
}

/* Laedt das Netz aus der .txt-Datei und testet alle zehn Ziffern. */
int main(int argc, char **argv)
{
    /* Pfad zur Gewichtsdatei: Standard ist ../models/7seg.txt, kann aber als Argument uebergeben werden */
    const char *path = argc > 1 ? argv[1] : "../models/7seg.txt";
    Network net;
    if (!nn_load_txt(&net, path)) {
        return 1;
    }
    printf("Netz geladen aus %s (%d Schichten)\n", path, net.num_layers);

    int correct_digits = 0, correct_segments = 0;
    /* Jede Ziffer: Rohwerte holen (nn_forward), auf 0/1 runden (nn_predict),
       Segment fuer Segment mit der Tabelle vergleichen und ausgeben */
    for (int d = 0; d < 10; d++) {
        int result[7];
        const float *raw = nn_forward(&net, INPUTS[d]);
        nn_predict(&net, INPUTS[d], result);

        int ok = 1;
        for (int i = 0; i < 7; i++) {
            if (result[i] == EXPECTED[d][i]) correct_segments++;
            else ok = 0;
        }
        correct_digits += ok;

        printf("\nZiffer %d: %s\n  Rohwerte:", d, ok ? "OK" : "FALSCH");
        for (int i = 0; i < 7; i++) printf(" %.3f", raw[i]);
        printf("\n  Ausgabe:  ");
        for (int i = 0; i < 7; i++) printf(" %d", result[i]);
        printf("\n");
        render_digit(result);
    }

    printf("\nZiffern richtig: %d/10\n", correct_digits);
    printf("Segment-Genauigkeit: %d/70\n", correct_segments);
    nn_free(&net); /* malloc-Speicher zurueckgeben */
    /* Rueckgabewert 0 = alles richtig, 1 = mindestens ein Fehler */
    return correct_digits == 10 ? 0 : 1;
}
