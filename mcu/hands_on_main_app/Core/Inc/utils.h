/*
 * utils.h
 */

#ifndef INC_UTILS_H_
#define INC_UTILS_H_

void start_cycle_count();
void stop_cycle_count(char *s);

void hex_encode(char* s, const uint8_t* buf, size_t len);

#endif /* INC_UTILS_H_ */
