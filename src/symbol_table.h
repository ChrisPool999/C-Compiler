#include <unordered_map>
#include <stack>
#include <list>
#include <string>
#include <stdint.h>
#include <iostream>
#include <vector>
 
constexpr uint32_t flag(int bit) {
  return 1 << bit;
}

enum class Flags {
  INT = flag(0),
  CHAR = flag(1),
  FLOAT = flag(2),
  DOUBLE = flag(3),
  VOID = flag(4),

  VARIABLE = flag(5),
  FUNCTION = flag(6),
  STRUCT = flag(7),

  ARRAY = flag(9),
  POINTER = flag(10),
  CONST = flag(8),
  STATIC = flag(10),
  EXTERN = flag(11),

  DEFINED = flag(12)
};

class Base {
  uint32_t flags = 0b0;
  uint32_t block;
  uint32_t* address;
  uint32_t lineDeclared;
  std::list<uint32_t> linesUsed;

  Flags getFlags(char*); 
  uint32_t getBlock();
  uint32_t* getAddress();
  uint32_t getLineDeclared();
  std::list<uint32_t> getLinesUsed();

  void setFlags(uint32_t flags);    
  void setAddress();
  void addLineUsed();
};

class Variable {
  Base base;
  uint32_t size;
  uint32_t dimension;
  char* initValue;

  uint32_t getSize();
  uint32_t getDimension();
  char* getInitValue();
  void setSize();
  void setDimension();
  void setInitValue();
};

class ParamList {
  std::vector<Flags> paramList;
  void setParamList();
  std::vector<Flags> getParamList();
};

class Function {
  Base base;
  ParamList parameters;
};

class Struct {
  Base base;
  ParamList parameters;
  uint32_t size;

  uint32_t getSize();
  void setSize();
};

class SymbolTable {
private:

  // first stack --> function stack      second stack --> variable shadowing 
  std::stack<std::unordered_map<std::string, std::stack<Symbol>>> table;
public:

  void addName(char* name, uint32_t block, uint32_t lineDeclared);
  void removeName(char* name);
  bool checkExists(char*);
  void functionCall();
  void functionEnd();
};

// get split this up into a variable, method, stack
// split up the properties

// -- goal, split into smaller classes, and combine them


  // struct - address, size, lineDeclared, linesUsed, paramList, 
  // function - address, lineDeclared, linesUsed, paramList, TYPE, KIND, KINDAttribute, DEFINED
  // variable - block, address, size, line declared, linesUsed, dimension, initValue, TYPE, KIND, KINDAttribute, defined