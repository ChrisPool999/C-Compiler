// NOTES:
// (when math is being done, just consider it all one expression to be calculated) -- can pre-work anything constants as well (optimize)
// main = special id that shows the start of the code being executed
// () = encloses arguments or expressions
// commas are used in arguments, variable declarations, for loops, init lists, 

// RULES: 
// E                                                                               --> valid but should remove for performance
// ID                                                                              --> valid but should remove for performance  

// T + N-ID                                                                        --> declaration
// T + N-ID + A + E                                                                --> declaration + assignment
// T + N-ID + [size]                                                               --> declaration
// T + N-ID + [size] + E                                                           --> declaration + assignment

// ID + A + E                                                                      --> assignment
// ARR + initializer list                                                          --> assignment
// function call                                                                   --> function call

// if + E + S                                                                      --> condition
// else if + E + S                                                                 --> condition
// else + S                                                                        --> condition

// while + E + S                                                                   --> loop
// for + declartion & A + E + single line S + S                                    --> loop

// return + E                                                                      --> return
// return                                                                          --> return void
// break                                                                           --> break
// continue                                                                        --> continue

// ___________________________________________________________________________________________________________________________________________
// TYPE
// ID (FUNCTION NAME / POINTER, VARIABLE)
// EXPRESSION (NUMBER, STRING, CHAR, BOOL, REFERENCE, POINTER, ARRAY, ARRAY INDEX, RETURNING FUNCTION CALL)
// OPERATORS (includes operators)

// FUNCTION DECLARATION --> always the end
// BLOCK STATEMENT      --> always the end

// branching  
//    <if/else> <expression> <block statement>
//    <else> <block statement>                                  (must have if condition to use)
// loops
//    <while> <expression> <statement>
//    <for> <init> <expression> <iteration> <statement>
// jumps
//    <break>
//    <continue>
//    <return> <expression>
// declare function
//    <type> <name> <arguments> <statement>
// single line statements
// <type>
// <type> <ID>
// <type> <ID> = <expression>
// <ID>
// <ID> = <expression>
// <expression>
// <function call>

int main()
{
  int foo = 0b000;
  int boo = ~0b0001;
}