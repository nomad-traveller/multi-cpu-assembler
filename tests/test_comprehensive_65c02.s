; 65C02 Comprehensive Test Suite
; Tests core assembler functionality with known-good assembly code
; Expected to assemble without errors and produce correct binary output

        .ORG $8000

; Test immediate addressing
START:  LDA #$55        ; Load immediate value $55
        STA $0200        ; Store to absolute address
        LDX #$00        ; Load X with zero
        LDY #$01        ; Load Y with one

; Test zero-page addressing
        LDA $00          ; Zero-page load
        STA $01          ; Zero-page store
        LDX $10          ; Zero-page X load
        STX $20          ; Zero-page X store

; Test absolute addressing
        LDA $1000        ; Absolute load
        STA $1001        ; Absolute store
        LDX $2000        ; Absolute X load
        LDY $3000        ; Absolute Y load

; Test indexed addressing
        LDA $1000,X      ; Absolute X indexed
        STA $2000,Y      ; Absolute Y indexed
        LDA $10,X        ; Zero-page X indexed
        STA $20,Y        ; Zero-page Y indexed

; Test accumulator addressing
        ASL A            ; Accumulator shift left
        LSR A            ; Accumulator shift right
        ROL A            ; Accumulator rotate left
        ROR A            ; Accumulator rotate right

; Test implied addressing
        CLC              ; Clear carry
        SEC              ; Set carry
        CLD              ; Clear decimal
        SED              ; Set decimal
        CLI              ; Clear interrupt
        SEI              ; Set interrupt
        CLV              ; Clear overflow

; Test branch instructions
        BCC SKIP1        ; Branch if carry clear
        BCS SKIP2        ; Branch if carry set
        BEQ SKIP3        ; Branch if equal
        BNE SKIP4        ; Branch if not equal
        BMI SKIP5        ; Branch if minus
        BPL SKIP6        ; Branch if plus
        BVC SKIP7        ; Branch if overflow clear
        BVS SKIP8        ; Branch if overflow set

SKIP1:  NOP
SKIP2:  NOP  
SKIP3:  NOP
SKIP4:  NOP
SKIP5:  NOP
SKIP6:  NOP
SKIP7:  NOP
SKIP8:  NOP

; Test stack operations
        PHA              ; Push accumulator
        PHP              ; Push processor status
        PLA              ; Pull accumulator
        PLP              ; Pull processor status

; Test transfer instructions
        TAX              ; Transfer A to X
        TAY              ; Transfer A to Y
        TXA              ; Transfer X to A
        TYA              ; Transfer Y to A
        TSX              ; Transfer SP to X
        TXS              ; Transfer X to SP

; Test arithmetic operations
        ADC #$10         ; Add with carry
        SBC #$20         ; Subtract with carry
        AND #$0F         ; Logical AND
        ORA #$F0         ; Logical OR
        EOR #$AA         ; Logical XOR

; Test compare operations
        CMP #$55         ; Compare accumulator
        CPX #$10         ; Compare X register
        CPY #$20         ; Compare Y register

; Test jump and subroutine
        JMP CONTINUE      ; Unconditional jump
        JSR SUBROUTINE   ; Jump to subroutine

SUBROUTINE:
        RTS              ; Return from subroutine

CONTINUE:
; Test indirect addressing
        LDA ($00FF)      ; Indirect absolute
        JMP ($1000)      ; Indirect jump

; Test 65C02 specific instructions
        BRA END           ; Branch always (65C02 specific)
        PHX              ; Push X (65C02 specific)
        PHY              ; Push Y (65C02 specific)
        PLX              ; Pull X (65C02 specific)
        PLY              ; Pull Y (65C02 specific)

; Test data directives
DATA:   .BYTE $01,$02,$03,$04    ; Define bytes
        .WORD $1234,$5678        ; Define words

END:    BRK              ; Breakpoint to end execution