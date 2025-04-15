;redcode-94
;name     Level3
;author   CSE548
;strategy Moderate replicator with occasional bombing

        org     start

start   spl     0             ; spawn a new process
        mov     @start, ptr   ; replicate code to ptr
        add     #5, ptr       ; advance replication pointer

        ; only bomb every 3rd iteration
        add     #1, counter   ; increment counter
        mov     bomb, @bptr   ; otherwise drop a bomb
        add     #25, bptr     ; advance bombing pointer

        jmp     start         ; loop forever

ptr      dat    #0           ; replication pointer
bptr     dat    #100         ; bombing pointer
counter  dat    #0           ; loop counter
bomb     dat    #0, #0       ; DAT bomb

;assert 1
        end     start

