#include "mel_filter_bank.h"

void mel_filter_apply(q15_t *fft_array, q15_t *mel_array, size_t fft_len, size_t mel_len) {
    arm_fill_q15(0, mel_array, mel_len);
    for (size_t i = 0; i < mel_len; i++) {
        mel_trian_t mel_triangle = mel_triangles[i];
        arm_dot_prod_q15(&fft_array[mel_triangle.idx_offset], mel_triangle.values, mel_triangle.triangle_len, &mel_array[i]);
    }
}

/*
Arm_math useful functions:
- arm_fill_q15
- arm_scale_q15
- arm_offset_q15
- arm_mult_q15
- arm_add_q15
- arm_sub_q15
- arm_dot_prod_q15
- arm_abs_q15
- arm_negate_q15
- arm_shift_q15
- arm_copy_q15
*/