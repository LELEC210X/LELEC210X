/* Rijndael code
 * August ’01
 *
 * author: Vincent Rijmen,
 * This code is based on the official reference code
 * by Paulo Barreto and Vincent Rijmen
 *
 * This code is placed in the public domain.
 * Without any warranty of fitness for any purpose.
 *
 * Extracted from
 *   Joan Daemen, Vincent Rijmen:
 *   The Design of Rijndael: AES - The Advanced Encryption Standard. Information
 *   Security and Cryptography, Springer 2002, ISBN 3-540-42580-2
 * Available at https://cs.ru.nl/~joan/papers/JDA_VRI_Rijndael_2002.pdf
 *
 * Edited by Gaetan Cassiers June 2021:
 *     remove main function and provide AES128 encrypt function.
 *     make KC, BC and ROUNDS constant.
 *
 * Cautionary note to students: This code is a pretty straightforward
 * implementation of Rijndael, which is the original name of the block cipher
 * that eventually became the AES (actually, the AES with 128-bit key is a
 * special case of Rijndael).
 * When reading this code, please keep in mind that this is written with
 * simplicity and compatibility with old compilers in mind, and not performance
 * or robustness.  Some design choices (e.g. usage of global variables) are not
 * recommended best C coding practices.
 */
#include <string.h>
typedef unsigned char word8;
typedef unsigned int word32;
/* The tables Logtable and Alogtable are used to perform
 * multiplications in GF(256)
 * Alog means inverse of the log function, such that alog(log(x) + log(y)) =
 * x*y (in GF(256)) for every non-zero x and y.
 */
word8 Logtable[256] = {
    0,   0,   25,  1,   50,  2,   26,  198, 75,  199, 27,  104, 51,  238, 223,
    3,   100, 4,   224, 14,  52,  141, 129, 239, 76,  113, 8,   200, 248, 105,
    28,  193, 125, 194, 29,  181, 249, 185, 39,  106, 77,  228, 166, 114, 154,
    201, 9,   120, 101, 47,  138, 5,   33,  15,  225, 36,  18,  240, 130, 69,
    53,  147, 218, 142, 150, 143, 219, 189, 54,  208, 206, 148, 19,  92,  210,
    241, 64,  70,  131, 56,  102, 221, 253, 48,  191, 6,   139, 98,  179, 37,
    226, 152, 34,  136, 145, 16,  126, 110, 72,  195, 163, 182, 30,  66,  58,
    107, 40,  84,  250, 133, 61,  186, 43,  121, 10,  21,  155, 159, 94,  202,
    78,  212, 172, 229, 243, 115, 167, 87,  175, 88,  168, 80,  244, 234, 214,
    116, 79,  174, 233, 213, 231, 230, 173, 232, 44,  215, 117, 122, 235, 22,
    11,  245, 89,  203, 95,  176, 156, 169, 81,  160, 127, 12,  246, 111, 23,
    196, 73,  236, 216, 67,  31,  45,  164, 118, 123, 183, 204, 187, 62,  90,
    251, 96,  177, 134, 59,  82,  161, 108, 170, 85,  41,  157, 151, 178, 135,
    144, 97,  190, 220, 252, 188, 149, 207, 205, 55,  63,  91,  209, 83,  57,
    132, 60,  65,  162, 109, 71,  20,  42,  158, 93,  86,  242, 211, 171, 68,
    17,  146, 217, 35,  32,  46,  137, 180, 124, 184, 38,  119, 153, 227, 165,
    103, 74,  237, 222, 197, 49,  254, 24,  13,  99,  140, 128, 192, 247, 112,
    7};

