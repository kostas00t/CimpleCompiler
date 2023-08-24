#include <stdio.h>
int main(){ 
 int x,count,T_0,T_1;
1 : ;
2 : scanf("%d",&x);
3 : count=0;
4 : if(x>0) goto 6;
5 : goto 11;
6 : T_0=x/10;
7 : x=T_0;
8 : T_1=count+1;
9 : count=T_1;
10 : goto 4;
11 : printf("%d",&count);
12 : ;
13 : ;
}