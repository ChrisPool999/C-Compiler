#include "lexer.cc"
#include <gtest/gtest.h>

TEST(LexerTests, Constructor) {
  Lexer lex = Lexer("input.c");
  lex.requestToken();
  lex.peekNextToken();
  
}