word8 Alogtable[256] = {
    1,   3,   5,   15,  17,  51,  85,  255, 26,  46,  114, 150, 161, 248, 19,
    53,  95,  225, 56,  72,  216, 115, 149, 164, 247, 2,   6,   10,  30,  34,
    102, 170, 229, 52,  92,  228, 55,  89,  235, 38,  106, 190, 217, 112, 144,
    171, 230, 49,  83,  245, 4,   12,  20,  60,  68,  204, 79,  209, 104, 184,
    211, 110, 178, 205, 76,  212, 103, 169, 224, 59,  77,  215, 98,  166, 241,
    8,   24,  40,  120, 136, 131, 158, 185, 208, 107, 189, 220, 127, 129, 152,
    179, 206, 73,  219, 118, 154, 181, 196, 87,  249, 16,  48,  80,  240, 11,
    29,  39,  105, 187, 214, 97,  163, 254, 25,  43,  125, 135, 146, 173, 236,
    47,  113, 147, 174, 233, 32,  96,  160, 251, 22,  58,  78,  210, 109, 183,
    194, 93,  231, 50,  86,  250, 21,  63,  65,  195, 94,  226, 61,  71,  201,
    64,  192, 91,  237, 44,  116, 156, 191, 218, 117, 159, 186, 213, 100, 172,
    239, 42,  126, 130, 157, 188, 223, 122, 142, 137, 128, 155, 182, 193, 88,
    232, 35,  101, 175, 234, 37,  111, 177, 200, 67,  197, 84,  252, 31,  33,
    99,  165, 244, 7,   9,   27,  45,  119, 153, 176, 203, 70,  202, 69,  207,
    74,  222, 121, 139, 134, 145, 168, 227, 62,  66,  198, 81,  243, 14,  18,
    54,  90,  238, 41,  123, 141, 140, 143, 138, 133, 148, 167, 242, 13,  23,
    57,  75,  221, 124, 132, 151, 162, 253, 28,  36,  108, 180, 199, 82,  246,
    1};
word8 S[256] = {
    99,  124, 119, 123, 242, 107, 111, 197, 48,  1,   103, 43,  254, 215, 171,
    118, 202, 130, 201, 125, 250, 89,  71,  240, 173, 212, 162, 175, 156, 164,
    114, 192, 183, 253, 147, 38,  54,  63,  247, 204, 52,  165, 229, 241, 113,
    216, 49,  21,  4,   199, 35,  195, 24,  150, 5,   154, 7,   18,  128, 226,
    235, 39,  178, 117, 9,   131, 44,  26,  27,  110, 90,  160, 82,  59,  214,
    179, 41,  227, 47,  132, 83,  209, 0,   237, 32,  252, 177, 91,  106, 203,
    190, 57,  74,  76,  88,  207, 208, 239, 170, 251, 67,  77,  51,  133, 69,
    249, 2,   127, 80,  60,  159, 168, 81,  163, 64,  143, 146, 157, 56,  245,
    188, 182, 218, 33,  16,  255, 243, 210, 205, 12,  19,  236, 95,  151, 68,
    23,  196, 167, 126, 61,  100, 93,  25,  115, 96,  129, 79,  220, 34,  42,
    144, 136, 70,  238, 184, 20,  222, 94,  11,  219, 224, 50,  58,  10,  73,
    6,   36,  92,  194, 211, 172, 98,  145, 149, 228, 121, 231, 200, 55,  109,
    141, 213, 78,  169, 108, 86,  244, 234, 101, 122, 174, 8,   186, 120, 37,
    46,  28,  166, 180, 198, 232, 221, 116, 31,  75,  189, 139, 138, 112, 62,
    181, 102, 72,  3,   246, 14,  97,  53,  87,  185, 134, 193, 29,  158, 225,
    248, 152, 17,  105, 217, 142, 148, 155, 30,  135, 233, 206, 85,  40,  223,
    140, 161, 137, 13,  191, 230, 66,  104, 65,  153, 45,  15,  176, 84,  187,
    22};
word8 Si[256] = {
    82,  9,   106, 213, 48,  54,  165, 56,  191, 64,  163, 158, 129, 243, 215,
    251, 124, 227, 57,  130, 155, 47,  255, 135, 52,  142, 67,  68,  196, 222,
    233, 203, 84,  123, 148, 50,  166, 194, 35,  61,  238, 76,  149, 11,  66,
    250, 195, 78,  8,   46,  161, 102, 40,  217, 36,  178, 118, 91,  162, 73,
    109, 139, 209, 37,  114, 248, 246, 100, 134, 104, 152, 22,  212, 164, 92,
    204, 93,  101, 182, 146, 108, 112, 72,  80,  253, 237, 185, 218, 94,  21,
    70,  87,  167, 141, 157, 132, 144, 216, 171, 0,   140, 188, 211, 10,  247,
    228, 88,  5,   184, 179, 69,  6,   208, 44,  30,  143, 202, 63,  15,  2,
    193, 175, 189, 3,   1,   19,  138, 107, 58,  145, 17,  65,  79,  103, 220,
    234, 151, 242, 207, 206, 240, 180, 230, 115, 150, 172, 116, 34,  231, 173,
    53,  133, 226, 249, 55,  232, 28,  117, 223, 110, 71,  241, 26,  113, 29,
    41,  197, 137, 111, 183, 98,  14,  170, 24,  190, 27,  252, 86,  62,  75,
    198, 210, 121, 32,  154, 219, 192, 254, 120, 205, 90,  244, 31,  221, 168,
    51,  136, 7,   199, 49,  177, 18,  16,  89,  39,  128, 236, 95,  96,  81,
    127, 169, 25,  181, 74,  13,  45,  229, 122, 159, 147, 201, 156, 239, 160,
    224, 59,  77,  174, 42,  245, 176, 200, 235, 187, 60,  131, 83,  153, 97,
    23,  43,  4,   126, 186, 119, 214, 38,  225, 105, 20,  99,  85,  33,  12,
    125};

