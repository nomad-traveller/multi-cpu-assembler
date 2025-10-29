; Test file with common assembly mistakes
.ORG $8000

; Invalid label name
INVALID-LABEL: LDA #$01

; Missing space around operator
LDA #$10+$20

; Invalid hex digit
LDA #$1G

; Long label name
VERY_VERY_VERY_VERY_VERY_VERY_LONG_LABEL_NAME: LDA #$01

; 6502 specific: ASL with immediate (invalid)
ASL #$01

; Branch with absolute addressing (invalid for 6502)
BEQ $9000

; Using wrong register
LDX Y

; Zero page optimization opportunity
LDA $1234

; Valid instruction for comparison
LDA #$42