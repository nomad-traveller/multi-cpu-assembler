; Hello World program for Intel 8086
; This is a simple example demonstrating basic 8086 instructions

.ORG $100

MAIN:
    ; Initialize registers
    MOV AX, #$1234    ; Load AX with hex value
    MOV BX, #5678     ; Load BX with decimal value
    MOV CX, AX        ; Copy AX to CX

    ; Simple arithmetic
    ADD AX, BX        ; AX = AX + BX
    SUB CX, #100      ; CX = CX - 100

    ; Jump to end
    JMP END_PROGRAM

END_PROGRAM:
    ; Software interrupt to exit (DOS style)
    MOV AH, #76       ; DOS terminate function
    INT #33           ; Call DOS interrupt

    ; Infinite loop (fallback)
INFINITE_LOOP:
    JMP INFINITE_LOOP

; Data section
.BYTE $01, $02, $03, $04
.WORD $ABCD, $EF12