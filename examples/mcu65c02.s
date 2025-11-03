; MCU 65C02 LED Blink Program
; This program blinks an LED connected to memory location $8000
; Assumes the LED is active high (on when bit 0 is set)

.ORG $8000          ; Start program at address $8000

; Initialize
LDA #$00            ; Load accumulator with 0
STA $8000           ; Initialize LED port to off

MAIN_LOOP:
    ; Turn LED on
    LDA #$01        ; Set bit 0 (LED on)
    STA $8000       ; Write to LED port

    ; Delay loop
    LDX #$FF        ; Load X with 255
DELAY_ON:
    LDY #$FF        ; Load Y with 255
INNER_DELAY_ON:
    DEY             ; Decrement Y
    BNE INNER_DELAY_ON ; Loop until Y = 0
    DEX             ; Decrement X
    BNE DELAY_ON    ; Loop until X = 0

    ; Turn LED off
    LDA #$00        ; Clear bit 0 (LED off)
    STA $8000       ; Write to LED port

    ; Delay loop
    LDX #$FF        ; Load X with 255
DELAY_OFF:
    LDY #$FF        ; Load Y with 255
INNER_DELAY_OFF:
    DEY             ; Decrement Y
    BNE INNER_DELAY_OFF ; Loop until Y = 0
    DEX             ; Decrement X
    BNE DELAY_OFF   ; Loop until X = 0

    JMP MAIN_LOOP   ; Repeat forever