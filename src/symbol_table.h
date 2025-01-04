#include <unordered_map>
#include <stack>
#include <list>
#include <string>
#include <iostream>
#include <vector>
#include <variant>
#include <stdint.h>

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

struct ReturnType {
  Types type;
  uint32_t pointerDepth = 0;
};

struct TypeDescriptor {
  Types type;
  uint32_t pointerDepth = 0;
  std::vector<uint32_t> size;
};

class MetaData {
private:
  Flags flags;
  uint32_t block;
  std::pair<uint32_t, uint32_t> declLocation;
  std::vector<uint32_t> linesUsed;
public:
  Flags getFlags();
  uint32_t getBlock();
  uint32_t getLineDeclared();
  std::pair<uint32_t, uint32_t> getdeclLocation();
  std::vector<uint32_t> getLinesUsed();
};

// Symbol Types

class Variable {
private:
  MetaData metaData;
  TypeDescriptor typeDescriptor;
  char* initValue = nullptr;
public:
  MetaData getMetaData() const;
  TypeDescriptor getTypeDescriptor() const;
  char* getInitValue() const;
  void setTypeDescriptor(TypeDescriptor TD); 
  void setInitValue(char* value);
};

class FunctionDef {
private:
  MetaData metaData;
  ReturnType returnType;
  std::vector<Variable> parameters;
public:
  MetaData getMetaData() const;
  ReturnType getReturnType() const;
  std::vector<Variable> getParameters() const;
  void setReturnType(ReturnType RT);
  void setParameters(std::vector<Variable>& parameters);
};

class FunctionPtr {
private:
  uint32_t pointerDepth = 0;
  FunctionDef function;
public:
  FunctionDef getFunction() const;
  uint32_t getPointerDepth() const;
  void setPointerDepth(uint32_t PD);
};

class StructDef {
private:
  MetaData metaData; 
  std::vector<Variable> parameters;
public:
  MetaData getMetaData() const;
  std::vector<Variable> getParameters() const;
  void setParameters(std::vector<Variable>& parameters);
};

class StructInstance {
private:
  MetaData metadata;
  StructDef* defintion;
  uint32_t pointerDepth = 0;
public:
  MetaData getMetaData() const;
  StructDef* getDefinition() const;
  std::vector<Variable> getParameters() const;
  void setParameters(std::vector<Variable>& parameters);
};

using Symbol = std::variant<
    Variable, FunctionDef, FunctionPtr, StructDef, StructInstance>;

class SymbolTable {
private:
  static std::unordered_map<std::string, Symbol> globals;
  SymbolTable* prevScope = nullptr;

  // stack is to support variables of the same name
  std::unordered_map<std::string, std::stack<Symbol>> map;
  uint32_t block = 0;
public:
  void addEntry(char* name, uint32_t lineDeclared);
  void removeEntry(char* name);
  bool checkExists(char* name) const;
  void createNewScope();
  void closeScope();
  Symbol* getEntry(char*);
};