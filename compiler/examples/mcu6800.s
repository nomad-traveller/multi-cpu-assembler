; =====================================================================
;   Motorola 6800 LED Blink Program
;
;   This program configures Port A of a 6821 PIA as an output and
;   repeatedly turns an LED on and off on pin PA0.
;
;   Hardware Assumptions:
;   - PIA is mapped at $8004.
;   - LED is connected to pin PA0.
; =====================================================================

PIA_A_DDR   EQU  $8004  ; Port A Data/Direction Register
PIA_A_CR    EQU  $8005  ; Port A Control Register

            .ORG $C000  ; Set program start address to $C000 (a common ROM address)

; --- Step 1: Initialize the PIA Port A for output ---
START:
            CLR  $8004   ; Clear Control Register A. This selects the
                            ; Data Direction Register (DDR) at $8004.

            LDAA #$FF       ; Load Accumulator A with all 1s (binary 11111111).
            STAA $8004  ; Store this in the DDR to set all pins of Port A as outputs.

            LDAA #$04       ; Load Accumulator A with %00000100 to set bit 2.
            STAA $8005   ; Store in Control Register A. This makes future
                            ; writes to $8004 go to the Port A data register.

; --- Step 2: Main program loop ---
LOOP:
            ; Turn the LED ON
            LDAA #$01       ; Load binary 1 into Accumulator A.
            STAA $8004  ; Write to Port A, setting pin PA0 high.
            JSR  DELAY      ; Jump to our delay subroutine.

            ; Turn the LED OFF
            CLR  $8004  ; Clear Port A data register (writes 0 to all pins).
            JSR  DELAY      ; Call the delay subroutine again.

            BRA  LOOP       ; Branch always back to the start of the loop.

; --- Step 3: A simple delay subroutine ---
; This loop just wastes time by counting the 16-bit X register down from a large number.
DELAY:
            LDX  #$FFFF     ; Load the Index Register (X) with 65535.
DELAY_LOOP:
            DEX             ; Decrement the X register.
            BNE  DELAY_LOOP ; Branch if Not Equal (to zero) back to the start of the delay.
            RTS             ; Return from Subroutine when X is zero.
