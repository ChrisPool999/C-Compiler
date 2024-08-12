#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <set>

enum class token_types
{
  IDENTIFIERS,
  NUMBER,
  STRING,
  SYMBOL,
  END_OF_FILE
};

class Token 
{
private:
  const token_types type;
  const std::string value;

  Token(token_types t, std::string v) : type(t), value(v) {};

public:
  token_types get_type() const
  {
    return type;
  }
  std::string get_value() const
  {
    return value;
  }

  friend class Lexer;
};

class Lexer
{
private:
  std::set<std::string> identifiers = {
      "if", "else if", "else", "while", "for",
      "return", "break", "main", "void", "int", "char", "double", "float"};

  const std::set<std::string> symbols = {
        "<", "<=", ">", ">=", "!", "!=", "=", "==", "+", "++", "+=", "-",
        "--", "-=", "%", "*", "*=", "/", "//", "/=", "&", "&&", "|", "||",
        "^", "~", "<<", ">>", ",", ";", "'", "\"", "[", "]", "{", "}", 
        "(", ")"}; 
 
  std::string filename;
  std::ifstream file;
  int line = 0;
  int col = 0;
  std::string statement;

  bool is_valid_symbol(char ch_one, char ch_two = ' ') const
  { 
    return (ch_two == ' ') ? 
        symbols.count(std::string{ch_one}) : 
        symbols.count(std::string{ch_one, ch_two});
  }

  bool is_white_space(char ch) const
  {
    return ch == ' ' || ch == '\t' || ch == '\0' || ch == '\n';
  }

  char get_token_start()
  {
    while (true)
    {
      while (col < statement.size() && is_white_space(statement[col]))
      {
        col++;
      }
      if (file.eof())
      {
        return EOF;
      }
      else if (col >= statement.size() || 
              (col + 1 < statement.size() && 
              statement[col] == '/' && statement[col + 1] == '/'))
      {
        std::getline(file, statement);
        line++;
        col = 0;
      }
      else 
      {
        return statement[col];
      }
    }
  }

  std::string get_number()
  {
    std::string result = "";
    bool has_decimal = false;

    while (col < statement.size() && 
          (statement[col] == '.' || 
          (statement[col] >= '0' && statement[col] <= '9')))
    {
      if (statement[col] == '.')
      {
        if (has_decimal)
        {
          throw std::logic_error( // logically line & col are 0-indexed, but UI is 1-indexed
                "Number has multiple decimal points on line " 
                + std::to_string(line + 1) 
                + " col " 
                + std::to_string(col + 1) + "\n");
        }
        has_decimal = true;
      }
      result += statement[col];
      col++;
    }

    if (col < statement.size() && isalpha(statement[col]))
    {
      throw std::logic_error("Invalid character in number on line " + 
          std::to_string(line + 1) + " col " + std::to_string(col + 1) + 
          " --> " + statement[col]); 
    }
    return result;
  }

  std::string get_string()
  {
    std::string str = "";

    col++;
    while (statement[col] != '\"')
    {
      str += statement[col];
      col++;
      if (col >= statement.size())
      {
        throw std::logic_error("Missing ending quote on line " + 
            std::to_string(line + 1) + " col " + std::to_string(col + 1));
      }
    }

    col++;
    return str;
  }

  std::string get_identifier()
  {
    std::string ID = "";
    while (isalnum(statement[col]) || statement[col] == '_')
    {
      ID += statement[col];
      col++;
    }
    return ID;
  }

  std::string get_symbol()
  {
    if (col + 1 < statement.size() && 
        is_valid_symbol(statement[col], statement[col + 1]))
    {
      std::string result = std::string(std::string(statement, col, 2));
      col += 2;
      return result;
    }

    return std::string({statement[col++]});
  }

public:

  Lexer(std::string f) 
  {
    filename = f;

    file.open(filename);
    
    if (file.good() == false)
    {
      throw std::ios_base::failure("File " + filename + " failed to open.");
    }

    std::getline(file, statement);
  }

  Token read_token()
  {
    char ch = get_token_start();

    if (ch == EOF)
    {
      return {token_types::END_OF_FILE, ""};
    }
    if (ch >= '0' && ch <= '9')
    {
      return {token_types::NUMBER, get_number()};
    }
    if (ch == '\"')
    {
      return {token_types::STRING, get_string()};
    }
    if (isalpha(ch) || ch == '_')
    {
      return {token_types::IDENTIFIERS, get_identifier()};
    }
    if (is_valid_symbol(ch))
    {
      return {token_types::SYMBOL, get_symbol()};
    }
    else
    {
      throw std::logic_error("Unidentified character on line " + 
          std::to_string(line + 1) + " col " + std::to_string(col + 1) + 
          " . --> " + ch);
    }
  }
};

int main(int argc, char* argv[])
{
  if (argc != 2)
  {
    std::cerr << "Expects exactly 1 argument. \n";
    return 1;
  }

  Lexer lex = Lexer(argv[1]);

  while (true)
  {
    Token t = lex.read_token();
    if (t.get_type() == token_types::END_OF_FILE)
    {
      break;
    }
    std::cout << int(t.get_type()) << " - " << t.get_value() << std::endl;
  }

  return 0;
}