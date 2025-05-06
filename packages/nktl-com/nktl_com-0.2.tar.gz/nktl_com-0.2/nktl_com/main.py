def hello():
    print("""EXP 1: TOKENS IN C:
CODE:
%{
#include<stdio.h>
%}
%%
[ \t\n] ;
int|float|char|if|else|double|long|switch|break|void {printf("KEYWORDS\n");}
[a-z][a-z0-9]* {printf("ID\n");}
"," {printf("COMMA\n");}
";" {printf("SEMI COLON\n");}
. {printf("%c\n",yytext[0]);}
%%
int main()
{
printf("Enter any input:");
yylex();
}
---------------------------------------------------------------------------------------------------------
          
EXP 2: BRANCHING ST.(IF..ELSE):
CODE:
(i)LEX PROG:
%{
#include<stdio.h>
#include "y.tab.h"
%}
%%
[ \t\n] ;
"if" return IF;
"else" return ELSE;
int|float|char|double|long|switch|break|void {return KEY;}
[0-9]+ return CONST;
[a-z][a-z0-9]* {return ID;}
[ > < = ] return OP;
"(" return OB;
")" return CB;
"{" return OC;
"}" return CC;
"," {return C;}
";" {return SC;}
. {printf("%c\n",yytext[0]);}
%%
(ii)YACC PROG:
%{
#include<stdio.h>
#include "y.tab.h"
%}
%token IF ELSE KEY OP OB CB OC CC C SC CONST ID;
%start S;
%%
S: stmt {printf("Valid");};
stmt: IF OB exp CB OC body CC ELSE OC body CC;
exp: ID OP ID | ID OP CONST ;
body: KEY ID OP CONST SC ;
%%
yyerror()
{
printf("Error");
}
main()
{
yyparse();
}
SAMPLE INPUT:
if(a<10)
{
int b=10;
}
else
{
int b=20;
}
-------------------------------------------------------------------------------------------------
                 
EXP 3: LOOPING ST.(WHILE):
CODE:
(i)LEX PROG:
%{
#include<stdio.h>
#include "y.tab.h"
%}
%%
"printf" return PRINTF;
"while" return WHILE;
"(" return OP;
[0-9]+ return NUM;
[a-zA-Z][a-zA-Z0-9_]* return ID;
"<" return LT;
">" return GT;
"==" return DEQ;
\" return QUOT;
"!=" return NEQ;
"+" return ADD;
"-" return SUB;
")" return CP;
"{" return OB;
"=" return EQ;
";" return SC;
"}" return CB;
%%
int yywrap()
{
return 1;//end of line
}
(ii)YACC PROG:
%{
#include<stdio.h>
%}
%token WHILE OP ID LT GT DEQ NEQ ADD SUB CP OB EQ QUOT PRINTF TEXT SC NUM CB;
%start S
%%
S:Loop {printf("The syntax is valid");};
Loop: WHILE OP condn CP OB body CB;
condn: ID LT ID
|ID GT ID
|ID DEQ ID
|ID NEQ ID
;
body:ID EQ ID SC body
|ID EQ NUM SC body
|ID ADD ADD SC body
|ID SUB SUB SC body
|PRINTF OP QUOT text QUOT CP SC body |
;
text:text | ID
;
%%
yyerror()
{
printf("Invalid syntax");
}
main()
{
yyparse();
}
SAMPLE INPUT:
while(a<b)
{
printf("loop");
a=10;
a++;
}
---------------------------------------------------------------------------------------------------------------
                   
EXP 4A: ARRAY WITH FOR LOOP:
CODE:
(i)LEX PROG:
%{
#include<stdio.h>
#include "y.tab.h"
%}
%%
[ \t\n] ;
"#include<stdio.h>" return HEADER;
"main" return MAIN;
"int" return INT;
"for" return FOR;
[a-zA-Z][a-zA-Z0-9_]* return ID;
[0-9]+ return NUM;
"[" return LSQ;
"]" return RSQ;
"(" return OP;
")" return CP;
"{" return OB;
"}" return CB;
"<" return LT;
"+" return ADD;
"-" return SUB;
"," return COM;
"=" return EQ;
";" return SC;
. return 0;
%%
int yywrap()
{
return 1;
}
(ii)YACC PROG:
%{
#include<stdio.h>
%}
%%
%token INT ID NUM LSQ RSQ EQ SC OB CB COM OP CP LT ADD SUB FOR HEADER MAIN;
%start S;
S: header main OB arrayDec CB {printf("array");} |header main OB loop CB {printf("loop");} |header main OB arrayDec loop CB {printf("Valid Program");};
header: HEADER;
main: INT MAIN OP CP;
arrayDec : INT ID LSQ num RSQ SC
| INT ID LSQ num RSQ EQ num SC
| INT ID LSQ RSQ EQ initialVal SC
;
loop: condn OB body CB
;
condn: FOR OP initialDec SC condFor SC incre CP;
initialDec: INT ID EQ num;
condFor: ID LT num;
incre: ID ADD ADD | ID SUB SUB;
body: ID LSQ ID RSQ EQ num SC;
num: NUM
;
initialVal: OB num COM num COM num CB
;
%%
yyerror()
{
printf("Invalid array declaration");
}
int main()
{
yyparse();
}
SAMPLE INPUTS:
TYPE 1
#include<stdio.h>
int main()
{
int marks[5];
for(int i=0;i<10;i++)
{
marks[i]=10;
}
}
TYPE 2
#include<stdio.h>
int main()
{
int marks[5]=10;
}
TYPE 3
#include<stdio.h>
int main()
{
for(int i=0;i<10;i++)
{
marks[i]=10;
}
}
---------------------------------------------------          
EXP 4B: PROCEDURE CALLS:
CODE:
(i)LEX PROG:
%{
#include<stdio.h>
#include "y.tab.h"
%}
%%
[ \t\n] ;
"#include<stdio.h>" return HEADER;
"main" return MAIN;
"int" return INT;
"printf" return PRINTF;
"return" return RETURN;
[0-9][0-9]* return NUM;
[a-zA-Z][a-zA-Z0-9_%:]* return ID;
"(" return OP;
")" return CP;
"{" return OB;
"}" return CB;
"," return COM;
";" return SC;
"+" return ADD;
"-" return SUB;
"*" return MUL;
"/" return DIV;
"=" return EQ;
\" return QUOT;
. return 0;
%%
int yywrap()
{
return 1;
}
(ii)YACC PROG:
%{
#include<stdio.h>
%}
%token HEADER MAIN INT PRINTF ID NUM OP CP OB CB COM SC RETURN ADD SUB MUL DIV QUOT EQ;
%start S;
%%
S: funcDef mainFunc {printf("Valid Program");} | mainFunc funcDef {printf("Valid Program");};
mainFunc: INT MAIN OP CP OB body CB;
body:PRINTF OP QUOT text QUOT COM ID CP SC body| INT ID SC body
| ID EQ ID OP NUM COM NUM CP SC body
| RETURN NUM SC body |
;
funcDef: INT ID OP parameters CP OB bodyFunc CB;
parameters: parameters COM INT ID
| INT ID
|
;
bodyFunc: RETURN ID opr ID SC;
opr: ADD | SUB | MUL | DIV ;
text: text text | ID;
%%
yyerror()
{
printf("Invalid syntax");
}
int main()
{
yyparse();
}
SAMPLE INPUT:
int sum(int a,int b)
{
return a+b;
}
int main()
{
int add;
add=sum(10,10);
printf("Sum is:%d",add);
return 0;}
""")
    
