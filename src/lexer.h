#include <fstream>
#include <vector>
#include <cstring>
#include <queue>
#include "symbol_table.h"

enum class TokenType {
  IDENTIFER,
  STRING,
  CONSTANT, 
  KEYWORD,
  OPERATOR,
  SYMBOLS
};

using token = std::pair<char*, TokenType>;

class Lexer {
private:
  static constexpr uint32_t maxBufferSize = 128;
  std::queue<token> buffer;

  std::ifstream file;
  std::string input;
  int inputIdx = 0;
  SymbolTable symbolTable = SymbolTable();

  const std::vector<char*> keywords = {
      "if", "else", "while", "for", "continue", 
      "return", "break", "main", "struct", "int",
      "char", "float", "double", "void", "struct",
      "static", "const", "extern"
  };  
  const std::vector<char*> operators = {
      ".", "!", "!=", "=", "==", "<", "<=", 
      ">", ">=","+", "+=", "-", "-=", "*", 
      "*=", "/", "/=", "%", "%=", "&&", "||"
  };
  const std::vector<char*> symbols = {
      ",", "[", "]", "(", ")", "{", "}", "'", "\""
  };

  int findTokenStart(const int i) const;
  int findTokenEnd(const int start) const;
  TokenType getTokenType(const uint32_t start, const uint32_t end) const;
  void fillBuffer();

public:
  token requestToken();
  token peekNextToken();
};