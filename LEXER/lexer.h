#include <fstream>
#include <vector>
#include <cstring>
#include <queue>
#include <regex>

enum class TokenType {
  IDENTIFER,
  STRING,
  CONSTANT, 
  KEYWORD,
  OPERATOR,
  PUNCTUATORS,
  END_OF_FILE
};

// ASTNode* node = nullptr; // add in later 
class Token {
  friend class Lexer;
  std::string value = "";
  TokenType type;
  uint32_t line = -1;
  uint32_t col = -1;
public:
  Token() {};
  Token(TokenType type) {
    this->type = type;
  }
  TokenType getType() const {
    return type;
  }
  const std::string getValue() const {
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
  static constexpr uint32_t minBufferSize = maxBufferSize / 4;
  std::queue<Token> buffer;
  Token pendingToken = Token();

  std::ifstream file;
  std::string srcLine;
  uint32_t line = 0;
  uint32_t col = 0;
  const std::regex regexID = std::regex("^[_A-Za-z]+[_A-Za-z0-9]*\\b");
  const std::regex regexConstant = std::regex("^(?=.*\\d)[+-]?\\d*.?\\d*\\b");

  void throwError(const std::string msg);
  bool isPunctuator(const char ch) const;
  bool isOperator(const char ch, const char ch2) const;
  bool isOperator(const char ch) const;
  bool isKeyword(const std::string& str) const;
  bool isConstant(std::string& str, uint32_t i) const;
  void skipWhiteSpace();
  void setToken(const TokenType type, const std::string val);
  void setString();
  void setWithRegex(const TokenType type, const std::regex& regex);
  void processToken();
  void getNextLine();
  void batchTokens();
public:
  const std::vector<std::string> keywords = {
      "if", "else", "while", "for", "continue", 
      "return", "break", "main", "struct", "int",
      "short", "long", "float", "double", "char",
      "void", "static", "const", "extern"
  };  
  const std::vector<char> operators = {
      '.', '!', '=', '<', '>', '+', '-', '*', '/', '%'
  };
  const std::vector<std::string> dblOperators = {
      "!=", "==", "<=", ">=", "+=", "-=", "*=", "/=", "%=", "&&", "||"
  };
  const std::vector<char> punctuators = {
      ',', '[', ']', '(', ')', '{', '}', '\'', '\"', ';'
  };

  Lexer(std::string filename);
  Token requestToken();
  const Token peekNextToken();
};