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

TokenType Lexer::getTokenType
    (const u_int32_t start, const u_int32_t end) const {

}

int main() {
  std::cout << sizeof(TokenType) << std::endl;
}

// keep going until we find a valid character... (use this to ignore all white space)
// - HAVE FOUND TOKEN START: 

// - catagorize type of token based on initial character
//   - function to handle each type of token based off intial character, eg letter and keyword or identifier
//   - return token type



// identifiers: handle WITH regex. ends when legit anything else other than alphanumber + '_'
// keywords: after checking for identifier, see if it matches with a keyword
// constants: handle WITH regex 
// literals: handle w/o regex
// operators: handle w/o regex
// punctuators: handle w/o regex 

// literals, keywords, constants, and identifiers MUST only be surrounded by spaces or operators / punctuators

// identifer must start with letter or underscore
// number must start with number but only include numbers

// must splice the regex search in C regex...

// do a findStart() and findEnd()

// findStart() -> pass through comments and white space, until we find a new character
// findEnd() -> go until a space or operator/punctuator is found

// findEnd solution:
// - slower, more flexible, allows easier maintaince and expansion

// break it down more based on first char:
// - find int
// - find identifier/keyword
// - find literal
// - dont need regex for operator, can have a isOperator() function