; Simple 65C02 test to isolate the issue
        .ORG $8000

START:  LDA #$55        ; Load immediate
        STA $0200        ; Store absolute
        LDA $1000,X      ; Absolute X indexed
        RTS