word32 RC[30] = {0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B,
                 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A, 0x2F, 0x5E, 0xBC, 0x63,
                 0xC6, 0x97, 0x35, 0x6A, 0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5};
#define MAXBC 8
#define MAXKC 8
#define MAXROUNDS 14
static word8 shifts[5][4] = {
		{0, 1, 2, 3},
		{0, 1, 2, 3},
		{0, 1, 2, 3},
		{0, 1, 2, 4},
		{0, 1, 3, 4}
};
static const int BC = 4;
static const int KC = 4;
static const int ROUNDS = 10;

word8 mul(word8 a, word8 b) {
  /* multiply two elements of GF(256)
   * required for MixColumns and InvMixColumns
   */
  if (a && b)
    return Alogtable[(Logtable[a] + Logtable[b]) % 255];
  else
    return 0;
}
void AddRoundKey(word8 a[4][MAXBC], word8 rk[4][MAXBC]) {
  /* XOR corresponding text input and round key input bytes
   */
  int i, j;
  for (i = 0; i < 4; i++)
    for (j = 0; j < BC; j++)
      a[i][j] ^= rk[i][j];
}
void SubBytes(word8 a[4][MAXBC], word8 box[256]) {
  /* Replace every byte of the input by the byte at that place
   * in the non-linear S-box
   */
  int i, j;
  for (i = 0; i < 4; i++)
    for (j = 0; j < BC; j++)
      a[i][j] = box[a[i][j]];
}

