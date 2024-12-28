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

class SymbolTable {
private:
  using Flags = uint32_t; 

  struct SymbolInfo {
    Flags flags = 0b0;
    uint32_t block;
    uint32_t* address;
    uint32_t size;
    uint32_t lineDeclared;
    std::list<uint32_t> linesUsed;
    uint32_t dimension;
    char* initValue;
    std::vector<Flags> paramList;
  };

  // first stack --> function stack      second stack --> variable shadowing 
  std::stack<std::unordered_map<std::string, std::stack<SymbolInfo>>> table;
public:
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

  // struct - address, size, lineDeclared, linesUsed, paramList, 
  // function - address, lineDeclared, linesUsed, paramList, TYPE, KIND, KINDAttribute, DEFINED
  // variable - block, address, size, line declared, linesUsed, dimension, initValue, TYPE, KIND, KINDAttribute, defined
  void addName(char* name, uint32_t block, uint32_t lineDeclared);
  void removeName(char* name);
  bool checkExists(char*);
  void functionCall();
  void functionEnd();

  void setAddress();
  void setSize();
  void addLineUsed();
  void setDimension();
  void setInitValue();
  void setParamList();
  void setFlags(uint32_t flags);

  uint32_t getBlock();
  uint32_t* getAddress();
  uint32_t getSize();
  uint32_t getLineDeclared();
  std::list<uint32_t> getLinesUsed();
  uint32_t getDimension();
  char* getInitValue();
  std::vector<Flags> getParamList();
  Flags getFlags(char*);
};