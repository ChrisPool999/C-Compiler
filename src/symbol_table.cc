#include "symbol_table.h"

void SymbolTable::addName(
    char* name, uint32_t block, uint32_t lineDeclared) {
  SymbolInfo info;

  info.block = block;
  info.lineDeclared = lineDeclared;

  table.top()[name].push(info);
}

void SymbolTable::removeName(char* name) {
  if (table.find(name) != table.end()) {
    table[name].pop();
  }
  else {
    throw std::runtime_error("name doesnt exist");
  }
}