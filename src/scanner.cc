#include "scanner.h"
#include <memory>

Token::Token(Token_Type t, std::string v) : type(t), value(v) {}

const std::vector<Token_Type> Scanner::all_token_types = {
  Token_Type::KEYWORD,
  Token_Type::IDENTIFIER,
  Token_Type::REAL,
  Token_Type::INTEGER,
  Token_Type::SYMBOL,
  Token_Type::STRING
};

const std::unordered_map<Token_Type, std::regex> Scanner::token_to_regex = {
  {Token_Type::KEYWORD, std::regex("^(if|else|while|for|continue|return|break|main|class|void|int|char|double|float)$")},
  {Token_Type::IDENTIFIER, std::regex("^([a-zA-Z_])([a-zA-Z\\d_])*$")},
  {Token_Type::REAL, std::regex("^([+-]?)(\\d+)?(\\.)(\\d*)$")},
  {Token_Type::INTEGER, std::regex("^([+-]?)(\\d+)$")},
  {Token_Type::SYMBOL, std::regex("(^[(){}[]<>+-*/!=%&|^~,;]$)")},
  {Token_Type::STRING, std::regex("^(\"[\s\S]\")$")}
};

  // {Token_Type::SYMBOL, std::regex("(^[\(\){}\[\]<>+\-*/!=%&|^~,;]|<=|>=|!=|==|\+\+|\+=|--|-=|\*=|/=|//|&&|<<|>>|\|\|$)")},

// used for debugging
const std::unordered_map<Token_Type, std::string> Scanner::token_as_str = {
  {Token_Type::KEYWORD, "KEYWORD"},
  {Token_Type::IDENTIFIER, "IDENTIFIER"},
  {Token_Type::REAL, "REAL"},
  {Token_Type::INTEGER, "INTEGER"},
  {Token_Type::SYMBOL, "SYMBOL"},
  {Token_Type::STRING, "STRING"}
};

Scanner::Scanner(std::string filename) {
  file.open(filename);
  if (file.good() == false) {
    throw std::ios_base::failure("File " + filename + " failed to open.");
  }
  std::getline(file, input);
}

Token Scanner::read_token() {
  goto_token_start();
  if (idx == -1) return {Token_Type::END_OF_FILE, ""};
  
  std::string::const_iterator start = input.begin() + idx;
  goto_token_end();
  std::string::const_iterator end = input.begin() + idx;
  
  std::string val = std::string(start, end);
  std::cout << val << std::endl;
  return {get_token_type(val), val};
}

// index where token begins
void Scanner::goto_token_start() {
  while (true) {
    while (idx < input.size() && is_white_space(input[idx])) {
      ++idx;
    }
    if (idx < input.size()) {
      return;
    }
    // no token found, read next line
    if (file.eof()) {
      idx = -1;
      return;
    }
    std::getline(file, input);
    idx = 0;
  }
}

// goes to index in input after token ends 
void Scanner::goto_token_end() {
  if (is_symbol(input[idx])) {
    bool compound_symbol = (idx + 1 < input.size()) && (is_symbol(input[idx], input[idx + 1]));
    idx += (compound_symbol ? 2 : 1);
    return;
  }
  while (idx < input.size() &&
      is_white_space(input[idx]) == false &&
      is_symbol(input[idx]) == false) {
    ++idx ;
  }
  std::cout << std::endl;
}

Token_Type Scanner::get_token_type(std::string s) const {
  static std::smatch match;
  for (auto t : all_token_types) {
    if (std::regex_search(s, match, token_to_regex.at(t))) {
      return t;
    }
  }
  throw std::runtime_error("illegal token ");
}

Token Scanner::record_token(std::string val) {
  if (symbol_table.count(val)) {
    ++symbol_table.at(val);
  } 
  else {
    symbol_table.insert({val, 1});
  }
  return {get_token_type(val), val};
}

bool Scanner::is_white_space(char ch) const {
  return ch == '\t' || ch == '\0' || ch == '\n' || ch == ' ';
}

bool Scanner::is_symbol(char ch) const {
  std::string s = std::to_string(ch);
  std::cout << ch << " ";
  std::cout << token_as_str.at(get_token_type(s)) << std::endl;
  return get_token_type(s) == Token_Type::SYMBOL;
}

bool Scanner::is_symbol(char ch, char ch2) const {
  std::string s = std::string(ch, ch2);
  return get_token_type(s) == Token_Type::SYMBOL;
}

void Scanner::view_symbol_table() const {
  for (auto &p : symbol_table) {
    std::cout << "Token name: " << p.first
        << " \nToken class: " << token_as_str.at(get_token_type(p.first))
        << " \nCount: " << p.second << "\n";
  }
  std::cout << "\n";
}

int main(int argc, char* argv[]) {
  if (argc != 2) {
    std::cerr << "Expects exactly 1 argument. \n";
    return 1;
  }

  Scanner sc = Scanner(argv[1]);
  while (true) {
    Token t = sc.read_token();
    if (t.type == Token_Type::END_OF_FILE) {
      sc.view_symbol_table();
      return 0;
    }
    sc.record_token(t.value);
  }
}

// add char

// make sure goto_start and goto_end work for new stuff added
// - string
// - comment
// - 2 width symbols

// include line number not just col position for seeing where syntax error is
// allow strings to run multiple lines

// symbol table needs:
//  - user defined symbols
//  - kind: reserved, typeID, varID, funcID, etc
//  - block number (scope)
//  - type: int, double, bull