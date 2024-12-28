#include "symbol_table.h"

void SymbolTable::addName(
    char* name, uint32_t block, uint32_t lineDeclared, uint32_t* address) {
  SymbolTableInfo info;

  info.block = block;
  info.address = address;
  info.lineDeclared = lineDeclared;

  table[name].push(info);
}

void SymbolTable::removeName(char* name) {
  if (table.find(name) != table.end()) {
    table[name].pop();
  }
  else {
    throw std::runtime_error("name doesnt exist");
  }
}