#include <arm_math.h>
#include <stdbool.h> // Include stdbool.h for the boolean data type

// Functions to convert between Hz and Mel scales

q15_t hz_to_mel(q15_t f_hz) {
    return 2595 * log(1 + f_hz / 700) / log(10);
}

q15_t mel_to_hz(q15_t f_mel) {
    return 700 * (pow(10, f_mel / 2595) - 1);
}

// Function to calculate the position of a triangle

typedef struct mel_triangle {
    q15_t center;
    q15_t width;
    q15_t height;
} mel_triangle;

q15_t triangle_pos(q15_t x, mel_triangle* triangle) {
    return max(0, 1 - abs(x - triangle->center) / triangle->width) * triangle->height;
}

/**
 * @brief Vectorized version of the triangle_pos function
 *
 * @param [x] Input positions (n_dft_len)
 */
void triangle_pos_vector(q15_t* x, mel_triangle* triangle, size_t n_dft_len) {
    arm_sub_q15(x, &triangle->center, x, n_dft_len); // Position the triangle
    arm_abs_q15(x, x, n_dft_len); // Calculate the absolute value (mirror)
    arm_div_q15(x, &triangle->width, x, n_dft_len); // Divide by the width
    arm_negate_q15(x, x, n_dft_len); // Negate the result
    arm_add_q15(x, &triangle->height, x, n_dft_len); // Add the height
    arm_clip_q15(x, 0, 1, x, n_dft_len); // Clip the result
    arm_scale_q15(x, triangle->height, 0, x, n_dft_len); // Scale the result
 } // TODO : REpair the bug where the height and stuff is 1D

bool test_triangle_properties() {
    mel_triangle triangle1 = { 0, 1, 1 };
    mel_triangle triangle2 = { 0, 1, 0.5 };
    mel_triangle triangle3 = { 0, 0.5, 1 };
    mel_triangle triangle4 = { 0, 2, 1 };
    mel_triangle triangle5 = { 0, 1, 2 };

    int x = 0;
    q15_t accumulator1 = 0;
    q15_t accumulator2 = 0;
    q15_t accumulator3 = 0;
    q15_t accumulator4 = 0;
    q15_t accumulator5 = 0;

    for (int i = -100; i <= 100; ++i) {
        q15_t y1 = triangle_pos(i, &triangle1);
        q15_t y2 = triangle_pos(i, &triangle2);
        q15_t y3 = triangle_pos(i, &triangle3);
        q15_t y4 = triangle_pos(i, &triangle4);
        q15_t y5 = triangle_pos(i, &triangle5);

        accumulator1 += y1;
        accumulator2 += y2;
        accumulator3 += y3;
        accumulator4 += y4;
        accumulator5 += y5;
    }

    // Test the area of the triangle
    bool tests = true;
    tests &= accumulator1 == triangle1.width*triangle1.height/2;
    tests &= accumulator2 == triangle2.width*triangle2.height/2;
    tests &= accumulator3 == triangle3.width*triangle3.height/2;
    tests &= accumulator4 == triangle4.width*triangle4.height/2;
    tests &= accumulator5 == triangle5.width*triangle5.height/2;

    return tests;
}

// Function to initialize the mel triangles

mel_triangle* init_triangles_mel(int f_ssampling, int n_mel_len) {
    mel_triangle* triangles = (mel_triangle*)malloc(n_mel_len * sizeof(mel_triangle));
    q15_t f_mel_min = hz_to_mel(0);
    q15_t f_mel_max = hz_to_mel(f_ssampling / 2);
    q15_t f_mel_step = (f_mel_max - f_mel_min) / (n_mel_len + 1);

    for (int i = 0; i < n_mel_len; ++i) {
        q15_t f_mel_center = f_mel_min + f_mel_step * (i + 1);
        q15_t f_hz_center  = mel_to_hz(f_mel_center);
        q15_t f_hz_width   = mel_to_hz(f_mel_center + f_mel_step) - f_hz_center;
        q15_t f_hz_height  = 2 / f_hz_width;

        triangles[i].center = f_hz_center;
        triangles[i].width = f_hz_width;
        triangles[i].height = f_hz_height;
    }

    return triangles;
}

// Function to calculate the mel spectrogram of 1 window

void mel_spectrogram(q15_t* window, q15_t* mel_window, mel_triangle* triangles, int n_mel_len) {
    for (int i = 0; i < n_mel_len; ++i) {
        mel_window[i] = 0;
        for (int j = 0; j < 256; ++j) {
            mel_window[i] += triangle_pos(j, &triangles[i]) * window[j];
        }
    }
}

// Function to calculate the mel spectrogram of the whole signal

void mel_spectrogram_signal(q15_t* signal, q15_t* mel_signal, mel_triangle* triangles, int n_mel_len, int n_signal_len) {
    q15_t* window = (q15_t*)malloc(256 * sizeof(q15_t));
    q15_t* mel_window = (q15_t*)malloc(n_mel_len * sizeof(q15_t));

    for (int i = 0; i < n_signal_len; ++i) {
        for (int j = 0; j < 256; ++j) {
            window[j] = signal[i + j];
        }

        mel_spectrogram(window, mel_window, triangles, n_mel_len);

        for (int j = 0; j < n_mel_len; ++j) {
            mel_signal[i * n_mel_len + j] = mel_window[j];
        }
    }
}