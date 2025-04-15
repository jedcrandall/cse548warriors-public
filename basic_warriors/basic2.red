;redcode-94
;name     Level2
;author   CSE548
;strategy More aggressive core-clear bomber with multiple pointers

        org     start

start   mov     bomb, @ptr1    
        mov     bomb, @ptr2    
        add     #50, ptr1      
        add     #50, ptr2      
        jmp     start          

ptr1    dat     #0             
ptr2    dat     #100           

bomb    dat     #0, #0         

;assert 1
        end     start

