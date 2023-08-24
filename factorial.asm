L0:   b Lfactorial 
Lfactorial: 
L1:        
      addi sp,sp,32 
      mv gp,sp 
L2:        
      li a7,5 
      ecall 
      sw a0,-12(sp) 
L3:        
      li t1,165 
      sw t1,-20(sp) 
L4:        
      li t1,1 
      sw t1,-16(sp) 
L5:        
      lw t1,-16(sp) 
      lw t2,-12(sp) 
      ble t1,t2,L7 
L6:        
      b L12 
L7:        
      lw t1,-20(sp) 
      lw t2,-16(sp) 
      mul t1,t1,t2 
      sw t1,-24(sp) 
L8:        
      lw t1,-24(sp) 
      sw t1,-20(sp) 
L9:        
      lw t1,-16(sp) 
      li t2,1 
      add t1,t1,t2 
      sw t1,-28(sp) 
L10:        
      lw t1,-28(sp) 
      sw t1,-16(sp) 
L11:        
      b L5 
L12:        
      lw a0,-20(sp) 
      li a7,1 
      ecall 
L13:        
      li a0,0 
      li a7,93 
      ecall 
L14:        
