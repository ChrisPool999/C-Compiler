#include <iostream>
#include <exception>
#include "lexer.h"

std::string _DEBUG_getTokenTypeStr(TokenType type) {
  if (type == TokenType::CONSTANT) return "CONSTANT";
  if (type == TokenType::END_OF_FILE) return "END_OF_FILE";
  if (type == TokenType::IDENTIFER) return "IDENTIFER";
  if (type == TokenType::KEYWORD) return "KEYWORD";
  if (type == TokenType::OPERATOR) return "OPERATOR";
  if (type == TokenType::PUNCTUATORS) return "PUNCTUATORS";
  if (type == TokenType::STRING) return "STRING";
  throw std::runtime_error("unexpected tokentype passed");
}

class SyntaxException : public std::exception {
  std::string message;
public:
  explicit SyntaxException(const std::string& msg) : message(msg) {}

  const char* what() const noexcept override {
    return message.c_str();
  }
};

// line and col properties are 0-indexed
void Lexer::throwError(std::string msg) {
  std::string location = "line " + std::to_string(line + 1) 
      + "col " + std::to_string(col + 1) + ": ";
  throw SyntaxException(location + msg);
}

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

// only matches with same quote type, eg single quote or double quote
void Lexer::parseString() {
  char quoteType = srcLine[col];
  uint32_t i = col + 1;
  std::string tokenValue = "";

  while (i < srcLine.size() && srcLine[i] != quoteType) {
    tokenValue += srcLine[i];
    i++;
  }
  if (i >= srcLine.size()) {
    throwError("Missing enclosing quotation");
  }
  col = i + 1;
  setToken(TokenType::STRING, tokenValue);
}
  
void Lexer::parseWithRegex(TokenType type, std::regex& regex) {
  static std::smatch match;

  std::string subStr = srcLine.substr(col);
  if (std::regex_search(subStr, match, regex)) {
    setToken(type, match.str());
  } else {
    throwError("Invalid syntax");
  }
}

// order is important, FOR EXAMPLE: parseString must be 
// checked first or the quote will be marked as a punctuator
void Lexer::processToken() {
  char ch = srcLine[col];
  if (ch == '\'' || ch == '\"') {
    parseString();
  }
  else if (ch == '.' || std::isdigit(ch)) {
    parseWithRegex(TokenType::CONSTANT, regexConstant);
  }
  else if (isPunctuator(ch)) {
    setToken(TokenType::PUNCTUATORS, std::string(1, ch));
  }
  else if (col + 1 < srcLine.size() && isOperator(ch, srcLine[col + 1])) {
    setToken(TokenType::OPERATOR, std::string() + ch + srcLine[col + 1]);
  }
  else if (isOperator(ch)) {
    setToken(TokenType::OPERATOR, std::string(1, ch));
  }
  else if (isalnum(ch) || ch == '_') {
    parseWithRegex(TokenType::IDENTIFER, regexID);
    if (isKeyword(pendingToken.value)) {
      pendingToken.type = TokenType::KEYWORD;
    }
  }
  else {
    throwError("Invalid character ->" + ch);
  }
}

void Lexer::getNextLine() {
  std::getline(file, srcLine);
  line++;
  col = 0;
}

void Lexer::fillBuffer() {
  while (buffer.size() != maxBufferSize) {
    skipWhiteSpace();  

    if (col >= srcLine.size() || isComment(srcLine, col)) {
      if (file.eof()) {
        return;
      }
      getNextLine();
      continue;
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
  if (buffer.empty()) {
    return Token(TokenType::END_OF_FILE);
  }
  Token token = buffer.front();
  buffer.pop();
  return token;
}

const Token Lexer::peekNextToken() {
  if (!buffer.size()) {
    throw std::runtime_error("token buffer empty");
  }
  return buffer.back();
}

int main() {
  Lexer lex = Lexer("./test/test1.c");
  Token t;
  while ((t = lex.requestToken()).getType() != TokenType::END_OF_FILE) {
    std::cout << t.getLine() << "-" << t.getCol() << " " << t.getValue() << " " << _DEBUG_getTokenTypeStr(t.getType()) <<std::endl;
  }
  return 0;
}

// TESTING
// BENCHMARKING
// DOCKER
// AUTOMATION (CMake, Tests, Benchmarking)
// ASYNCHRONIOUS (Threading will improve performance since Parser won't be waiting on I/O Reads)

// any final refactoring