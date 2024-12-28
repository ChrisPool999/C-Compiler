#include <unordered_map>
#include <stack>
#include <list>
#include <string>
#include <stdint.h>
#include <iostream>

class SymbolTable {
private:
  using Flags = uint32_t; 

  struct SymbolTableInfo {
    uint32_t block;
    uint32_t* address;
    uint32_t size;
    uint32_t lineDeclared;
    std::list<uint32_t> linesUsed;
    uint32_t dimension;
    uint32_t* closingScope;
    char* initValue;
    std::vector<Flags> paramList;
    Flags flags = 0b0000;
  };

  // mapped with a stack, to support variable shadowing 
  std::unordered_map<std::string, std::stack<SymbolTableInfo>> table; 
public:
  enum class TypeFlags {
    
  }

  enum class FlagOptions {
    CONST = 1,
    STATIC = 2,
    EXTERN = 4,
    INIT = 8,
    POINTER = 16,
    ARRAY = 32,
    STRUCT = 64,
    FUNCTION = 128,
    VARIABLE = 256,
    INT = 512,
    CHAR = 1024,
    FLOAT = 2048,
    DOUBLE = 4096,
    VOID = 8192,
    BEING_DEFINED = 16384
  };

  void addName(char* name, uint32_t block, uint32_t lineDeclared, uint32_t* address);
  void removeName(char* name);
  bool checkExists(char*);
  void setBlock();
  void setAddress();
  void setSize();
  void setLineDeclared();
  void setDataType();
  void setTypeSize();
  void setdimension();
  void setlinesUsed();
  Flags getFlags(char*);
  void setFlags(uint32_t flags);
};

// lexer (add name) = name, line declared

// parser - block, 