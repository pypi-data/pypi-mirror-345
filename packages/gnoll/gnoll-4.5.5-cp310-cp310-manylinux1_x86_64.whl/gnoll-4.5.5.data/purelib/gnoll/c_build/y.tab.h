/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

#ifndef YY_YY_Y_TAB_H_INCLUDED
# define YY_YY_Y_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token kinds.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    YYEMPTY = -2,
    YYEOF = 0,                     /* "end of file"  */
    YYerror = 256,                 /* error  */
    YYUNDEF = 257,                 /* "invalid token"  */
    NUMBER = 258,                  /* NUMBER  */
    SIDED_DIE = 259,               /* SIDED_DIE  */
    FATE_DIE = 260,                /* FATE_DIE  */
    REPEAT = 261,                  /* REPEAT  */
    SIDED_DIE_ZERO = 262,          /* SIDED_DIE_ZERO  */
    EXPLOSION = 263,               /* EXPLOSION  */
    IMPLOSION = 264,               /* IMPLOSION  */
    PENETRATE = 265,               /* PENETRATE  */
    ONCE = 266,                    /* ONCE  */
    MACRO_ACCESSOR = 267,          /* MACRO_ACCESSOR  */
    MACRO_STORAGE = 268,           /* MACRO_STORAGE  */
    SYMBOL_SEPERATOR = 269,        /* SYMBOL_SEPERATOR  */
    ASSIGNMENT = 270,              /* ASSIGNMENT  */
    KEEP_LOWEST = 271,             /* KEEP_LOWEST  */
    KEEP_HIGHEST = 272,            /* KEEP_HIGHEST  */
    DROP_LOWEST = 273,             /* DROP_LOWEST  */
    DROP_HIGHEST = 274,            /* DROP_HIGHEST  */
    FILTER = 275,                  /* FILTER  */
    LBRACE = 276,                  /* LBRACE  */
    RBRACE = 277,                  /* RBRACE  */
    PLUS = 278,                    /* PLUS  */
    MINUS = 279,                   /* MINUS  */
    MULT = 280,                    /* MULT  */
    MODULO = 281,                  /* MODULO  */
    DIVIDE_ROUND_UP = 282,         /* DIVIDE_ROUND_UP  */
    DIVIDE_ROUND_DOWN = 283,       /* DIVIDE_ROUND_DOWN  */
    REROLL = 284,                  /* REROLL  */
    SYMBOL_LBRACE = 285,           /* SYMBOL_LBRACE  */
    SYMBOL_RBRACE = 286,           /* SYMBOL_RBRACE  */
    STATEMENT_SEPERATOR = 287,     /* STATEMENT_SEPERATOR  */
    CAPITAL_STRING = 288,          /* CAPITAL_STRING  */
    DO_COUNT = 289,                /* DO_COUNT  */
    UNIQUE = 290,                  /* UNIQUE  */
    IS_EVEN = 291,                 /* IS_EVEN  */
    IS_ODD = 292,                  /* IS_ODD  */
    RANGE = 293,                   /* RANGE  */
    FN_MAX = 294,                  /* FN_MAX  */
    FN_MIN = 295,                  /* FN_MIN  */
    FN_ABS = 296,                  /* FN_ABS  */
    FN_POOL = 297,                 /* FN_POOL  */
    UMINUS = 298,                  /* UMINUS  */
    NE = 299,                      /* NE  */
    EQ = 300,                      /* EQ  */
    GT = 301,                      /* GT  */
    LT = 302,                      /* LT  */
    LE = 303,                      /* LE  */
    GE = 304                       /* GE  */
  };
  typedef enum yytokentype yytoken_kind_t;
#endif
/* Token kinds.  */
#define YYEMPTY -2
#define YYEOF 0
#define YYerror 256
#define YYUNDEF 257
#define NUMBER 258
#define SIDED_DIE 259
#define FATE_DIE 260
#define REPEAT 261
#define SIDED_DIE_ZERO 262
#define EXPLOSION 263
#define IMPLOSION 264
#define PENETRATE 265
#define ONCE 266
#define MACRO_ACCESSOR 267
#define MACRO_STORAGE 268
#define SYMBOL_SEPERATOR 269
#define ASSIGNMENT 270
#define KEEP_LOWEST 271
#define KEEP_HIGHEST 272
#define DROP_LOWEST 273
#define DROP_HIGHEST 274
#define FILTER 275
#define LBRACE 276
#define RBRACE 277
#define PLUS 278
#define MINUS 279
#define MULT 280
#define MODULO 281
#define DIVIDE_ROUND_UP 282
#define DIVIDE_ROUND_DOWN 283
#define REROLL 284
#define SYMBOL_LBRACE 285
#define SYMBOL_RBRACE 286
#define STATEMENT_SEPERATOR 287
#define CAPITAL_STRING 288
#define DO_COUNT 289
#define UNIQUE 290
#define IS_EVEN 291
#define IS_ODD 292
#define RANGE 293
#define FN_MAX 294
#define FN_MIN 295
#define FN_ABS 296
#define FN_POOL 297
#define UMINUS 298
#define NE 299
#define EQ 300
#define GT 301
#define LT 302
#define LE 303
#define GE 304

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
union YYSTYPE
{
#line 126 "src/grammar/dice.yacc"

    vec values;

#line 169 "y.tab.h"

};
typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;


int yyparse (void);


#endif /* !YY_YY_Y_TAB_H_INCLUDED  */
