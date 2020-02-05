#include <stdint.h>

uint32_t crc_table[256];
/* Run this function previously */
extern void make_crc_table() {
	for(uint32_t i = 0; i < 256; i++) {
		uint32_t c = i;
		for(int j = 0; j < 8; j++) {
			c = (c & 1) ? (0x82F63B78^(c >> 1)) : (c >> 1);
		}
		crc_table[i] = c;
	}
}

extern long calc_checksum(char *buf, int len) {
	long c = 0xFFFFFFFF;
	for(size_t i = 0; i < len; i++) {
		c = crc_table[(c^((uint8_t)buf[i])) & 0xFF] ^ (c >> 8);
	}
	return c ^ 0xFFFFFFFF;
}