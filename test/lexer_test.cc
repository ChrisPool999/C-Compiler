#include "lexer.cc"
#include <gtest/gtest.h>

TEST(LexerTests, Constructor) {
  try {
    Lexer lex = Lexer("doesnt_exist.c");
    FAIL() << "Lexer should throw an exception if the file doesn't exist";
  }
  catch (std::ios_base::failure& e) {
    SUCCEED();
  } catch (...) {
    FAIL() << "Expected ios_base::failure. Got different exception"; 
  }
}


// check empty lines and random white space
// check comments work
// check all punctuator types
// check all operator types
// check all keywords
// check string with both 'quotes' and "quotes"
// check string that doesnt have an enclosing brace
// check invalid suffix on regex search (ID, CONSTANT, KEYWORD)
// check all different kinds of constant +34  -.9943
// check peepNextToken()
// check requestToken()
// check all kinds of different types to ensure its picked up -
// - and that the col ends where it should



// fix dot operator... eg foo.info