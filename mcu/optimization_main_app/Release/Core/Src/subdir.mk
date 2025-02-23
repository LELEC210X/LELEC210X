################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (12.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Core/Src/adc.c \
../Core/Src/adc_dblbuf.c \
../Core/Src/aes_ref.c \
../Core/Src/arm_absmax_q15.c \
../Core/Src/dma.c \
../Core/Src/eval_radio.c \
../Core/Src/gpio.c \
../Core/Src/main.c \
../Core/Src/packet.c \
../Core/Src/retarget.c \
../Core/Src/s2lp.c \
../Core/Src/spectrogram.c \
../Core/Src/spi.c \
../Core/Src/stm32l4xx_hal_msp.c \
../Core/Src/stm32l4xx_it.c \
../Core/Src/sysmem.c \
../Core/Src/system_stm32l4xx.c \
../Core/Src/tim.c \
../Core/Src/usart.c \
../Core/Src/utils.c 

OBJS += \
./Core/Src/adc.o \
./Core/Src/adc_dblbuf.o \
./Core/Src/aes_ref.o \
./Core/Src/arm_absmax_q15.o \
./Core/Src/dma.o \
./Core/Src/eval_radio.o \
./Core/Src/gpio.o \
./Core/Src/main.o \
./Core/Src/packet.o \
./Core/Src/retarget.o \
./Core/Src/s2lp.o \
./Core/Src/spectrogram.o \
./Core/Src/spi.o \
./Core/Src/stm32l4xx_hal_msp.o \
./Core/Src/stm32l4xx_it.o \
./Core/Src/sysmem.o \
./Core/Src/system_stm32l4xx.o \
./Core/Src/tim.o \
./Core/Src/usart.o \
./Core/Src/utils.o 

C_DEPS += \
./Core/Src/adc.d \
./Core/Src/adc_dblbuf.d \
./Core/Src/aes_ref.d \
./Core/Src/arm_absmax_q15.d \
./Core/Src/dma.d \
./Core/Src/eval_radio.d \
./Core/Src/gpio.d \
./Core/Src/main.d \
./Core/Src/packet.d \
./Core/Src/retarget.d \
./Core/Src/s2lp.d \
./Core/Src/spectrogram.d \
./Core/Src/spi.d \
./Core/Src/stm32l4xx_hal_msp.d \
./Core/Src/stm32l4xx_it.d \
./Core/Src/sysmem.d \
./Core/Src/system_stm32l4xx.d \
./Core/Src/tim.d \
./Core/Src/usart.d \
./Core/Src/utils.d 


# Each subdirectory must supply rules for building sources it contributes
Core/Src/%.o Core/Src/%.su Core/Src/%.cyclo: ../Core/Src/%.c Core/Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -DUSE_HAL_DRIVER -DSTM32L4A6xx -c -I../Core/Inc -I"C:/Dev/GIT/LELEC210X_GROUP_E/mcu/optimization_main_app/ARM_CMSIS/CMSIS/DSP/Include" -I../Drivers/STM32L4xx_HAL_Driver/Inc -I../Drivers/STM32L4xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32L4xx/Include -I../Drivers/CMSIS/Include -O3 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Core-2f-Src

clean-Core-2f-Src:
	-$(RM) ./Core/Src/adc.cyclo ./Core/Src/adc.d ./Core/Src/adc.o ./Core/Src/adc.su ./Core/Src/adc_dblbuf.cyclo ./Core/Src/adc_dblbuf.d ./Core/Src/adc_dblbuf.o ./Core/Src/adc_dblbuf.su ./Core/Src/aes_ref.cyclo ./Core/Src/aes_ref.d ./Core/Src/aes_ref.o ./Core/Src/aes_ref.su ./Core/Src/arm_absmax_q15.cyclo ./Core/Src/arm_absmax_q15.d ./Core/Src/arm_absmax_q15.o ./Core/Src/arm_absmax_q15.su ./Core/Src/dma.cyclo ./Core/Src/dma.d ./Core/Src/dma.o ./Core/Src/dma.su ./Core/Src/eval_radio.cyclo ./Core/Src/eval_radio.d ./Core/Src/eval_radio.o ./Core/Src/eval_radio.su ./Core/Src/gpio.cyclo ./Core/Src/gpio.d ./Core/Src/gpio.o ./Core/Src/gpio.su ./Core/Src/main.cyclo ./Core/Src/main.d ./Core/Src/main.o ./Core/Src/main.su ./Core/Src/packet.cyclo ./Core/Src/packet.d ./Core/Src/packet.o ./Core/Src/packet.su ./Core/Src/retarget.cyclo ./Core/Src/retarget.d ./Core/Src/retarget.o ./Core/Src/retarget.su ./Core/Src/s2lp.cyclo ./Core/Src/s2lp.d ./Core/Src/s2lp.o ./Core/Src/s2lp.su ./Core/Src/spectrogram.cyclo ./Core/Src/spectrogram.d ./Core/Src/spectrogram.o ./Core/Src/spectrogram.su ./Core/Src/spi.cyclo ./Core/Src/spi.d ./Core/Src/spi.o ./Core/Src/spi.su ./Core/Src/stm32l4xx_hal_msp.cyclo ./Core/Src/stm32l4xx_hal_msp.d ./Core/Src/stm32l4xx_hal_msp.o ./Core/Src/stm32l4xx_hal_msp.su ./Core/Src/stm32l4xx_it.cyclo ./Core/Src/stm32l4xx_it.d ./Core/Src/stm32l4xx_it.o ./Core/Src/stm32l4xx_it.su ./Core/Src/sysmem.cyclo ./Core/Src/sysmem.d ./Core/Src/sysmem.o ./Core/Src/sysmem.su ./Core/Src/system_stm32l4xx.cyclo ./Core/Src/system_stm32l4xx.d ./Core/Src/system_stm32l4xx.o ./Core/Src/system_stm32l4xx.su ./Core/Src/tim.cyclo ./Core/Src/tim.d ./Core/Src/tim.o ./Core/Src/tim.su ./Core/Src/usart.cyclo ./Core/Src/usart.d ./Core/Src/usart.o ./Core/Src/usart.su ./Core/Src/utils.cyclo ./Core/Src/utils.d ./Core/Src/utils.o ./Core/Src/utils.su

.PHONY: clean-Core-2f-Src

