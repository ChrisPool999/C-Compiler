#ifndef SCANNER_H
#define SCANNER_H
#include <regex>
#include <iostream>
#include <map>
#include <fstream>

enum class Token_Type {
  KEYWORD,
  IDENTIFIER,
  REAL,
  INTEGER,
  SYMBOL,
  STRING,
  END_OF_FILE
};

class Token {
  public:
  const Token_Type type;
  const std::string value;
  Token(Token_Type t, std::string v);
};

class Scanner {
private:
  std::ifstream file;
  std::string input;
  int idx = 0;
  static const std::vector<Token_Type> all_token_types;
  static const std::unordered_map<Token_Type, std::regex> token_to_regex;
  static const std::unordered_map<Token_Type, std::string> token_as_str;
  std::unordered_map<std::string, int> symbol_table;
  bool is_white_space(char ch) const;
  bool is_symbol(char ch) const;
  bool is_symbol(char ch, char ch2) const;
  Token_Type get_token_type(std::string) const;
  void goto_token_start();
  void goto_token_end();
public:
  Scanner(std::string f);
  Token record_token(std::string val);
  Token read_token();
  void view_symbol_table() const;
};

#endif