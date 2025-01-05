#include <iostream>
#include <exception>
#include "lexer.h"

class SyntaxException : public std::exception {
  std::string message;
public:
  explicit SyntaxException(const std::string& msg) : message(msg) {}

  const char* what() const noexcept override {
    return message.c_str();
  }
};

static bool isWhiteSpace(const char ch) {
  return (ch == ' ' || ch == '\t' || ch == '\n' || ch == '\0');
}

static bool isComment(const std::string& input, const uint32_t i) {
  return i + 1 < input.size() && input[i] == '/' && input[i+1] == '/';
}

bool Lexer::isPunctuator(const char ch) const {
  for (auto p : punctuators) {
    if (p == ch) {
      return true;
    }
  }
  return false;
}

bool Lexer::isOperator(const char ch, const char ch2) const {
  for (const auto &op : operators) {
    if (op[0] == ch && op[1] == ch2) {
      return true;
    }
  }
  return false;
}

bool Lexer::isOperator(const char ch) const {
  for (const auto &op : operators) {
    if (op[0] == ch) {
      return true;
    }
  }  
  return false;    
}

bool Lexer::isKeyword(std::string& str) {
  auto it = std::find(keywords.begin(), keywords.end(), str); 
  return it != keywords.end();
}

void Lexer::skipWhiteSpace() {
  while (col < srcLine.size() && isWhiteSpace(srcLine[col])) {
    col++;
  }
}

void Lexer::setToken(TokenType type, std::string value) {
  pendingToken.type = type;
  pendingToken.value = value;
}

void Lexer::parseString() {
  uint32_t i = col + 1;
  std::string tokenValue = "";

  while (i < srcLine.size() && srcLine[i] != '"') {
    tokenValue += srcLine[i];
    i++;
  }

  if (i >= srcLine.size()) {
    char error[] = "line %d col %d: Missing enclosing quotation", line, col; 
    throw SyntaxException(std::string(error));
  }

  setToken(TokenType::STRING, tokenValue);
}
  
void Lexer::parseWithRegex(TokenType type, std::regex& regex) {
  static std::smatch match;

  std::string subStr = srcLine.substr(col);
  if (std::regex_search(subStr, match, regex)) {
    setToken(type, match.str());
  } else {
    char error[] = "line %d col %d: Invalid syntax", line, col; 
    throw SyntaxException(std::string(error));
  }
}

void Lexer::processToken() {
  char ch = srcLine[col];
  if (isPunctuator(ch)) {
    setToken(TokenType::PUNCTUATORS, std::string(1, ch));
  }
  else if (col + 1 < srcLine.size() && isOperator(ch, srcLine[col + 1])) {
    setToken(TokenType::OPERATOR, std::string() + ch + srcLine[col + 1]);
  }
  else if (isOperator(ch)) {
    setToken(TokenType::OPERATOR, std::string(1, ch));
  }
  else if (ch == '"') {
    parseString();
  }
  else if (ch == '.' || std::isdigit(ch)) {
    parseWithRegex(TokenType::CONSTANT, regexConstant);
  }
  else if (isalnum(ch) || ch == '_') {
    parseWithRegex(TokenType::IDENTIFER, regexConstant);
    if (isKeyword(pendingToken.value)) {
      pendingToken.type = TokenType::KEYWORD;
    }
  }
  else {
    char error[] = "line %d col %d: Invalid character -> %c", line, col, ch; 
    throw SyntaxException(std::string(error));
  }
}

// returns true if EOF reached
bool Lexer::getNextLine() {
  if (file.eof()) {
    return false;
  }
  std::getline(file, srcLine);
  line++;
  col = 0;
  return true;
}

// returns true if EOF reached
bool Lexer::fillBuffer() {
  while (buffer.size() != maxBufferSize) {
    skipWhiteSpace();  

    if (col >= srcLine.size()) {
      if (!getNextLine()) {
        return false;
      }
    }

    pendingToken.line = line;
    pendingToken.col = col;

    processToken();

    col += pendingToken.value.size();
    buffer.push(pendingToken);
  }
}

Lexer::Lexer(std::string filename) {
  file.open(filename);

  if (!file) {
    throw std::ios_base::failure("failed to open file: " + filename);
  }
  std::getline(file, srcLine);
}

Token Lexer::requestToken() {
  if (buffer.size() < minBufferSize) {
    fillBuffer();
  } 
  Token token = buffer.back();
  buffer.pop();
  return token;
}

const Token Lexer::peekNextToken() {
  if (!buffer.size()) {
    throw std::runtime_error("token buffer empty");
  }
  return buffer.back();
}

// handle both functions both returning bool for EOF yet not doing anything
// -- about it in the calling function
// TEST
// any final refactoring