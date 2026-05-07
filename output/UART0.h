/**
 * @file UART_periph_template.h
 * @author L. Nicholson-Andrews (lewisnich01@outlook.com)
 * @brief This is a template header file for any Peripheral to use
 */

#ifndef UART0_H
#define UART0_H

#include <stdint.h>

#define UART0_BASE    1073750016

/* Register Offsets */
#define UART0_CR    0
#define UART0_SR    4
#define UART0_DR    8
#define UART0_BRR    12

/* Declarations / Function Prototypes */
void UART0_init(void);
void UART0_open(void);
void UART0_close(void);
void UART0_write(uint8_t data);
uint8_t UART0_read(void);

typedef struct{
    uint32_t baud_rate;
    uint8_t data_len;
    int8_t UART_PARITY      : 1;    /* 1 bit - even or odd */
    int8_t UART_STOP_BIT    : 1;    /* 1 bit - one or two stop bits */
}uart_comm_sett_t;

typedef enum{
    UART_INIT,
    UART_OPEN,
    UART_CLOSE,
    UART_READ,
    UART_WRITE
}uart_handle_t;

#endif /* UART0_H */