void ShiftRows(word8 a[4][MAXBC], word8 d) {
  /* Row 0 remains unchanged
   * The other three rows are shifted a variable amount
   */
  word8 tmp[MAXBC];
  int i, j;
  if (d == 0) {
    for (i = 1; i < 4; i++) {
      for (j = 0; j < BC; j++)
        tmp[j] = a[i][(j + shifts[BC - 4][i]) % BC];
      for (j = 0; j < BC; j++)
        a[i][j] = tmp[j];
    }
  } else {
    for (i = 1; i < 4; i++) {
      for (j = 0; j < BC; j++)
        tmp[j] = a[i][(BC + j - shifts[BC - 4][i]) % BC];
      for (j = 0; j < BC; j++)
        a[i][j] = tmp[j];
    }
  }
}
void MixColumns(word8 a[4][MAXBC]) {
  /* Mix the four bytes of every column in a linear way
   */
  word8 b[4][MAXBC];
  int i, j;
  for (j = 0; j < BC; j++)
    for (i = 0; i < 4; i++)
      b[i][j] = mul(2, a[i][j]) ^ mul(3, a[(i + 1) % 4][j]) ^
                a[(i + 2) % 4][j] ^ a[(i + 3) % 4][j];
  for (i = 0; i < 4; i++)
    for (j = 0; j < BC; j++)
      a[i][j] = b[i][j];
}
void InvMixColumns(word8 a[4][MAXBC]) {
  /* Mix the four bytes of every column in a linear way
   * This is the opposite operation of Mixcolumns
   */
  word8 b[4][MAXBC];
  int i, j;
  for (j = 0; j < BC; j++)
    for (i = 0; i < 4; i++)
      b[i][j] = mul(0xe, a[i][j]) ^ mul(0xb, a[(i + 1) % 4][j]) ^
                mul(0xd, a[(i + 2) % 4][j]) ^ mul(0x9, a[(i + 3) % 4][j]);
  for (i = 0; i < 4; i++)
    for (j = 0; j < BC; j++)
      a[i][j] = b[i][j];
}
int KeyExpansion(word8 k[4][MAXKC], word8 W[MAXROUNDS + 1][4][MAXBC]) {
  /* Calculate the required round keys
   */
  int i, j, t, RCpointer = 1;
  word8 tk[4][MAXKC];
  for (j = 0; j < KC; j++)
    for (i = 0; i < 4; i++)
      tk[i][j] = k[i][j];
  t = 0;
  /* copy values into round key array */
  for (j = 0; (j < KC) && (t < (ROUNDS + 1) * BC); j++, t++)
    for (i = 0; i < 4; i++)
      W[t / BC][i][t % BC] = tk[i][j];
  while (t < (ROUNDS + 1) * BC) {
    /* while not enough round key material calculated,
     * calculate new values
     */
    for (i = 0; i < 4; i++)
      tk[i][0] ^= S[tk[(i + 1) % 4][KC - 1]];
    tk[0][0] ^= RC[RCpointer++];

    if (KC <= 6)
      for (j = 1; j < KC; j++)
        for (i = 0; i < 4; i++)
          tk[i][j] ^= tk[i][j - 1];
    else {
      for (j = 1; j < 4; j++)
        for (i = 0; i < 4; i++)
          tk[i][j] ^= tk[i][j - 1];
      for (i = 0; i < 4; i++)
        tk[i][4] ^= S[tk[i][3]];
      for (j = 5; j < KC; j++)
        for (i = 0; i < 4; i++)
          tk[i][j] ^= tk[i][j - 1];
    }
    /* copy values into round key array */
    for (j = 0; (j < KC) && (t < (ROUNDS + 1) * BC); j++, t++)
      for (i = 0; i < 4; i++)
        W[t / BC][i][t % BC] = tk[i][j];
  }
  return 0;
}
int Encrypt(word8 a[4][MAXBC], word8 rk[MAXROUNDS + 1][4][MAXBC]) {
  /* Encryption of one block.
   */
  int r;
  /* begin with a key addition
   * */
  AddRoundKey(a, rk[0]);
  /* ROUNDS-1 ordinary rounds
   */
  for (r = 1; r < ROUNDS; r++) {
    SubBytes(a, S);
    ShiftRows(a, 0);
    MixColumns(a);
    AddRoundKey(a, rk[r]);
  }
  /* Last round is special: there is no MixColumns
   */
  SubBytes(a, S);
  ShiftRows(a, 0);
  AddRoundKey(a, rk[ROUNDS]);
  return 0;
}
int Decrypt(word8 a[4][MAXBC], word8 rk[MAXROUNDS + 1][4][MAXBC]) {
  int r;
  /* To decrypt:
  *
  apply the inverse operations of the encrypt routine,
  *
  in opposite order
  *
  * - AddRoundKey is equal to its inverse)
  * - the inverse of SubBytes with table S is
  *
  SubBytes with the inverse table of S)
  * - the inverse of Shiftrows is Shiftrows over
  *
  a suitable distance)
  */
  /* First the special round:
  *
  without InvMixColumns
  *
  with extra AddRoundKey
  */
  AddRoundKey(a, rk[ROUNDS]);
  SubBytes(a, Si);
  ShiftRows(a, 1);
  /* ROUNDS-1 ordinary rounds
   */
  for (r = ROUNDS - 1; r > 0; r--) {
    AddRoundKey(a, rk[r]);
    InvMixColumns(a);
    SubBytes(a, Si);
    ShiftRows(a, 1);
  }
  /* End with the extra key addition
   */
  AddRoundKey(a, rk[0]);
  return 0;
}

void AES128_encrypt(word8* block, const word8* key) {
  word8 a[4][MAXBC], rk[MAXROUNDS + 1][4][MAXBC], sk[4][MAXKC];
  for (int j=0; j<4; j++) {
      for (int i=0; i<4; i++) {
          a[i][j] = block[4*j+i];
          sk[i][j] = key[4*j+i];
      }
  }
  KeyExpansion(sk, rk);
  Encrypt(a, rk);
  for (int j=0; j<4; j++) {
      for (int i=0; i<4; i++) {
          block[4*j+i] = a[i][j];
      }
  }
}
