#include <unordered_map>
#include <stack>
#include <list>
#include <string>
#include <stdint.h>
#include <iostream>
#include <vector>

static constexpr uint32_t flag(int bit) {
  return 1 << bit;
}

enum class Types {
  INT,
  SHORT,
  LONG,
  FLOAT,
  DOUBLE,
  CHAR,
  VOID,
  STRUCT
};

enum class Flags {
  CONST = flag(1),
  STATIC = flag(2),  
  EXTERN = flag(3), 
  DEFINED = flag(4) 
};

struct MetaData {
  Flags flags;
  uint32_t block;
  uint32_t lineDeclared;
  std::vector<uint32_t> linesUsed;
};

struct ReturnType {
  Types type;
  uint32_t pointerDepth;
};

struct TypeDescriptor {
  Types type;
  uint32_t pointerDepth;
  std::vector<uint32_t> size;
};

class Variable {
  MetaData metaData;
  TypeDescriptor typeDescriptor;
  char* initValue = nullptr;
};

class FunctionDef {
  MetaData metaData;
  ReturnType returnType;
  std::vector<Variable> parameters;
};

class FunctionPtr {
  FunctionDef function;
  uint32_t pointerDepth;
};

class StructDef {
  MetaData metaData; 
  std::vector<Variable> parameters;
  uint32_t size;
};

class StructInstance {
  MetaData metadata;
  StructDef* defintion;
  uint32_t pointerDepth;
};

class SymbolTable {
private:

  // first stack --> function stack      second stack --> variable shadowing 
  // std::stack<std::unordered_map<std::string, std::stack<Symbol>>> table;
public:

  void addName(char* name, uint32_t block, uint32_t lineDeclared);
  void removeName(char* name);
  bool checkExists(char*);
  void functionCall();
  void functionEnd();
};