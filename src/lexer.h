#include <fstream>
#include <vector>
#include <cstring>
#include <queue>

enum class TokenType {
  IDENTIFER,
  STRING,
  CONSTANT, 
  KEYWORD,
  OPERATOR,
  PUNCTUATORS
};

class Token {
  friend class Lexer;
  TokenType type;
  char* value = nullptr;
  uint32_t line;
  uint32_t col;
  // ASTNode* node = nullptr; // add in later 
public:
  TokenType getType() const {
    return type;
  }
  const char* getValue() const {
    return value;
  }
  uint32_t getLine() const {
    return line;
  }
  uint32_t getCol() const {
    return col;
  }
};

class Lexer {
  static constexpr uint32_t maxBufferSize = 128;
  std::queue<Token> buffer;
  Token pendingToken;

  std::ifstream file;
  std::string srcLine;
  uint32_t line = 1;
  uint32_t col = 1;

  const std::vector<char*> keywords = {
      "if", "else", "while", "for", "continue", 
      "return", "break", "main", "struct", "int",
      "short", "long", "float", "double", "char"
      "void", "struct", "static", "const", "extern"
  };  
  const std::vector<char*> operators = {
      ".", "!", "!=", "=", "==", "<", "<=", 
      ">", ">=","+", "+=", "-", "-=", "*", 
      "*=", "/", "/=", "%", "%=", "&&", "||"
  };
  const std::vector<char> punctuators = {
      ',', '[', ']', '(', ')', '{', '}', '\'', '\"', ';'
  };

  bool isPunctuator(char ch) const;
  bool isOperator(char ch, char ch2 = '\0') const;
  int32_t findTokenStart(uint32_t i) const;
  uint32_t findTokenEnd(const uint32_t start) const;
  TokenType findTokenType(const uint32_t start);
  void fillBuffer();

public:
  Token requestToken();
  Token peekNextToken();
};