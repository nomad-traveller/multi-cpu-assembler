; 6800 Comprehensive Test Suite
; Tests core assembler functionality with known-good assembly code
; Expected to assemble without errors and produce correct binary output

        .ORG $8000

; Test immediate addressing
START:  LDAA #$55       ; Load accumulator A immediate
        LDAB #$33       ; Load accumulator B immediate
        LDX #$00         ; Load X register immediate
        LDY #$01         ; Load Y register immediate

; Test direct addressing (6800 equivalent of zero-page)
        LDAA $00          ; Direct load accumulator A
        STAA $01          ; Direct store accumulator A
        LDAB $10          ; Direct load accumulator B
        STAB $20          ; Direct store accumulator B
        LDX $30           ; Direct load X
        STX $40           ; Direct store X

; Test extended addressing
        LDAA $1000        ; Extended load accumulator A
        STAA $1001        ; Extended store accumulator A
        LDAB $2000        ; Extended load accumulator B
        STAB $2001        ; Extended store accumulator B
        LDX $3000         ; Extended load X
        STX $3001         ; Extended store X

; Test indexed addressing
        LDAA $1000,X      ; Extended X indexed
        STAA $2000,X      ; Extended X indexed
        LDAB $10,X        ; Direct X indexed
        STAB $20,X        ; Direct X indexed

; Test inherent addressing (no operands)
        NOP               ; No operation
        CLC               ; Clear carry
        SEC               ; Set carry
        CLI               ; Clear interrupt mask
        SEI               ; Set interrupt mask
        TAP               ; Transfer accumulator to condition code register
        TPA               ; Transfer condition code register to accumulator
        TSX               ; Transfer stack pointer to X
        TXS               ; Transfer X to stack pointer
        RTS               ; Return from subroutine
        RTI               ; Return from interrupt

; Test accumulator operations
        INCA              ; Increment accumulator A
        INCB              ; Increment accumulator B
        DECA              ; Decrement accumulator A
        DECB              ; Decrement accumulator B
        COMA              ; Complement accumulator A
        COMB              ; Complement accumulator B
        NEGA              ; Negate accumulator A
        NEGB              ; Negate accumulator B

; Test register operations
        INX               ; Increment X register
        DEX               ; Decrement X register
        INY               ; Increment Y register
        DEY               ; Decrement Y register

; Test arithmetic operations
        ADDA #$10         ; Add to accumulator A
        ADDB #$20         ; Add to accumulator B
        SUBA #$05         ; Subtract from accumulator A
        SUBB #$15         ; Subtract from accumulator B
        ANDA #$0F         ; Logical AND accumulator A
        ANDB #$F0         ; Logical AND accumulator B
        ORA #$AA          ; Logical OR accumulator A
        ORB #$55          ; Logical OR accumulator B
        EORA #$33         ; Logical XOR accumulator A
        EORB #$CC         ; Logical XOR accumulator B

; Test compare operations
        CMPA #$55         ; Compare accumulator A
        CMPB #$33         ; Compare accumulator B
        CPX #$10          ; Compare X register
        CBA               ; Compare accumulator B to accumulator A

; Test branch instructions
        BCC SKIP1         ; Branch if carry clear
        BCS SKIP2         ; Branch if carry set
        BEQ SKIP3         ; Branch if equal
        BNE SKIP4         ; Branch if not equal
        BMI SKIP5         ; Branch if minus
        BPL SKIP6         ; Branch if plus
        BVC SKIP7         ; Branch if overflow clear
        BVS SKIP8         ; Branch if overflow set
        BGE SKIP9         ; Branch if greater than or equal
        BGT SKIP10        ; Branch if greater than
        BLE SKIP11        ; Branch if less than or equal
        BLT SKIP12        ; Branch if less than
        BHI SKIP13        ; Branch if higher
        BLS SKIP14        ; Branch if lower or same
        BRA END            ; Branch always

SKIP1:  NOP
SKIP2:  NOP
SKIP3:  NOP
SKIP4:  NOP
SKIP5:  NOP
SKIP6:  NOP
SKIP7:  NOP
SKIP8:  NOP
SKIP9:  NOP
SKIP10: NOP
SKIP11: NOP
SKIP12: NOP
SKIP13: NOP
SKIP14: NOP

; Test stack operations
        PSHA              ; Push accumulator A
        PSHB              ; Push accumulator B
        PULA              ; Pull accumulator A
        PULB              ; Pull accumulator B

; Test transfer operations
        TBA               ; Transfer accumulator B to accumulator A
        TAB               ; Transfer accumulator A to accumulator B
        DAA               ; Decimal adjust accumulator A

; Test shift and rotate operations
        ASLA              ; Arithmetic shift left accumulator A
        ASLB              ; Arithmetic shift left accumulator B
        ASRA              ; Arithmetic shift right accumulator A
        ASRB              ; Arithmetic shift right accumulator B
        LSLA              ; Logical shift left accumulator A
        LSLB              ; Logical shift left accumulator B
        LSRA              ; Logical shift right accumulator A
        LSRB              ; Logical shift right accumulator B
        ROLA              ; Rotate left accumulator A
        ROLB              ; Rotate left accumulator B
        RORA              ; Rotate right accumulator A
        RORB              ; Rotate right accumulator B

; Test memory operations
        CLR $1000          ; Clear memory location
        COM $1001          ; Complement memory location
        NEG $1002          ; Negate memory location

; Test jump and subroutine
        JMP CONTINUE       ; Unconditional jump
        JSR SUBROUTINE    ; Jump to subroutine

SUBROUTINE:
        RTS               ; Return from subroutine

CONTINUE:
; Test data directives
DATA:   .BYTE $01,$02,$03,$04    ; Define bytes
        .WORD $1234,$5678        ; Define words

END:    SWI               ; Software interrupt to end execution