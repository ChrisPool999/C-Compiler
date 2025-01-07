#include <iostream>
#include <exception>
#include "lexer.h"

static std::string tokenAsStr(TokenType type) {
  if (type == TokenType::CONSTANT) return "CONSTANT";
  if (type == TokenType::END_OF_FILE) return "END_OF_FILE";
  if (type == TokenType::IDENTIFER) return "IDENTIFER";
  if (type == TokenType::KEYWORD) return "KEYWORD";
  if (type == TokenType::OPERATOR) return "OPERATOR";
  if (type == TokenType::PUNCTUATORS) return "PUNCTUATORS";
  if (type == TokenType::STRING) return "STRING";
  throw std::runtime_error("unknown type");
}

static bool isWhiteSpace(const char ch) {
  return (ch == ' ' || ch == '\t' || ch == '\n' || ch == '\0');
}

static bool isComment(const std::string& input, const uint32_t i) {
  return i + 1 < input.size() && input[i] == '/' && input[i+1] == '/';
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
void Lexer::throwError(const std::string msg) {
  std::string error = "line " + std::to_string(line + 1) 
      + "col " + std::to_string(col + 1) + ": " + msg;
  throw SyntaxException(error);
}

bool Lexer::isPunctuator(const char ch) const {
  for (auto p : Lexer::punctuators) {
    if (p == ch) {
      return true;
    }
  }
  return false;
}

bool Lexer::isOperator(const char ch, const char ch2) const {
  for (const auto &op : dblOperators) {
    if (op[0] == ch && op[1] == ch2) {
      return true;
    }
  }
  return false;
}

bool Lexer::isOperator(const char ch) const {
  for (const char op : operators) {
    if (op == ch) {
      return true;
    }
  }  
  return false;    
}

bool Lexer::isKeyword(const std::string& str) const {
  auto it = std::find(keywords.begin(), keywords.end(), str); 
  return it != keywords.end();
}

bool Lexer::isConstant(std::string& str, uint32_t i) const {
  char ch = str[i];
  return isdigit(ch) ||
      ( 
        (ch == '+' || ch == '-' || ch == '.') && 
        col + 1 <= srcLine.size() &&
        isdigit(srcLine[col + 1])
      ) || 
      (
        (ch == '+' || ch == '-') &&
        col + 2 <= srcLine.size() &&
        srcLine[col + 1] == '.' &&
        isdigit(srcLine[col + 2])
      );
}

void Lexer::skipWhiteSpace() {
  while (col < srcLine.size() && isWhiteSpace(srcLine[col])) {
    col++;
  }
}

void Lexer::setToken(const TokenType type, const std::string value) {
  pendingToken.type = type;
  pendingToken.value = value;
}

// only matches with same quote type, eg single quote or double quote
void Lexer::setString() {
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
  
void Lexer::setWithRegex(const TokenType type, const std::regex& regex) {
  static std::smatch match;

  std::string subStr = srcLine.substr(col);
  if (std::regex_search(subStr, match, regex)) {
    setToken(type, match.str());
  } else {
    throwError("Invalid suffix on " + tokenAsStr(type));
  }
}

// order is important, FOR EXAMPLE: parseString must be 
// checked first or the quote will be marked as a punctuator
void Lexer::processToken() {
  char ch = srcLine[col];
  if (ch == '\'' || ch == '\"') {
    setString();
  }
  else if (isConstant(srcLine, col)) {
    setWithRegex(TokenType::CONSTANT, regexConstant);
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
  else if (isalpha(ch) || ch == '_') {
    setWithRegex(TokenType::IDENTIFER, regexID);
    if (isKeyword(pendingToken.value)) {
      pendingToken.type = TokenType::KEYWORD;
    }
  }
  else {
    throwError("Invalid character: -> " + std::string(1, ch));
  }
}

void Lexer::getNextLine() {
  std::getline(file, srcLine);
  line++;
  col = 0;
}

void Lexer::batchTokens() {
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
    batchTokens();
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
    std::cout << t.getLine() << "-" << t.getCol() << " " << t.getValue() << " " << tokenAsStr(t.getType()) <<std::endl;
  }
  return 0;
}

// TESTING
// BENCHMARKING
// DOCKER
// AUTOMATION (CMake, Tests, Benchmarking)
// ASYNCHRONIOUS (Threading will improve performance since Parser won't be waiting on I/O Reads)

// any final refactoring