def nothello():
    print("""# FIRST AND FOLLOW SET CALCULATOR - SIMPLE VERSION
# STEP 1: Get grammar input from user

n = int(input("Enter number of productions: "))
productions = []  # This will store all grammar rules
print("\nEnter productions (one per line, format 'A->BC' or 'A->a'):")

# Read each production and validate
for _ in range(n):
    prod = input().strip()  # Remove extra whitespace
    if '->' not in prod:
        print("Error: Production must contain '->'")
        exit()
    productions.append(prod)

# STEP 2: Identify all non-terminals (uppercase letters on left side)
non_terminals = set(prod[0] for prod in productions)

# STEP 3: Define FIRST set calculation
def first(symbol):
    result = set()  # Using set to avoid duplicates
    
    # Case 1: If symbol is terminal (lowercase), its FIRST is itself
    if not symbol.isupper():
        return {symbol}
    
    # Case 2: For non-terminals, check all productions
    for prod in productions:
        # Only look at productions for this non-terminal
        if prod[0] == symbol:
            rhs = prod.split('->')[1]  # Get right-hand side
            
            # Case 2a: Empty production (epsilon)
            if not rhs or rhs == '$':
                result.add('$')
            else:
                # Case 2b: Add FIRST of first symbol in production
                result.update(first(rhs[0]))
    return result

# STEP 4: Define FOLLOW set calculation
def follow(symbol):
    result = set()
    
    # Rule 1: Start symbol always has $ in FOLLOW
    if symbol == productions[0][0]:
        result.add('$')
    
    # Check all productions where symbol appears
    for prod in productions:
        rhs = prod.split('->')[1]  # Get right-hand side
        
        # If our symbol appears in this production
        if symbol in rhs:
            pos = rhs.index(symbol)  # Find its position
            
            # Case 1: Symbol is not last in production
            if pos+1 < len(rhs):
                next_sym = rhs[pos+1]  # Get next symbol
                # Add FIRST of next symbol (except epsilon)
                result.update(first(next_sym) - {'$'})
    return result

# STEP 5: Calculate and display results for all non-terminals
print("\nResults:")
for nt in sorted(non_terminals):  # Process in alphabetical order
    print(f"FIRST({nt}): {first(nt)}")
    print(f"FOLLOW({nt}): {follow(nt)}")
    print()
------------------------------------------------------------------------------------------------------------------
                   
EXP 6    
EXP 6:LL(1) PARSER:
CODE:
table={'E':{'id':'TR','(':'TR'},'R':{'+':'+TR',')':'e','$':'e'},'T':{'id':'FY','(':'FY'},'Y':{'+':'e','*':'*FY',')':'e','$':'e'},'F':{'id':'id','(':'(E)'}}
inp='id + id * id $'
w=inp.split(' ')
i=0
word=w[i]
stack=[]
stack.append('$')
stack.append('E')
focus=stack[1]
terminal=['*','+','*','id','(',')','e','-','$']
while(focus):
print('f',focus)
print('w',word)
if(focus=='$' and word=='$'):
print('input string is valid')
break
elif(focus in terminal):
if(focus == word):
print('reduce')
stack.pop()
s=len(stack)-1
focus=stack[s]
i=i+1
word=w[i]
else:
e=stack.pop()
print(table[e])
if(word not in table[e]):
print('error')
break;
if(table[e][word]):
right=table[e][word]
if(right=='id'):
stack.append('id')
else:
for j in range(len(right)-1,-1,-1):
if(right[j]!='e'):
stack.append(right[j])
print(stack)
s=len(stack)-1
focus=stack[s]                
----------------------------------------------------------------------------------------------------------------------------------
                  
EXP 7: LR(1) PARSER:
CODE:
ACTION = {0 : {'id' : 5, '(' : 4},1 : {'+' : 6, '$' : '*'}, 2 : {'+' : -2, '*' : 7, ')' : -2, '$' : -2},3 : {'+' : -4, '*' : -4, ')' : -4, '$' : -4}, 4 : {'id' : 5, '(' : 4},5 : {'+' : -6, '*' : -6, ')' : -6, '$' : -6},6 : {'id' : 5, '(' : 4},7 : {'id' : 5, '(' : 4},8 : {'+' : 6, ')' : 11},9 : {'+' : -1, '*' : 7, ')' : -1, '$' : -1},10 : {'+' : -3, '*' : -3, ')' : -3, '$' : -3},11 : {'+' : -5, '*' : -5, ')' : -5, '$' : -5}}
GOTO = {0 : {'E' : 1, 'T' : 2, 'F' : 3},4 : {'E' : 8, 'T' : 2, 'F' : 3},6 : {'T' : 9, 'F' : 3},7 : {'F' : 10}}
GRAMMAR = [None,('E' , ['E', '+', 'T']),('E' , ['T']),('T' , ['T' , '*', 'F']),('T' , ['F']),('F' , ['(', 'E', ')']),('F' , ['id'])]
sentence = input("Enter the statement: ").strip().split()
stack = ['$', 0]
i = 0
while True:
if i >= len(sentence) or sentence[i] not in ACTION[stack[-1]]:
print("Failed!!")
break
if ACTION[stack[-1]][sentence[i]] == '*':
print("Success!!")
break
elif ACTION[stack[-1]][sentence[i]] < 0:
A, B = GRAMMAR[-ACTION[stack[-1]][sentence[i]]]
for _ in range(2*len(B)):
stack.pop()
stack.append(A)
stack.append(GOTO[stack[-2]][A])
else:
stack.append(sentence[i])
stack.append(ACTION[stack[-2]][sentence[i]])
i += 1
SAMPLE INPUT AND OUTPUT:
Enter the statement: id + id * id + ( id + id ) $
Success!!
Enter the statement: ( id + id ) * id $
Success!!
Enter the statement: ( ( id + id ) * ( id + id ) * id ) * ( id + id ) $
Success!!
Enter the statement: ( id + id ) * id * id + id + id $
Success!!
Fail Cases
Enter the statement: ( id + id ) * id * id + id id $
Failed!!
------------------------------------------------------------------------------------------------------------------------------------------------
                   
EXP 8: IF TO SWITCH:
CODE:
(i) LEX PROG:
%{ #include<stdio.h>
#include "y.tab.h"
extern int yylval; 
%}
%% [ /t] ; "if" return IF; "else" return ELSE; 
          "printf" return PRINTF; [a-zA-Z%][a-zA-Z0-9+]* {yylval = strdup(yytext); return ID;} "{" return OB;
           "}" return CB; "(" return OP; ")" return CP; [0-9]+ {yylval = atoi(yytext); return NUM;} "==" return EQ;
           ";" return SC; "," return COM; \" {yylval = strdup(yytext);return QUOT;} . return yytext[0]; %%
(ii) YACC PROG:
%{ #include<stdio.h>
int cnt=0;
 %} 
%token NUM IF ELSE ELIF PRINTF ID OB CB OP CP SC COM QUOT EQ 
%start S 
%%
S: if elif | if else {printf("VALID PROG!");} ;
if: IF OP ID EQ NUM CP {printf("switch(%s)\n{\ncase %d:",$3,cnt);} text;
elif:elif elif | ELSE IF OP ID EQ NUM CP {cnt++; printf("case %d:",cnt);} text | else;
else: ELSE {printf("default:");} def ;
text: PRINTF OP QUOT ID QUOT COM ID CP SC {printf("printf(%s%s%s,%s);",$3,$4,$5,$7);};
def: PRINTF OP QUOT ID QUOT CP SC {printf("printf(%s%s%s);\n}",$3,$4,$5);};
%%
yyerror()   
{ printf("Error!"); }
main() { yyparse(); }
INPUT FILE: (inp.txt)
if(a==0) printf("%d",a); else if(a==1) printf("%d",a+1); else if(a==2) printf("%d",a+2); else printf("default");          
./a.out <int.txt

 ===============         
/* C3: Use YACC to implement: Expression values evaluation (Desktop calculator). */
          

File C3.y
/* definition section*/
%{
#include <stdio.h>
#include <ctype.h>
int x[5],y[5],k,j[5],a[5][10],e,w;
%}
%token digit
%%
S : E { printf("\nAnswer : %d\n",$1); }
;
E : T { x[e]=$1; } E1 { $$=x[e]; }
;
E1 : '+' T { w=x[e]; x[e]=x[e]+$2; printf("Addition Operation %d
and %d : %d\n",w,$2,x[e]); } E1 { $$=x[e]; }
| '-' T { w=x[e]; x[e]=x[e]-$2; printf("Subtraction Operation
%d and %d : %d\n",w,$2,x[e]); } E1 { $$=x[e]; }
| { $$=x[e]; }
;
T : Z { y[e]=$1; } T1 { $$=y[e]; }
;
T1 : '*' Z { w=y[e]; y[e]=y[e]*$2; printf("Multiplication
Operation of %d and %d : %d\n",w,$2,y[e]); } T1 { $$=y[e]; }
| { $$=y[e]; }
;
Z : F { a[e][j[e]++]=$1; } Z1 { $$=$3; }
;
Z1 : '^' Z { $$=$2; }

| { for(k=j[e]-1;k>0;k--) { w=a[e][k-1]; a[e][k-
1]=powr(a[e][k-1],a[e][k]); printf("Power Operation %d ^ %d :

%d\n",w,a[e][k],a[e][k-1]); } $$=a[e][0]; j[e]=0; }
;
F : digit { $$=$1; printf("Digit : %d\n",$1); }
| '(' { e++; } E { e--; } ')' { $$=$3; }

2

;
%%
int main()
{
for(e=0;e<5;e++) { x[e]=y[e]=0; j[e]=0; }
e=0;
printf("Enter an expression\n");
yyparse();
return 0;
}
yyerror()
{
printf("NITW Error");
}
// when the input is finished yywrap is called to exit the code
int yywrap()
{
return 1;
}

int powr(int m,int n)
{
int ans=1;
while(n) { ans=ans*m; n--; }
return ans;
}
File C3.l
/* definitions */
%{
#include "y.tab.h"
#include <stdlib.h>

extern int yylval;
%}
%%

[0-9]+ {yylval=atoi(yytext);return digit;}

[\t] ;

[\n] return 0;

last match.
. return yytext[0];
%%          
========================================================
logical expression 
.y
/* File C3.y - Logical Expression Evaluator */
%{
#include <stdio.h>
#include <ctype.h>
#include <stdbool.h>

int yylval;
bool eval_stack[10];
int stack_ptr = 0;
%}

%token TRUE FALSE
%token AND OR NOT

%left OR
%left AND
%right NOT

%%
input:    /* empty */
        | input expr '\n' { printf("Result: %s\n", $2 ? "true" : "false"); }
        | input '\n'
        ;

expr:    expr OR expr     { $$ = $1 || $3; }
        | expr AND expr   { $$ = $1 && $3; }
        | NOT expr        { $$ = !$2; }
        | '(' expr ')'    { $$ = $2; }
        | TRUE            { $$ = true; }
        | FALSE           { $$ = false; }
        ;
%%

int main() {
    printf("Logical Expression Evaluator\n");
    printf("Enter expressions using true, false, &&, ||, !\n");
    yyparse();
    return 0;
}

int yyerror(char *s) {
    fprintf(stderr, "Error: %s\n", s);
    return 0;
}

int yywrap() {
    return 1;
}
          
.l
          
/* File C3.l - Lexer for Logical Expressions */
%{
#include "y.tab.h"
%}

%%
true        { yylval = true; return TRUE; }
false       { yylval = false; return FALSE; }
"&&"        { return AND; }
"\|\|"      { return OR; }
"!"         { return NOT; }
[()\n]      { return yytext[0]; }
[ \t]       ; /* ignore whitespace */
.           { printf("Invalid character: %s\n", yytext); }
%%
          
output
true && false
!(true || false)
true && (false || true)

------------------------------------------------------------------------------------------------------------------------
EXP 9A: THREE ADDRESS CODE:
CODE:
(i)LEX PROG:
%{
#include<stdio.h>
#include "y.tab.h"
extern int yylval;
%}
%%
[ \t\n] ;
[0-9]+ {yylval=strdup(yytext); return NUM;}
[_a-zA-Z][_0-9a-zA-Z]* {yylval=strdup(yytext); return ID;}
"+" {yylval=strdup(yytext);return ADD;}
"-" {yylval=strdup(yytext);return SUB;}
"*" {yylval=strdup(yytext);return MUL;}
"/" {yylval=strdup(yytext);return DIV;}
">" {yylval=strdup(yytext);return GT;}
"<" {yylval=strdup(yytext);return LT;}
"=" {yylval=strdup(yytext);return EQ;}
";" {return SC;}
"," {return C0M;}
"{" {return OB;}
"}" {return CB;}
"(" {return OP;}
")" {return CP;}
. return yytext[0];
%%
(ii)YACC PROG:
%{
#include "y.tab.h"
#include <stdio.h>
count=1;
%}
%token ID FS GT LT PL AK BS MI EQ AD OR XR MD IV QM CN SC CM OB CB OP CP IC
%%
S: statements {printf("\n\nvalid!!\n\n");} ;
statements: statement statements | statement ;
statement: ID EQ E {printf("%s = %s\n", $1, $3);};
E: E PL T {printf("t%d = %s %s %s\n", count, $1, $2, $3); sprintf($$, "t%d", count); count++;} | value {$$ = $1;}
| E MI T {printf("t%d = %s %s %s\n", count, $1, $2, $3); sprintf($$, "t%d", count); count++;} | value {$$ = $1;}
| T ;
T: T AK F {printf("t%d = %s %s %s\n", count, $1, $2, $3); sprintf($$, "t%d", count); count++;} | value {$$ = $1;}
| T BS F {printf("t%d = %s %s %s\n", count, $1, $2, $3); sprintf($$, "t%d", count); count++;} | value {$$ = $1;}
| F ;
F: OP E CP {$$ = $2;} | value {$$ = $1;};
value: IC | ID {$$ = $1;};
operator: PL | AK | MI | BS {$$ = $1;};
%%
void yyerror(){
printf("Invalid Syntax!");
}
int main(){
yyparse();
return 0;
}
INPUT FILE:(inp.txt)
a=b+c*d
OUTPUT:
t1 = c * d
t2 = b + t1
a = t2
valid!!
 =====================================         
EXP 9B: POSTFIX EXP:
CODE:
(i)LEX PROG:
%{
#include<stdio.h>
#include "y.tab.h"
extern int yylval;
%}
%%
[0-9]+ {yylval = atoi(yytext); return NUM;}
[a-z][a-zA-Z]* {yylval=strdup(yytext);return ID;}
[\n\t] return 0;
. return yytext[0];
%%
yywrap() {return 1;}
(ii)YACC PROG:
%{
#include <stdio.h>
#include <stdlib.h>
%}
%token NUM ID
%left '+''-'
%left '*''/'
%%
start:T;
T: T'+'T {printf("+");}
| T'-'T {printf("-"); }
| T'*'T {printf("*"); }
| T'/'T {printf("/");}
| NUM {printf("%d",$1);}
| ID {printf("%s",$1);}
;
%%
int main()
{
printf("\nEnter expression:");
yyparse();
return 0;
}
int yyerror()
{
printf("Error");
}
INPUT:
a+b*c
OUTPUT:
abc*+        
-------------------------------------------------------------------------------------------------------------------
          
EXP 10: COMMON SUB EXP ELIMINATION:
CODE:
import java.io.*;
import java.util.*;
import java.lang.*;
class mod
{
public static void main(String args[])throws IOException
{
String s,temp;
Scanner sc= new Scanner(System.in);
System.out.println("Enter the size");
int size=sc.nextInt();
String arr[][]=new String[size][2];
int flag=0,index=0;
BufferedReader br=new BufferedReader(new InputStreamReader(new FileInputStream("input.txt")));
for(;(s=br.readLine())!=null;flag=0)
{
arr[index][0]=s.substring(0,s.indexOf("="));
arr[index][1]=s.substring(s.indexOf("=")+1);
index++;
}
for(int i=1;i<arr.length;i++)
{
for(int j=i-1;j>=0;j--)
{
if(arr[i][1].equals(arr[j][1]))
{
arr[i][1]=arr[j][0];
break;
}
}
}
for(int i=0;i<arr.length;i++)
{
System.out.println(arr[i][0]+"="+arr[i][1]);
}
}
}
INPUT FILE:(input.txt)
a=b
b=a+e*f
c=b
d=a+e*f
OUTPUT:    
-------------------------------------------------------------------------------------------------------------------
11. Use LEX &amp; YACC to write a back end that traverses the three address intermediate code and generates
x86 code.
EXP 11: CODE GENERATION(machine lang):
CODE:
(i) LEX PROG:
%{
#include<stdio.h>
#include "y.tab.h"
extern int yylval;
%}
%%
[0-9]+ {yylval=strdup(yytext); return IC;}
[_a-zA-Z][_0-9a-zA-Z]* {yylval=strdup(yytext); return ID;}
"+" {yylval=strdup(yytext);return PL;}
"-" {yylval=strdup(yytext);return MI;}
"*" {yylval=strdup(yytext);return AK;}
"/" {yylval=strdup(yytext);return BS;}
"\\" {yylval=strdup(yytext);return FS;}
">" {yylval=strdup(yytext);return GT;}
"<" {yylval=strdup(yytext);return LT;}
"=" {yylval=strdup(yytext);return EQ;}
"&" {yylval=strdup(yytext);return AD;}
"|" {yylval=strdup(yytext);return OR;}
"^" {yylval=strdup(yytext);return XR;}
"%" {yylval=strdup(yytext);return MD;}
"~" {yylval=strdup(yytext);return IV;}
"?" {yylval=strdup(yytext);return QM;}
":" {yylval=strdup(yytext);return CN;}
";" {return SC;}
"," {return CM;}
"{" {return OB;}
"}" {return CB;}
"(" {return OP;}
")" {return CP;}
%%
(ii)YACC PROG:
%{
#include "y.tab.h"
#include <stdio.h>
count=1;
%}
%token ID FS GT LT PL AK BS MI EQ AD OR XR MD IV QM CN SC CM OB CB OP CP IC
%%
S: statements {printf("\n\nvalid!!\n\n");} ;
statements: statement statements | statement ;
statement: ID EQ E SC {printf("STR[%s], %s\n\n", $1, $3);};
E: value operator value {
$$=$1;
if (!strcmp($2, "+"))
printf("ADD %s, %s\n", $1, $3);
else if (!strcmp($2, "-"))
printf("SUB %s, %s\n", $1, $3);
else if (!strcmp($2, "*"))
printf("MUL %s, %s\n", $1, $3);
else if (!strcmp($2, "/"))
printf("DIV %s, %s\n", $1, $3);
};
value: IC {printf("LOAD R%d, %s\n", count, $1); sprintf($$, "R%d", count++);}
| ID {printf("LOAD R%d, [%s]\n", count, $1); sprintf($$, "R%d", count++);};
operator: PL | AK | MI | BS {$$ = $1;};
%%
void yyerror(){
printf("Invalid Syntax!");
}
int main(){
yyparse();
return 0;
}
INPUT FILE (input.txt):
a=b+c;
c=a*d;
OUTPUT:       
--------------------------------------------------------------------------------------------------------------------------------

12 list scheduling 
from collections import defaultdict, deque
from heapq import heappop, heappush

def main():
    # Get instruction delays
    delays = {}
    print("Enter operations and their costs (format: 'op cost', blank line to stop):")
    while True:
        line = input().strip()
        if not line:
            break
        op, cost = line.split()
        delays[op] = int(cost)

    # Build dependency graph
    successors = defaultdict(list)
    predecessors = defaultdict(list)
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    
    print("\nEnter dependencies (format: 'op1 op2', blank line to stop):")
    while True:
        line = input().strip()
        if not line:
            break
        u, v = line.split()
        successors[u].append(v)
        predecessors[v].append(u)
        in_degree[v] += 1
        out_degree[u] += 1

    # Calculate priorities (critical path length)
    priority = {}
    queue = deque(op for op in delays if op not in successors or not successors[op])
    
    while queue:
        node = queue.popleft()
        priority[node] = delays[node]
        for pred in predecessors[node]:
            priority[pred] = max(priority.get(pred, 0), priority[node] + delays[pred])
            out_degree[pred] -= 1
            if out_degree[pred] == 0:
                queue.append(pred)

    # Scheduling
    print("\nScheduling Timeline:")
    cycle = 1
    ready_heap = [(-priority[op], op) for op in delays if in_degree[op] == 0]
    active_ops = []
    
    while ready_heap or active_ops:
        # Complete finished operations
        completed = set()
        for start_cycle, op in active_ops:
            if start_cycle + delays[op] <= cycle:
                completed.add(op)
                for successor in successors[op]:
                    in_degree[successor] -= 1
                    if in_degree[successor] == 0:
                        heappush(ready_heap, (-priority[successor], successor))
        
        active_ops = [(c, op) for c, op in active_ops if op not in completed]
        
        # Print current state
        ready_ops = [op for _, op in ready_heap]
        active_ops_list = [op for _, op in active_ops]
        print(f"Cycle {cycle}: Ready={ready_ops}, Active={active_ops_list}")
        
        # Schedule next operation if possible
        if ready_heap:
            _, next_op = heappop(ready_heap)
            active_ops.append((cycle, next_op))
        
        cycle += 1
    
    print(f"\nTotal cycles needed: {cycle-1}")

if __name__ == "__main__":
    main()
            
          """)