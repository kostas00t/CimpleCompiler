L0:   b LfinalCodeExample 
L1:        
      sw ra,-0(sp) 
L2:        
      li t1,4 
      sw t1,-12(sp) 
L3:        
      lw t1,-16(gp) 
      sw t1,-12(gp) 
L4:        
      lw t1,-20(gp) 
      sw t1,-24(gp) 
L5:        
      lw t1,-28(gp) 
      lw t2,-12(sp) 
      add t1,t1,t2 
      sw t1,-16(sp) 
L6:        
      lw t1,-16(sp) 
      lw t0,-8(sp) 
      sw t1,(t0) 
L7:        
      lw ra,-0(sp) 
      jr ra 
L8:        
      sw ra,-0(sp) 
L9:        
      lw a0,-12(gp) 
      li a7,1 
      ecall 
L10:        
      lw a0,-16(gp) 
      li a7,1 
      ecall 
L11:        
      addi fp,sp,20 
      addi t0,sp,-20 
      sw t0,-8(fp) 
L12:        
      sw sp,-4(fp) 
      addi sp,sp,20 
      jal L1 
      addi sp,sp,-20 
L13:        
      lw t1,-20(sp) 
      sw t1,-16(gp) 
L14:        
      lw a0,-12(gp) 
      li a7,1 
      ecall 
L15:        
      lw a0,-16(gp) 
      li a7,1 
      ecall 
L16:        
      lw ra,-0(sp) 
      jr ra 
LfinalCodeExample: 
L17:        
      addi sp,sp,32 
      mv gp,sp 
L18:        
      li t1,3 
      sw t1,-28(sp) 
L19:        
      li t1,2 
      sw t1,-12(sp) 
L20:        
      li t1,2 
      sw t1,-16(sp) 
L21:        
      addi fp,sp,24 
      lw t0,-12(sp) 
      sw t0,-12(fp) 
L22:        
      addi t0,sp,-16 
      sw t0,-12(fp) 
L23:        
      sw sp,-4(fp) 
      addi sp,sp,24 
      jal L8 
      addi sp,sp,-24 
L24:        
      lw a0,-12(sp) 
      li a7,1 
      ecall 
L25:        
      lw a0,-16(sp) 
      li a7,1 
      ecall 
L26:        
      li a0,0 
      li a7,93 
      ecall 
L27:        
