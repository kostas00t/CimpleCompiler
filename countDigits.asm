L0:   b LcountDigits 
LcountDigits: 
L1:        
      addi sp,sp,28 
      mv gp,sp 
L2:        
      li a7,5 
      ecall 
      sw a0,-12(sp) 
L3:        
      li t1,0 
      sw t1,-16(sp) 
L4:        
      lw t1,-12(sp) 
      li t2,0 
      bgt t1,t2,L6 
L5:        
      b L11 
L6:        
      lw t1,-12(sp) 
      li t2,10 
      div t1,t1,t2 
      sw t1,-20(sp) 
L7:        
      lw t1,-20(sp) 
      sw t1,-12(sp) 
L8:        
      lw t1,-16(sp) 
      li t2,1 
      add t1,t1,t2 
      sw t1,-24(sp) 
L9:        
      lw t1,-24(sp) 
      sw t1,-16(sp) 
L10:        
      b L4 
L11:        
      lw a0,-16(sp) 
      li a7,1 
      ecall 
L12:        
      li a0,0 
      li a7,93 
      ecall 
L13:        
