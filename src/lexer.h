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

  std::regex regexID = std::regex("^[_A-Za-z]+[_A-Za-z0-9]*\\b");
  std::regex regexConstant = std::regex("^[+-]?\\d*.?\\d*\\b");
  const std::vector<std::string> keywords = {
      "if", "else", "while", "for", "continue", 
      "return", "break", "main", "struct", "int",
      "short", "long", "float", "double", "char",
      "void", "struct", "static", "const", "extern"
  };  
  const std::vector<std::string> operators = {
      ".", "!", "!=", "=", "==", "<", "<=", 
      ">", ">=", "+", "+=", "-", "-=", "*", 
      "*=", "/", "/=", "%", "%=", "&&", "||"
  };
  const std::vector<char> punctuators = {
      ',', '[', ']', '(', ')', '{', '}', '\'', '\"', ';'
  };

  void throwError(std::string msg);
  bool isPunctuator(const char ch) const;
  bool isOperator(const char ch, const char ch2) const;
  bool isOperator(const char ch) const;
  bool isKeyword(std::string& str);
  void skipWhiteSpace();
  void setToken(TokenType type, std::string val);
  void parseString();
  void parseWithRegex(TokenType type, std::regex& regex);
  void processToken();
  void getNextLine();
  void fillBuffer();
public:
  Lexer(std::string filename);
  Token requestToken();
  const Token peekNextToken();
};