#include <iostream>
#include "lexer.h"

template <typename T>
bool contains(std::vector<T> vec, T val) {
  for (auto v : vec) if (v == val) return true;
  return false;
}  

bool contains(const std::vector<char*> vec, const char* val) {
  for (auto v : vec) {
    if (std::strcmp(v, val) == 0) {
      return true;
    }
  }
  return false;
}  

bool isWhiteSpace(const char ch) {
  return (ch == ' ' || ch == '\t' || ch == '\n' || ch == '\0');
}

bool isComment(const std::string& input, const uint32_t i) {
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

bool Lexer::isOperator(char ch, char ch2 = '\0') const {
  if (ch2 == '\0') {
    for (const auto &op : operators) {
      if (op[0] == ch && op[1] == '\0') {
        return true;
      }
    }
  }
  else {
    for (const auto &op : operators) {
      if (op[0] == ch && op[1] == ch2) {
        return true;
      }
    }  
  }
  return false;    
}

int32_t Lexer::findTokenStart(uint32_t i) const {
  while (i < srcLine.size() && isWhiteSpace(srcLine[i])) {
    i++;
  }
  
  if (i >= srcLine.size() || isComment(srcLine, i)) {
    return -1;
  }
  
  return i;
}

TokenType Lexer::findTokenType(const uint32_t start) {
  char ch = srcLine[start];
  if (isalnum(ch) || ch == '_') {
    // identifier or token
  }
  if (std::isdigit(ch) || ch == '.') {
    pendingToken.type = TokenType::CONSTANT;
  }
  if ()
}

uint32_t Lexer::findTokenEnd(uint32_t start) const {
  char ch = srcLine[start];
  if (isalpha(ch) || ch == '_') {
    while (isalnum(ch) || ch == '_') {
      start++;
    }
    return start;
  }

  if (ch == '"') {
    start++;
    while (ch != '"') {
      start++;
    }
    return start;
  }

  if (ch == '.' || std::isdigit(ch)) {
    bool hasDecimal = false;
    while (std::isdigit(ch) || (ch == '.' && !hasDecimal)) {
      if (ch == '.') {
        hasDecimal = true;
      }
      start++;
    }
    return start;
  }

  if (isPunctuator(ch)) {
    return ++start;
  }

  if (start + 1 < srcLine.size() && isOperator(ch, srcLine[start + 1])) {
    return start + 2;
  }

  if (isOperator(ch)) {
    return start + 1;
  }

  return -1; // error
}

TokenType Lexer::getTokenType
    (const u_int32_t start, const u_int32_t end) const {
}

int main() {
  std::cout << sizeof(TokenType) << std::endl;
}


// identifiers: handle WITH regex. ends when legit anything else other than alphanumber + '_'
// string: handle w/o regex
// constants: handle WITH regex 
// keywords: after checking for identifier, see if it matches with a keyword
// operators: handle w/o regex
// punctuators: handle w/o regex 

// literals, keywords, constants, and identifiers MUST only be surrounded by spaces or operators / punctuators

// identifer must start with letter or underscore
// number must start with number but only include numbers
//--------------------------------------------------------------------------------------------------------

// ID:          punctuator, operator, whitespace, 
// STRING:      Quote
// CONSTANT:    punctuator, operator, whitespace (NOT decimal)
// KEYWORD:     punctuator, operator, whitespace, 
// OPERATOR:    base it off size
// PUNCTUATOR:  base it off size

// ends if space, punctuator, operator 

// letter -> ID, Keyword
// int    -> constant or decimal
// Quotes -> String
// nothing else? == operator or symbol 