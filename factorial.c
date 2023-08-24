#include <stdio.h>
int main(){ 
 int x,i,fact,T_0,T_1;
1 : ;
2 : scanf("%d",&x);
3 : fact=165;
4 : i=1;
5 : if(i<=x) goto 7;
6 : goto 12;
7 : T_0=fact*i;
8 : fact=T_0;
9 : T_1=i+1;
10 : i=T_1;
11 : goto 5;
12 : printf("%d",&fact);
13 : ;
14 : ;
}