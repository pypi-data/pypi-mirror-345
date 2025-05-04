/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison implementation for Yacc-like parsers in C

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

/* C LALR(1) parser skeleton written by Richard Stallman, by
   simplifying the original so-called "semantic" parser.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output, and Bison version.  */
#define YYBISON 30802

/* Bison version string.  */
#define YYBISON_VERSION "3.8.2"

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Push parsers.  */
#define YYPUSH 0

/* Pull parsers.  */
#define YYPULL 1




/* First part of user prologue.  */
#line 4 "src/grammar/dice.yacc"


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <limits.h>
#include <assert.h>
#include <errno.h>
#include "shared_header.h"
#include "external/pcg-c/include/pcg_variants.h"    // TODO: Move this to randomness.c
#include "external/tinydir.h"
#include "operations/macros.h"
#include "operations/conditionals.h"
#include "rolls/dice_core.h"
#include "rolls/dice_frontend.h"
#include "util/mocking.h"
#include "util/safe_functions.h"
#include "util/array_functions.h"
#include "util/vector_functions.h"
#include "util/string_functions.h"
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#endif

#define UNUSED(x) (void)(x)
// Avoid conflicts with MacOs predefined macros
#define MAXV(x, y) (((x) > (y)) ? (x) : (y))
#define MINV(x, y) (((x) < (y)) ? (x) : (y))
#define ABSV(x) (((x) < 0) ? (-x) : (x))

#ifdef __EMSCRIPTEN__
#define VERBOSITY 1
#else
// UNDO
#define VERBOSITY 0
#endif

int yylex(void);
int yyerror(const char* s);
int yywrap(void);

//TODO: move to external file 

#ifdef JUST_YACC
int yydebug=1;
#endif

int verbose = 0;
int dice_breakdown = 0;
int seeded = 0;
int write_to_file = 0;
char * output_file;

extern int gnoll_errno;
extern struct macro_struct *macros;
pcg64_random_t rng;

// Function Signatures for this file
int initialize(void);
int countDigits(long long num);

// Functions
int initialize(void){
    if (!seeded){
        unsigned long int tick = (unsigned long)time(0)+(unsigned long)clock();
        pcg64_srandom_r(
            &rng,
            tick ^ (unsigned long int)&printf,
            54u
        );
        seeded = 1;
    }
    return 0;
}

int countDigits(long long num) {
    // count units in a number
    int count = 0;
    
    // Handle negative numbers
    if (num < 0) {
        num = -num;
    }
    
    // Count digits
    do {
        count++;
        num /= 10;
    } while (num > 0);
    
    return count;
}


#line 167 "y.tab.c"

# ifndef YY_CAST
#  ifdef __cplusplus
#   define YY_CAST(Type, Val) static_cast<Type> (Val)
#   define YY_REINTERPRET_CAST(Type, Val) reinterpret_cast<Type> (Val)
#  else
#   define YY_CAST(Type, Val) ((Type) (Val))
#   define YY_REINTERPRET_CAST(Type, Val) ((Type) (Val))
#  endif
# endif
# ifndef YY_NULLPTR
#  if defined __cplusplus
#   if 201103L <= __cplusplus
#    define YY_NULLPTR nullptr
#   else
#    define YY_NULLPTR 0
#   endif
#  else
#   define YY_NULLPTR ((void*)0)
#  endif
# endif

/* Use api.header.include to #include this header
   instead of duplicating it here.  */
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

#line 322 "y.tab.c"

};
typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;


int yyparse (void);


#endif /* !YY_YY_Y_TAB_H_INCLUDED  */
/* Symbol kind.  */
enum yysymbol_kind_t
{
  YYSYMBOL_YYEMPTY = -2,
  YYSYMBOL_YYEOF = 0,                      /* "end of file"  */
  YYSYMBOL_YYerror = 1,                    /* error  */
  YYSYMBOL_YYUNDEF = 2,                    /* "invalid token"  */
  YYSYMBOL_NUMBER = 3,                     /* NUMBER  */
  YYSYMBOL_SIDED_DIE = 4,                  /* SIDED_DIE  */
  YYSYMBOL_FATE_DIE = 5,                   /* FATE_DIE  */
  YYSYMBOL_REPEAT = 6,                     /* REPEAT  */
  YYSYMBOL_SIDED_DIE_ZERO = 7,             /* SIDED_DIE_ZERO  */
  YYSYMBOL_EXPLOSION = 8,                  /* EXPLOSION  */
  YYSYMBOL_IMPLOSION = 9,                  /* IMPLOSION  */
  YYSYMBOL_PENETRATE = 10,                 /* PENETRATE  */
  YYSYMBOL_ONCE = 11,                      /* ONCE  */
  YYSYMBOL_MACRO_ACCESSOR = 12,            /* MACRO_ACCESSOR  */
  YYSYMBOL_MACRO_STORAGE = 13,             /* MACRO_STORAGE  */
  YYSYMBOL_SYMBOL_SEPERATOR = 14,          /* SYMBOL_SEPERATOR  */
  YYSYMBOL_ASSIGNMENT = 15,                /* ASSIGNMENT  */
  YYSYMBOL_KEEP_LOWEST = 16,               /* KEEP_LOWEST  */
  YYSYMBOL_KEEP_HIGHEST = 17,              /* KEEP_HIGHEST  */
  YYSYMBOL_DROP_LOWEST = 18,               /* DROP_LOWEST  */
  YYSYMBOL_DROP_HIGHEST = 19,              /* DROP_HIGHEST  */
  YYSYMBOL_FILTER = 20,                    /* FILTER  */
  YYSYMBOL_LBRACE = 21,                    /* LBRACE  */
  YYSYMBOL_RBRACE = 22,                    /* RBRACE  */
  YYSYMBOL_PLUS = 23,                      /* PLUS  */
  YYSYMBOL_MINUS = 24,                     /* MINUS  */
  YYSYMBOL_MULT = 25,                      /* MULT  */
  YYSYMBOL_MODULO = 26,                    /* MODULO  */
  YYSYMBOL_DIVIDE_ROUND_UP = 27,           /* DIVIDE_ROUND_UP  */
  YYSYMBOL_DIVIDE_ROUND_DOWN = 28,         /* DIVIDE_ROUND_DOWN  */
  YYSYMBOL_REROLL = 29,                    /* REROLL  */
  YYSYMBOL_SYMBOL_LBRACE = 30,             /* SYMBOL_LBRACE  */
  YYSYMBOL_SYMBOL_RBRACE = 31,             /* SYMBOL_RBRACE  */
  YYSYMBOL_STATEMENT_SEPERATOR = 32,       /* STATEMENT_SEPERATOR  */
  YYSYMBOL_CAPITAL_STRING = 33,            /* CAPITAL_STRING  */
  YYSYMBOL_DO_COUNT = 34,                  /* DO_COUNT  */
  YYSYMBOL_UNIQUE = 35,                    /* UNIQUE  */
  YYSYMBOL_IS_EVEN = 36,                   /* IS_EVEN  */
  YYSYMBOL_IS_ODD = 37,                    /* IS_ODD  */
  YYSYMBOL_RANGE = 38,                     /* RANGE  */
  YYSYMBOL_FN_MAX = 39,                    /* FN_MAX  */
  YYSYMBOL_FN_MIN = 40,                    /* FN_MIN  */
  YYSYMBOL_FN_ABS = 41,                    /* FN_ABS  */
  YYSYMBOL_FN_POOL = 42,                   /* FN_POOL  */
  YYSYMBOL_UMINUS = 43,                    /* UMINUS  */
  YYSYMBOL_NE = 44,                        /* NE  */
  YYSYMBOL_EQ = 45,                        /* EQ  */
  YYSYMBOL_GT = 46,                        /* GT  */
  YYSYMBOL_LT = 47,                        /* LT  */
  YYSYMBOL_LE = 48,                        /* LE  */
  YYSYMBOL_GE = 49,                        /* GE  */
  YYSYMBOL_YYACCEPT = 50,                  /* $accept  */
  YYSYMBOL_gnoll_entry = 51,               /* gnoll_entry  */
  YYSYMBOL_gnoll_statement = 52,           /* gnoll_statement  */
  YYSYMBOL_sub_statement = 53,             /* sub_statement  */
  YYSYMBOL_macro_statement = 54,           /* macro_statement  */
  YYSYMBOL_dice_statement = 55,            /* dice_statement  */
  YYSYMBOL_math = 56,                      /* math  */
  YYSYMBOL_collapsing_dice_operations = 57, /* collapsing_dice_operations  */
  YYSYMBOL_dice_operations = 58,           /* dice_operations  */
  YYSYMBOL_die_roll = 59,                  /* die_roll  */
  YYSYMBOL_custom_symbol_dice = 60,        /* custom_symbol_dice  */
  YYSYMBOL_csd = 61,                       /* csd  */
  YYSYMBOL_singular_condition = 62,        /* singular_condition  */
  YYSYMBOL_condition = 63,                 /* condition  */
  YYSYMBOL_die_symbol = 64                 /* die_symbol  */
};
typedef enum yysymbol_kind_t yysymbol_kind_t;




#ifdef short
# undef short
#endif

/* On compilers that do not define __PTRDIFF_MAX__ etc., make sure
   <limits.h> and (if available) <stdint.h> are included
   so that the code can choose integer types of a good width.  */

#ifndef __PTRDIFF_MAX__
# include <limits.h> /* INFRINGES ON USER NAME SPACE */
# if defined __STDC_VERSION__ && 199901 <= __STDC_VERSION__
#  include <stdint.h> /* INFRINGES ON USER NAME SPACE */
#  define YY_STDINT_H
# endif
#endif

/* Narrow types that promote to a signed type and that can represent a
   signed or unsigned integer of at least N bits.  In tables they can
   save space and decrease cache pressure.  Promoting to a signed type
   helps avoid bugs in integer arithmetic.  */

#ifdef __INT_LEAST8_MAX__
typedef __INT_LEAST8_TYPE__ yytype_int8;
#elif defined YY_STDINT_H
typedef int_least8_t yytype_int8;
#else
typedef signed char yytype_int8;
#endif

#ifdef __INT_LEAST16_MAX__
typedef __INT_LEAST16_TYPE__ yytype_int16;
#elif defined YY_STDINT_H
typedef int_least16_t yytype_int16;
#else
typedef short yytype_int16;
#endif

/* Work around bug in HP-UX 11.23, which defines these macros
   incorrectly for preprocessor constants.  This workaround can likely
   be removed in 2023, as HPE has promised support for HP-UX 11.23
   (aka HP-UX 11i v2) only through the end of 2022; see Table 2 of
   <https://h20195.www2.hpe.com/V2/getpdf.aspx/4AA4-7673ENW.pdf>.  */
#ifdef __hpux
# undef UINT_LEAST8_MAX
# undef UINT_LEAST16_MAX
# define UINT_LEAST8_MAX 255
# define UINT_LEAST16_MAX 65535
#endif

#if defined __UINT_LEAST8_MAX__ && __UINT_LEAST8_MAX__ <= __INT_MAX__
typedef __UINT_LEAST8_TYPE__ yytype_uint8;
#elif (!defined __UINT_LEAST8_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST8_MAX <= INT_MAX)
typedef uint_least8_t yytype_uint8;
#elif !defined __UINT_LEAST8_MAX__ && UCHAR_MAX <= INT_MAX
typedef unsigned char yytype_uint8;
#else
typedef short yytype_uint8;
#endif

#if defined __UINT_LEAST16_MAX__ && __UINT_LEAST16_MAX__ <= __INT_MAX__
typedef __UINT_LEAST16_TYPE__ yytype_uint16;
#elif (!defined __UINT_LEAST16_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST16_MAX <= INT_MAX)
typedef uint_least16_t yytype_uint16;
#elif !defined __UINT_LEAST16_MAX__ && USHRT_MAX <= INT_MAX
typedef unsigned short yytype_uint16;
#else
typedef int yytype_uint16;
#endif

#ifndef YYPTRDIFF_T
# if defined __PTRDIFF_TYPE__ && defined __PTRDIFF_MAX__
#  define YYPTRDIFF_T __PTRDIFF_TYPE__
#  define YYPTRDIFF_MAXIMUM __PTRDIFF_MAX__
# elif defined PTRDIFF_MAX
#  ifndef ptrdiff_t
#   include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  endif
#  define YYPTRDIFF_T ptrdiff_t
#  define YYPTRDIFF_MAXIMUM PTRDIFF_MAX
# else
#  define YYPTRDIFF_T long
#  define YYPTRDIFF_MAXIMUM LONG_MAX
# endif
#endif

#ifndef YYSIZE_T
# ifdef __SIZE_TYPE__
#  define YYSIZE_T __SIZE_TYPE__
# elif defined size_t
#  define YYSIZE_T size_t
# elif defined __STDC_VERSION__ && 199901 <= __STDC_VERSION__
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# else
#  define YYSIZE_T unsigned
# endif
#endif

#define YYSIZE_MAXIMUM                                  \
  YY_CAST (YYPTRDIFF_T,                                 \
           (YYPTRDIFF_MAXIMUM < YY_CAST (YYSIZE_T, -1)  \
            ? YYPTRDIFF_MAXIMUM                         \
            : YY_CAST (YYSIZE_T, -1)))

#define YYSIZEOF(X) YY_CAST (YYPTRDIFF_T, sizeof (X))


/* Stored state numbers (used for stacks). */
typedef yytype_int8 yy_state_t;

/* State numbers in computations.  */
typedef int yy_state_fast_t;

#ifndef YY_
# if defined YYENABLE_NLS && YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(Msgid) dgettext ("bison-runtime", Msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(Msgid) Msgid
# endif
#endif


#ifndef YY_ATTRIBUTE_PURE
# if defined __GNUC__ && 2 < __GNUC__ + (96 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_PURE __attribute__ ((__pure__))
# else
#  define YY_ATTRIBUTE_PURE
# endif
#endif

#ifndef YY_ATTRIBUTE_UNUSED
# if defined __GNUC__ && 2 < __GNUC__ + (7 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_UNUSED __attribute__ ((__unused__))
# else
#  define YY_ATTRIBUTE_UNUSED
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YY_USE(E) ((void) (E))
#else
# define YY_USE(E) /* empty */
#endif

/* Suppress an incorrect diagnostic about yylval being uninitialized.  */
#if defined __GNUC__ && ! defined __ICC && 406 <= __GNUC__ * 100 + __GNUC_MINOR__
# if __GNUC__ * 100 + __GNUC_MINOR__ < 407
#  define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN                           \
    _Pragma ("GCC diagnostic push")                                     \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")
# else
#  define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN                           \
    _Pragma ("GCC diagnostic push")                                     \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")              \
    _Pragma ("GCC diagnostic ignored \"-Wmaybe-uninitialized\"")
# endif
# define YY_IGNORE_MAYBE_UNINITIALIZED_END      \
    _Pragma ("GCC diagnostic pop")
#else
# define YY_INITIAL_VALUE(Value) Value
#endif
#ifndef YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_END
#endif
#ifndef YY_INITIAL_VALUE
# define YY_INITIAL_VALUE(Value) /* Nothing. */
#endif

#if defined __cplusplus && defined __GNUC__ && ! defined __ICC && 6 <= __GNUC__
# define YY_IGNORE_USELESS_CAST_BEGIN                          \
    _Pragma ("GCC diagnostic push")                            \
    _Pragma ("GCC diagnostic ignored \"-Wuseless-cast\"")
# define YY_IGNORE_USELESS_CAST_END            \
    _Pragma ("GCC diagnostic pop")
#endif
#ifndef YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_END
#endif


#define YY_ASSERT(E) ((void) (0 && (E)))

#if !defined yyoverflow

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# ifdef YYSTACK_USE_ALLOCA
#  if YYSTACK_USE_ALLOCA
#   ifdef __GNUC__
#    define YYSTACK_ALLOC __builtin_alloca
#   elif defined __BUILTIN_VA_ARG_INCR
#    include <alloca.h> /* INFRINGES ON USER NAME SPACE */
#   elif defined _AIX
#    define YYSTACK_ALLOC __alloca
#   elif defined _MSC_VER
#    include <malloc.h> /* INFRINGES ON USER NAME SPACE */
#    define alloca _alloca
#   else
#    define YYSTACK_ALLOC alloca
#    if ! defined _ALLOCA_H && ! defined EXIT_SUCCESS
#     include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
      /* Use EXIT_SUCCESS as a witness for stdlib.h.  */
#     ifndef EXIT_SUCCESS
#      define EXIT_SUCCESS 0
#     endif
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's 'empty if-body' warning.  */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (0)
#  ifndef YYSTACK_ALLOC_MAXIMUM
    /* The OS might guarantee only one guard page at the bottom of the stack,
       and a page size can be as small as 4096 bytes.  So we cannot safely
       invoke alloca (N) if N exceeds 4096.  Use a slightly smaller number
       to allow for a few compiler-allocated temporary stack slots.  */
#   define YYSTACK_ALLOC_MAXIMUM 4032 /* reasonable circa 2006 */
#  endif
# else
#  define YYSTACK_ALLOC YYMALLOC
#  define YYSTACK_FREE YYFREE
#  ifndef YYSTACK_ALLOC_MAXIMUM
#   define YYSTACK_ALLOC_MAXIMUM YYSIZE_MAXIMUM
#  endif
#  if (defined __cplusplus && ! defined EXIT_SUCCESS \
       && ! ((defined YYMALLOC || defined malloc) \
             && (defined YYFREE || defined free)))
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   ifndef EXIT_SUCCESS
#    define EXIT_SUCCESS 0
#   endif
#  endif
#  ifndef YYMALLOC
#   define YYMALLOC malloc
#   if ! defined malloc && ! defined EXIT_SUCCESS
void *malloc (YYSIZE_T); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
#  ifndef YYFREE
#   define YYFREE free
#   if ! defined free && ! defined EXIT_SUCCESS
void free (void *); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
# endif
#endif /* !defined yyoverflow */

#if (! defined yyoverflow \
     && (! defined __cplusplus \
         || (defined YYSTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  yy_state_t yyss_alloc;
  YYSTYPE yyvs_alloc;
};

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (YYSIZEOF (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (YYSIZEOF (yy_state_t) + YYSIZEOF (YYSTYPE)) \
      + YYSTACK_GAP_MAXIMUM)

# define YYCOPY_NEEDED 1

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack_alloc, Stack)                           \
    do                                                                  \
      {                                                                 \
        YYPTRDIFF_T yynewbytes;                                         \
        YYCOPY (&yyptr->Stack_alloc, Stack, yysize);                    \
        Stack = &yyptr->Stack_alloc;                                    \
        yynewbytes = yystacksize * YYSIZEOF (*Stack) + YYSTACK_GAP_MAXIMUM; \
        yyptr += yynewbytes / YYSIZEOF (*yyptr);                        \
      }                                                                 \
    while (0)

#endif

#if defined YYCOPY_NEEDED && YYCOPY_NEEDED
/* Copy COUNT objects from SRC to DST.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if defined __GNUC__ && 1 < __GNUC__
#   define YYCOPY(Dst, Src, Count) \
      __builtin_memcpy (Dst, Src, YY_CAST (YYSIZE_T, (Count)) * sizeof (*(Src)))
#  else
#   define YYCOPY(Dst, Src, Count)              \
      do                                        \
        {                                       \
          YYPTRDIFF_T yyi;                      \
          for (yyi = 0; yyi < (Count); yyi++)   \
            (Dst)[yyi] = (Src)[yyi];            \
        }                                       \
      while (0)
#  endif
# endif
#endif /* !YYCOPY_NEEDED */

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  33
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   177

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  50
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  15
/* YYNRULES -- Number of rules.  */
#define YYNRULES  72
/* YYNSTATES -- Number of states.  */
#define YYNSTATES  114

/* YYMAXUTOK -- Last valid token kind.  */
#define YYMAXUTOK   304


/* YYTRANSLATE(TOKEN-NUM) -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex, with out-of-bounds checking.  */
#define YYTRANSLATE(YYX)                                \
  (0 <= (YYX) && (YYX) <= YYMAXUTOK                     \
   ? YY_CAST (yysymbol_kind_t, yytranslate[YYX])        \
   : YYSYMBOL_YYUNDEF)

/* YYTRANSLATE[TOKEN-NUM] -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex.  */
static const yytype_int8 yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21,    22,    23,    24,
      25,    26,    27,    28,    29,    30,    31,    32,    33,    34,
      35,    36,    37,    38,    39,    40,    41,    42,    43,    44,
      45,    46,    47,    48,    49
};

#if YYDEBUG
/* YYRLINE[YYN] -- Source line where rule number YYN was defined.  */
static const yytype_int16 yyrline[] =
{
       0,   136,   136,   142,   148,   150,   152,   161,   163,   168,
     196,   266,   291,   312,   329,   333,   372,   413,   456,   495,
     564,   607,   646,   650,   667,   696,   757,   808,   840,   867,
     889,   912,   936,   959,   981,   998,  1014,  1033,  1052,  1056,
    1088,  1119,  1147,  1177,  1204,  1233,  1258,  1288,  1313,  1337,
    1364,  1393,  1413,  1435,  1437,  1442,  1473,  1548,  1623,  1646,
    1686,  1688,  1707,  1707,  1707,  1708,  1708,  1708,  1708,  1708,
    1708,  1711,  1722
};
#endif

/** Accessing symbol of state STATE.  */
#define YY_ACCESSING_SYMBOL(State) YY_CAST (yysymbol_kind_t, yystos[State])

#if YYDEBUG || 0
/* The user-facing name of the symbol whose (internal) number is
   YYSYMBOL.  No bounds checking.  */
static const char *yysymbol_name (yysymbol_kind_t yysymbol) YY_ATTRIBUTE_UNUSED;

/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const yytname[] =
{
  "\"end of file\"", "error", "\"invalid token\"", "NUMBER", "SIDED_DIE",
  "FATE_DIE", "REPEAT", "SIDED_DIE_ZERO", "EXPLOSION", "IMPLOSION",
  "PENETRATE", "ONCE", "MACRO_ACCESSOR", "MACRO_STORAGE",
  "SYMBOL_SEPERATOR", "ASSIGNMENT", "KEEP_LOWEST", "KEEP_HIGHEST",
  "DROP_LOWEST", "DROP_HIGHEST", "FILTER", "LBRACE", "RBRACE", "PLUS",
  "MINUS", "MULT", "MODULO", "DIVIDE_ROUND_UP", "DIVIDE_ROUND_DOWN",
  "REROLL", "SYMBOL_LBRACE", "SYMBOL_RBRACE", "STATEMENT_SEPERATOR",
  "CAPITAL_STRING", "DO_COUNT", "UNIQUE", "IS_EVEN", "IS_ODD", "RANGE",
  "FN_MAX", "FN_MIN", "FN_ABS", "FN_POOL", "UMINUS", "NE", "EQ", "GT",
  "LT", "LE", "GE", "$accept", "gnoll_entry", "gnoll_statement",
  "sub_statement", "macro_statement", "dice_statement", "math",
  "collapsing_dice_operations", "dice_operations", "die_roll",
  "custom_symbol_dice", "csd", "singular_condition", "condition",
  "die_symbol", YY_NULLPTR
};

static const char *
yysymbol_name (yysymbol_kind_t yysymbol)
{
  return yytname[yysymbol];
}
#endif

#define YYPACT_NINF (-53)

#define yypact_value_is_default(Yyn) \
  ((Yyn) == YYPACT_NINF)

#define YYTABLE_NINF (-5)

#define yytable_value_is_error(Yyn) \
  0

/* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
   STATE-NUM.  */
static const yytype_int16 yypact[] =
{
      35,   -53,    85,   -53,   -53,   -53,   -29,   -18,    57,    57,
      12,    14,    34,    67,    26,   -53,   -53,   -53,    90,   -53,
      92,    48,   -53,    54,   -53,    65,   -53,    64,   -16,   -53,
      57,    57,    57,   -53,    13,    57,    57,    57,    57,    57,
      57,    79,    80,    91,    97,    84,   -53,   -53,    58,    93,
     -53,    18,   -53,   114,   -53,    18,   -53,    57,   -53,   111,
     126,   119,   -53,    45,    45,   -53,   -53,   -53,   -53,   -53,
     -53,   -53,   -53,   -53,   -53,   -53,   -53,   -53,   -53,   -53,
     -53,   -53,   -53,   120,   125,   121,    33,   110,   -53,   -12,
      55,    32,    90,    57,    57,   -53,   -53,   172,   -53,   -53,
     -53,   173,    18,   -53,   -53,   -53,   -53,   133,   140,   -53,
     -53,   -53,   -53,   -53
};

/* YYDEFACT[STATE-NUM] -- Default reduction number in state STATE-NUM.
   Performed when YYTABLE does not specify something else to do.  Zero
   means the default is an error.  */
static const yytype_int8 yydefact[] =
{
       0,     6,    54,    71,    52,    72,     0,     0,     0,     0,
       0,     0,     0,     0,     2,     5,     7,     8,    10,    22,
      24,    38,    53,     0,    51,     0,    57,     0,     0,    21,
       0,     0,     0,     1,     0,     0,     0,     0,     0,     0,
       0,    36,    34,    37,    35,     0,    23,    29,     0,    46,
      48,     0,    50,    45,    47,     0,    49,     0,    14,     0,
       0,     0,     3,    19,    20,    15,    18,    16,    17,    32,
      30,    33,    31,    62,    64,    63,    70,    65,    67,    66,
      68,    69,    28,     0,     0,     0,    44,    61,    60,     0,
      43,     0,     9,     0,     0,    13,    27,     0,    26,    42,
      40,     0,     0,    56,    41,    39,    55,     0,     0,    25,
      59,    58,    11,    12
};

/* YYPGOTO[NTERM-NUM].  */
static const yytype_int16 yypgoto[] =
{
     -53,   -53,    59,   -53,   -53,   -53,    -8,   -53,   -53,   -53,
     -53,   -52,   -53,   -43,   175
};

/* YYDEFGOTO[NTERM-NUM].  */
static const yytype_int8 yydefgoto[] =
{
       0,    13,    14,    15,    16,    17,    18,    19,    20,    21,
      22,    89,    82,    83,    23
};

/* YYTABLE[YYPACT[STATE-NUM]] -- What to do in state STATE-NUM.  If
   positive, shift that token.  If negative, reduce the rule whose
   number is the opposite.  If YYTABLE_NINF, syntax error.  */
static const yytype_int8 yytable[] =
{
      28,    29,   102,    91,    26,    85,    58,    35,    36,    37,
      38,    39,    40,    -4,     1,    27,     2,     3,     4,   103,
       5,    87,    59,    60,    61,     6,     7,    63,    64,    65,
      66,    67,    68,    30,     8,    31,     1,     9,     2,     3,
       4,    97,     5,    99,   100,    -4,   102,     6,     7,    92,
     111,    88,    10,    11,    12,    32,     8,    49,    34,     9,
       2,     3,     4,   106,     5,   104,   105,    33,    53,     6,
      37,    38,    39,    40,    10,    11,    12,    48,     8,    57,
      50,     9,    69,    70,    51,   107,   108,    84,    52,     3,
      24,    54,     5,    62,    71,    55,    10,    11,    12,    56,
      72,    86,    76,    77,    78,    79,    80,    81,    41,    42,
      43,    44,    45,    35,    36,    37,    38,    39,    40,    73,
      74,    75,    90,    96,    98,    93,    46,    47,    76,    77,
      78,    79,    80,    81,    35,    36,    37,    38,    39,    40,
      94,    95,    35,    36,    37,    38,    39,    40,   101,    35,
      36,    37,    38,    39,    40,   112,    35,    36,    37,    38,
      39,    40,   113,    35,    36,    37,    38,    39,    40,    76,
      77,    78,    79,    80,    81,   109,   110,    25
};

static const yytype_int8 yycheck[] =
{
       8,     9,    14,    55,    33,    48,    22,    23,    24,    25,
      26,    27,    28,     0,     1,    33,     3,     4,     5,    31,
       7,     3,    30,    31,    32,    12,    13,    35,    36,    37,
      38,    39,    40,    21,    21,    21,     1,    24,     3,     4,
       5,    84,     7,    10,    11,    32,    14,    12,    13,    57,
     102,    33,    39,    40,    41,    21,    21,     3,    32,    24,
       3,     4,     5,    31,     7,    10,    11,     0,     3,    12,
      25,    26,    27,    28,    39,    40,    41,    29,    21,    15,
      26,    24,     3,     3,    30,    93,    94,    29,    34,     4,
       5,    26,     7,    34,     3,    30,    39,    40,    41,    34,
       3,     8,    44,    45,    46,    47,    48,    49,    16,    17,
      18,    19,    20,    23,    24,    25,    26,    27,    28,    35,
      36,    37,     8,     3,     3,    14,    34,    35,    44,    45,
      46,    47,    48,    49,    23,    24,    25,    26,    27,    28,
      14,    22,    23,    24,    25,    26,    27,    28,    38,    23,
      24,    25,    26,    27,    28,    22,    23,    24,    25,    26,
      27,    28,    22,    23,    24,    25,    26,    27,    28,    44,
      45,    46,    47,    48,    49,     3,     3,     2
};

/* YYSTOS[STATE-NUM] -- The symbol kind of the accessing symbol of
   state STATE-NUM.  */
static const yytype_int8 yystos[] =
{
       0,     1,     3,     4,     5,     7,    12,    13,    21,    24,
      39,    40,    41,    51,    52,    53,    54,    55,    56,    57,
      58,    59,    60,    64,     5,    64,    33,    33,    56,    56,
      21,    21,    21,     0,    32,    23,    24,    25,    26,    27,
      28,    16,    17,    18,    19,    20,    34,    35,    29,     3,
      26,    30,    34,     3,    26,    30,    34,    15,    22,    56,
      56,    56,    52,    56,    56,    56,    56,    56,    56,     3,
       3,     3,     3,    35,    36,    37,    44,    45,    46,    47,
      48,    49,    62,    63,    29,    63,     8,     3,    33,    61,
       8,    61,    56,    14,    14,    22,     3,    63,     3,    10,
      11,    38,    14,    31,    10,    11,    31,    56,    56,     3,
       3,    61,    22,    22
};

/* YYR1[RULE-NUM] -- Symbol kind of the left-hand side of rule RULE-NUM.  */
static const yytype_int8 yyr1[] =
{
       0,    50,    51,    52,    52,    52,    52,    53,    53,    54,
      55,    56,    56,    56,    56,    56,    56,    56,    56,    56,
      56,    56,    56,    57,    57,    58,    58,    58,    58,    58,
      58,    58,    58,    58,    58,    58,    58,    58,    58,    59,
      59,    59,    59,    59,    59,    59,    59,    59,    59,    59,
      59,    59,    59,    59,    59,    60,    60,    60,    61,    61,
      61,    61,    62,    62,    62,    63,    63,    63,    63,    63,
      63,    64,    64
};

/* YYR2[RULE-NUM] -- Number of symbols on the right-hand side of rule RULE-NUM.  */
static const yytype_int8 yyr2[] =
{
       0,     2,     1,     3,     2,     1,     1,     1,     1,     4,
       1,     6,     6,     4,     3,     3,     3,     3,     3,     3,
       3,     2,     1,     2,     1,     5,     4,     4,     3,     2,
       3,     3,     3,     3,     2,     2,     2,     2,     1,     5,
       4,     5,     4,     4,     3,     3,     2,     3,     2,     3,
       2,     2,     1,     1,     1,     5,     4,     2,     3,     3,
       1,     1,     1,     1,     1,     1,     1,     1,     1,     1,
       1,     1,     1
};


enum { YYENOMEM = -2 };

#define yyerrok         (yyerrstatus = 0)
#define yyclearin       (yychar = YYEMPTY)

#define YYACCEPT        goto yyacceptlab
#define YYABORT         goto yyabortlab
#define YYERROR         goto yyerrorlab
#define YYNOMEM         goto yyexhaustedlab


#define YYRECOVERING()  (!!yyerrstatus)

#define YYBACKUP(Token, Value)                                    \
  do                                                              \
    if (yychar == YYEMPTY)                                        \
      {                                                           \
        yychar = (Token);                                         \
        yylval = (Value);                                         \
        YYPOPSTACK (yylen);                                       \
        yystate = *yyssp;                                         \
        goto yybackup;                                            \
      }                                                           \
    else                                                          \
      {                                                           \
        yyerror (YY_("syntax error: cannot back up")); \
        YYERROR;                                                  \
      }                                                           \
  while (0)

/* Backward compatibility with an undocumented macro.
   Use YYerror or YYUNDEF. */
#define YYERRCODE YYUNDEF


/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)                        \
do {                                            \
  if (yydebug)                                  \
    YYFPRINTF Args;                             \
} while (0)




# define YY_SYMBOL_PRINT(Title, Kind, Value, Location)                    \
do {                                                                      \
  if (yydebug)                                                            \
    {                                                                     \
      YYFPRINTF (stderr, "%s ", Title);                                   \
      yy_symbol_print (stderr,                                            \
                  Kind, Value); \
      YYFPRINTF (stderr, "\n");                                           \
    }                                                                     \
} while (0)


/*-----------------------------------.
| Print this symbol's value on YYO.  |
`-----------------------------------*/

static void
yy_symbol_value_print (FILE *yyo,
                       yysymbol_kind_t yykind, YYSTYPE const * const yyvaluep)
{
  FILE *yyoutput = yyo;
  YY_USE (yyoutput);
  if (!yyvaluep)
    return;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YY_USE (yykind);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}


/*---------------------------.
| Print this symbol on YYO.  |
`---------------------------*/

static void
yy_symbol_print (FILE *yyo,
                 yysymbol_kind_t yykind, YYSTYPE const * const yyvaluep)
{
  YYFPRINTF (yyo, "%s %s (",
             yykind < YYNTOKENS ? "token" : "nterm", yysymbol_name (yykind));

  yy_symbol_value_print (yyo, yykind, yyvaluep);
  YYFPRINTF (yyo, ")");
}

/*------------------------------------------------------------------.
| yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (included).                                                   |
`------------------------------------------------------------------*/

static void
yy_stack_print (yy_state_t *yybottom, yy_state_t *yytop)
{
  YYFPRINTF (stderr, "Stack now");
  for (; yybottom <= yytop; yybottom++)
    {
      int yybot = *yybottom;
      YYFPRINTF (stderr, " %d", yybot);
    }
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)                            \
do {                                                            \
  if (yydebug)                                                  \
    yy_stack_print ((Bottom), (Top));                           \
} while (0)


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

static void
yy_reduce_print (yy_state_t *yyssp, YYSTYPE *yyvsp,
                 int yyrule)
{
  int yylno = yyrline[yyrule];
  int yynrhs = yyr2[yyrule];
  int yyi;
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %d):\n",
             yyrule - 1, yylno);
  /* The symbols being reduced.  */
  for (yyi = 0; yyi < yynrhs; yyi++)
    {
      YYFPRINTF (stderr, "   $%d = ", yyi + 1);
      yy_symbol_print (stderr,
                       YY_ACCESSING_SYMBOL (+yyssp[yyi + 1 - yynrhs]),
                       &yyvsp[(yyi + 1) - (yynrhs)]);
      YYFPRINTF (stderr, "\n");
    }
}

# define YY_REDUCE_PRINT(Rule)          \
do {                                    \
  if (yydebug)                          \
    yy_reduce_print (yyssp, yyvsp, Rule); \
} while (0)

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args) ((void) 0)
# define YY_SYMBOL_PRINT(Title, Kind, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !YYDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   YYSTACK_ALLOC_MAXIMUM < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif






/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

static void
yydestruct (const char *yymsg,
            yysymbol_kind_t yykind, YYSTYPE *yyvaluep)
{
  YY_USE (yyvaluep);
  if (!yymsg)
    yymsg = "Deleting";
  YY_SYMBOL_PRINT (yymsg, yykind, yyvaluep, yylocationp);

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YY_USE (yykind);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}


/* Lookahead token kind.  */
int yychar;

/* The semantic value of the lookahead symbol.  */
YYSTYPE yylval;
/* Number of syntax errors so far.  */
int yynerrs;




/*----------.
| yyparse.  |
`----------*/

int
yyparse (void)
{
    yy_state_fast_t yystate = 0;
    /* Number of tokens to shift before error messages enabled.  */
    int yyerrstatus = 0;

    /* Refer to the stacks through separate pointers, to allow yyoverflow
       to reallocate them elsewhere.  */

    /* Their size.  */
    YYPTRDIFF_T yystacksize = YYINITDEPTH;

    /* The state stack: array, bottom, top.  */
    yy_state_t yyssa[YYINITDEPTH];
    yy_state_t *yyss = yyssa;
    yy_state_t *yyssp = yyss;

    /* The semantic value stack: array, bottom, top.  */
    YYSTYPE yyvsa[YYINITDEPTH];
    YYSTYPE *yyvs = yyvsa;
    YYSTYPE *yyvsp = yyvs;

  int yyn;
  /* The return value of yyparse.  */
  int yyresult;
  /* Lookahead symbol kind.  */
  yysymbol_kind_t yytoken = YYSYMBOL_YYEMPTY;
  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;



#define YYPOPSTACK(N)   (yyvsp -= (N), yyssp -= (N))

  /* The number of symbols on the RHS of the reduced rule.
     Keep to zero when no symbol should be popped.  */
  int yylen = 0;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yychar = YYEMPTY; /* Cause a token to be read.  */

  goto yysetstate;


/*------------------------------------------------------------.
| yynewstate -- push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed.  So pushing a state here evens the stacks.  */
  yyssp++;


/*--------------------------------------------------------------------.
| yysetstate -- set current state (the top of the stack) to yystate.  |
`--------------------------------------------------------------------*/
yysetstate:
  YYDPRINTF ((stderr, "Entering state %d\n", yystate));
  YY_ASSERT (0 <= yystate && yystate < YYNSTATES);
  YY_IGNORE_USELESS_CAST_BEGIN
  *yyssp = YY_CAST (yy_state_t, yystate);
  YY_IGNORE_USELESS_CAST_END
  YY_STACK_PRINT (yyss, yyssp);

  if (yyss + yystacksize - 1 <= yyssp)
#if !defined yyoverflow && !defined YYSTACK_RELOCATE
    YYNOMEM;
#else
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYPTRDIFF_T yysize = yyssp - yyss + 1;

# if defined yyoverflow
      {
        /* Give user a chance to reallocate the stack.  Use copies of
           these so that the &'s don't force the real ones into
           memory.  */
        yy_state_t *yyss1 = yyss;
        YYSTYPE *yyvs1 = yyvs;

        /* Each stack pointer address is followed by the size of the
           data in use in that stack, in bytes.  This used to be a
           conditional around just the two extra args, but that might
           be undefined if yyoverflow is a macro.  */
        yyoverflow (YY_("memory exhausted"),
                    &yyss1, yysize * YYSIZEOF (*yyssp),
                    &yyvs1, yysize * YYSIZEOF (*yyvsp),
                    &yystacksize);
        yyss = yyss1;
        yyvs = yyvs1;
      }
# else /* defined YYSTACK_RELOCATE */
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= yystacksize)
        YYNOMEM;
      yystacksize *= 2;
      if (YYMAXDEPTH < yystacksize)
        yystacksize = YYMAXDEPTH;

      {
        yy_state_t *yyss1 = yyss;
        union yyalloc *yyptr =
          YY_CAST (union yyalloc *,
                   YYSTACK_ALLOC (YY_CAST (YYSIZE_T, YYSTACK_BYTES (yystacksize))));
        if (! yyptr)
          YYNOMEM;
        YYSTACK_RELOCATE (yyss_alloc, yyss);
        YYSTACK_RELOCATE (yyvs_alloc, yyvs);
#  undef YYSTACK_RELOCATE
        if (yyss1 != yyssa)
          YYSTACK_FREE (yyss1);
      }
# endif

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;

      YY_IGNORE_USELESS_CAST_BEGIN
      YYDPRINTF ((stderr, "Stack size increased to %ld\n",
                  YY_CAST (long, yystacksize)));
      YY_IGNORE_USELESS_CAST_END

      if (yyss + yystacksize - 1 <= yyssp)
        YYABORT;
    }
#endif /* !defined yyoverflow && !defined YYSTACK_RELOCATE */


  if (yystate == YYFINAL)
    YYACCEPT;

  goto yybackup;


/*-----------.
| yybackup.  |
`-----------*/
yybackup:
  /* Do appropriate processing given the current state.  Read a
     lookahead token if we need one and don't already have one.  */

  /* First try to decide what to do without reference to lookahead token.  */
  yyn = yypact[yystate];
  if (yypact_value_is_default (yyn))
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* YYCHAR is either empty, or end-of-input, or a valid lookahead.  */
  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token\n"));
      yychar = yylex ();
    }

  if (yychar <= YYEOF)
    {
      yychar = YYEOF;
      yytoken = YYSYMBOL_YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else if (yychar == YYerror)
    {
      /* The scanner already issued an error message, process directly
         to error recovery.  But do not keep the error token as
         lookahead, it is too special and may lead us to an endless
         loop in error recovery. */
      yychar = YYUNDEF;
      yytoken = YYSYMBOL_YYerror;
      goto yyerrlab1;
    }
  else
    {
      yytoken = YYTRANSLATE (yychar);
      YY_SYMBOL_PRINT ("Next token is", yytoken, &yylval, &yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  yyn += yytoken;
  if (yyn < 0 || YYLAST < yyn || yycheck[yyn] != yytoken)
    goto yydefault;
  yyn = yytable[yyn];
  if (yyn <= 0)
    {
      if (yytable_value_is_error (yyn))
        goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  /* Shift the lookahead token.  */
  YY_SYMBOL_PRINT ("Shifting", yytoken, &yylval, &yylloc);
  yystate = yyn;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END

  /* Discard the shifted token.  */
  yychar = YYEMPTY;
  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     '$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];


  YY_REDUCE_PRINT (yyn);
  switch (yyn)
    {
  case 2: /* gnoll_entry: gnoll_statement  */
#line 136 "src/grammar/dice.yacc"
                   {
        free_vector((yyvsp[0].values));
    }
#line 1460 "y.tab.c"
    break;

  case 3: /* gnoll_statement: gnoll_statement STATEMENT_SEPERATOR gnoll_statement  */
#line 142 "src/grammar/dice.yacc"
                                                       {
        free_vector((yyvsp[0].values));
        // vec1 freed at root.
    }
#line 1469 "y.tab.c"
    break;

  case 6: /* gnoll_statement: error  */
#line 152 "src/grammar/dice.yacc"
          {
        printf("Invalid Notation\n");
        gnoll_errno = SYNTAX_ERROR;
        YYABORT;
        yyclearin;
    }
#line 1480 "y.tab.c"
    break;

  case 9: /* macro_statement: MACRO_STORAGE CAPITAL_STRING ASSIGNMENT math  */
#line 168 "src/grammar/dice.yacc"
                                                {
        /**
        * MACRO_STORAGE - the symbol '#''
        * CAPITAL_STRING - vector 
        * ASSIGNMENT - the symbol '='
        * math - vector dice roll assignment
        * returns - nothing.
        */
                
        vec key = (yyvsp[-2].values);
        vec value = (yyvsp[0].values);

        register_macro(&key, &value.source);

        // Cleanup
        free_vector(key);
        free_vector(value);
        
        if(gnoll_errno){
            YYABORT;
            yyclearin;
        }
        vec null_vec;
        light_initialize_vector(&null_vec, NUMERIC, 0);
        (yyval.values) = null_vec;
    }
#line 1511 "y.tab.c"
    break;

  case 10: /* dice_statement: math  */
#line 196 "src/grammar/dice.yacc"
                    {
    /**
    * functions a vector
    * return NULL
    */

    vec vector = (yyvsp[0].values);
    vec new_vec;

    //  Step 1: Collapse pool to a single value if nessicary
    collapse_vector(&vector, &new_vec);
    if(gnoll_errno){
        YYABORT;
        yyclearin;
    }

    // Step 2: Output to file
    FILE *fp = NULL;

    if(write_to_file){
        fp = safe_fopen(output_file, "a+");
        if(gnoll_errno){
            YYABORT;
            yyclearin;
        }
    }

    // TODO: To Function
#ifdef __EMSCRIPTEN__
    printf("Result:");
#endif
    for(unsigned long long i = 0; i!= new_vec.length;i++){
        if (new_vec.dtype == SYMBOLIC){
            // TODO: Strings >1 character
            if (verbose || VERBOSITY ){
                printf("%s;", new_vec.storage.symbols[i]);
            }
            if(write_to_file){
                fprintf(fp, "%s;", new_vec.storage.symbols[i]);
            }
        }else{
            if(verbose || VERBOSITY ){

                printf("%lld;", new_vec.storage.content[i]);
            }
            if(write_to_file){
                fprintf(fp, "%lld;", new_vec.storage.content[i]);

            }
        }
    }
    if(verbose || VERBOSITY){
       printf("\n");
    }
    
    if (dice_breakdown){
        fprintf(fp, "\n");
    }

    if(write_to_file){
        fclose(fp);
    }

    free_vector(vector);
    
    (yyval.values) = new_vec;
}
#line 1583 "y.tab.c"
    break;

  case 11: /* math: FN_MAX LBRACE math SYMBOL_SEPERATOR math RBRACE  */
#line 266 "src/grammar/dice.yacc"
                                                   {
        /** @brief performs the min(__, __) function
        * @FN_MAX the symbol "max"
        * @LBRACE the symbol "("
        * function The target vector
        * SYMBOL_SEPERATOR the symbol ","
        * function The target vector
        * @RBRACE the symbol ")"
        * return vector
        */
        vec new_vec;
        initialize_vector(&new_vec, NUMERIC, 1);

        long long vmax = MAXV(

            (yyvsp[-3].values).storage.content[0],
            (yyvsp[-1].values).storage.content[0]

        );
        new_vec.storage.content[0] = vmax;
        (yyval.values) = new_vec;
        free_vector((yyvsp[-3].values));
        free_vector((yyvsp[-1].values));
    }
#line 1612 "y.tab.c"
    break;

  case 12: /* math: FN_MIN LBRACE math SYMBOL_SEPERATOR math RBRACE  */
#line 291 "src/grammar/dice.yacc"
                                                   {
        /** @brief performs the min(__, __) function
        * @FN_MIN the symbol "min"
        * @LBRACE the symbol "("
        * function The target vector
        * SYMBOL_SEPERATOR the symbol ","
        * function The target vector
        * @RBRACE the symbol ")"
        * return vector
        */
        vec new_vec;
        initialize_vector(&new_vec, NUMERIC, 1);
        new_vec.storage.content[0] = MINV(
            (yyvsp[-3].values).storage.content[0],
            (yyvsp[-1].values).storage.content[0]
        );
        (yyval.values) = new_vec;
        free_vector((yyvsp[-3].values));
        free_vector((yyvsp[-1].values));
    }
#line 1637 "y.tab.c"
    break;

  case 13: /* math: FN_ABS LBRACE math RBRACE  */
#line 312 "src/grammar/dice.yacc"
                             {
        /** @brief performs the abs(__) function
        * @FN_ABS the symbol "abs"
        * @LBRACE the symbol "("
        * function The target vector
        * @RBRACE the symbol ")"
        * return vector
        */
        vec new_vec;
        initialize_vector(&new_vec, NUMERIC, 1);
        new_vec.storage.content[0] = ABSV(
            (yyvsp[-1].values).storage.content[0]
        );
        (yyval.values) = new_vec;
        free_vector((yyvsp[-1].values));
    }
#line 1658 "y.tab.c"
    break;

  case 14: /* math: LBRACE math RBRACE  */
#line 329 "src/grammar/dice.yacc"
                      {
        (yyval.values) = (yyvsp[-1].values);
    }
#line 1666 "y.tab.c"
    break;

  case 15: /* math: math MULT math  */
#line 333 "src/grammar/dice.yacc"
                  {
        /** @brief Collapse both sides and multiply
        * Math vector
        * MULT symbol '*'
        * Math vector
        */
        vec vector1 = (yyvsp[-2].values);
        vec vector2 = (yyvsp[0].values);

        if (vector1.dtype == SYMBOLIC || vector2.dtype == SYMBOLIC){
            printf("Multiplication not implemented for symbolic dice.\n");
            gnoll_errno = NOT_IMPLEMENTED;
            YYABORT;
            yyclearin;
        }else{

            long long v1 = collapse(vector1.storage.content, vector1.length);
            long long v2 = collapse(vector2.storage.content, vector2.length);

            vec new_vec;
            new_vec.storage.content = (long long*)safe_calloc(sizeof(long long), 1);
            new_vec.length = 1;
            if (v1 != 0 && v2 > INT_MAX / v1){
               gnoll_errno = MATH_OVERFLOW;
            }
            if (v1 != 0 && v2 < INT_MIN / v1){
               gnoll_errno = MATH_UNDERFLOW;
            }
            new_vec.storage.content[0] = v1 * v2;

            new_vec.dtype = vector1.dtype;

            (yyval.values) = new_vec;
        }
        
        free_vector(vector1);
        free_vector(vector2);
    }
#line 1709 "y.tab.c"
    break;

  case 16: /* math: math DIVIDE_ROUND_UP math  */
#line 372 "src/grammar/dice.yacc"
                             {
        /** @brief Collapse both sides and divide
        * Math vector
        * Divide symbol '/'
        * Math vector
        */
        // Collapse both sides and subtract
        vec vector1 = (yyvsp[-2].values);
        vec vector2 = (yyvsp[0].values);

        if (vector1.dtype == SYMBOLIC || vector2.dtype == SYMBOLIC){
            printf("Division unsupported for symbolic dice.\n");
            gnoll_errno = UNDEFINED_BEHAVIOUR;
            YYABORT;
            yyclearin;

        }else{

            long long v1 = collapse(vector1.storage.content, vector1.length);
            long long v2 = collapse(vector2.storage.content, vector2.length);

            vec new_vec;
            new_vec.storage.content = (long long*)safe_calloc(sizeof(long long), 1);

            if(gnoll_errno){ YYABORT; yyclearin;}
            new_vec.length = 1;
            if(v2==0){
                gnoll_errno=DIVIDE_BY_ZERO;
                new_vec.storage.content[0] = 0;
            }else{
                new_vec.storage.content[0] = (v1+(v2-1))/ v2;
            }
            new_vec.dtype = vector1.dtype;

            (yyval.values) = new_vec;
        }
        
        free_vector(vector1);
        free_vector(vector2);
    }
#line 1754 "y.tab.c"
    break;

  case 17: /* math: math DIVIDE_ROUND_DOWN math  */
#line 413 "src/grammar/dice.yacc"
                               {
        /** @brief Collapse both sides and divide
        * Math vector
        * Divide symbol '\'
        * Math vector
        */
        // Collapse both sides and subtract
        vec vector1 = (yyvsp[-2].values);
        vec vector2 = (yyvsp[0].values);

        if (vector1.dtype == SYMBOLIC || vector2.dtype == SYMBOLIC){
            printf("Division unsupported for symbolic dice.\n");
            gnoll_errno = UNDEFINED_BEHAVIOUR;
            YYABORT;
            yyclearin;
        }else{

            long long v1 = collapse(vector1.storage.content, vector1.length);
            long long v2 = collapse(vector2.storage.content, vector2.length);

            vec new_vec;
            new_vec.storage.content = (long long*)safe_calloc(sizeof(long long), 1);

            if(gnoll_errno){
               YYABORT;
               yyclearin;
            }
            new_vec.length = 1;
            if(v2==0){
                gnoll_errno=DIVIDE_BY_ZERO;
                new_vec.storage.content[0] = 0;
            }else{
                new_vec.storage.content[0] = v1 / v2;
            }
            new_vec.dtype = vector1.dtype;

            (yyval.values) = new_vec;
        }
        
        free_vector(vector1);
        free_vector(vector2);
    }
#line 1801 "y.tab.c"
    break;

  case 18: /* math: math MODULO math  */
#line 456 "src/grammar/dice.yacc"
                    {
        /** @brief Collapse both sides and modulo
        * Math vector
        * MULT symbol '%'
        * Math vector
        */
        // Collapse both sides and subtract
        vec vector1 = (yyvsp[-2].values);
        vec vector2 = (yyvsp[0].values);

        if (vector1.dtype == SYMBOLIC || vector2.dtype == SYMBOLIC){
            printf("Modulo unsupported for symbolic dice.\n");
            gnoll_errno = UNDEFINED_BEHAVIOUR;
            YYABORT;
            yyclearin;

        }else{

            long long v1 = collapse(vector1.storage.content, vector1.length);
            long long v2 = collapse(vector2.storage.content, vector2.length);

            vec new_vec;
            new_vec.storage.content = (long long*)safe_calloc(sizeof(long long), 1);

            if(gnoll_errno){
                YYABORT;
                yyclearin;
            }
            new_vec.length = 1;
            new_vec.storage.content[0] = v1 % v2;
            new_vec.dtype = vector1.dtype;

            (yyval.values) = new_vec;
        }
        
        free_vector(vector1);
        free_vector(vector2);
    }
#line 1844 "y.tab.c"
    break;

  case 19: /* math: math PLUS math  */
#line 495 "src/grammar/dice.yacc"
                  {
        /** @brief
        * math vector
        * PLUS symbol "+"
        * math vector
        */
        // Collapse both sides and subtract
        vec vector1 = (yyvsp[-2].values);
        vec vector2 = (yyvsp[0].values);

        if (
            (vector1.dtype == SYMBOLIC && vector2.dtype == NUMERIC) ||
            (vector2.dtype == SYMBOLIC && vector1.dtype == NUMERIC)
        ){
            printf("Addition not supported with mixed dice types.\n");
            gnoll_errno = UNDEFINED_BEHAVIOUR;
            YYABORT;
            yyclearin;
        } else if (vector1.dtype == SYMBOLIC){
            vec new_vec;

            unsigned long long concat_length = vector1.length + vector2.length;
            new_vec.storage.symbols = safe_calloc(sizeof(char *), concat_length);

            if(gnoll_errno){
                YYABORT;
                yyclearin;
            }

            for (unsigned long long i = 0; i != concat_length; i++){
                new_vec.storage.symbols[i] = safe_calloc(sizeof(char), MAX_SYMBOL_LENGTH);

                if(gnoll_errno){
                    YYABORT;
                    yyclearin;
                }
            }
            new_vec.length = concat_length;
            new_vec.dtype = vector1.dtype;

            concat_symbols(
                vector1.storage.symbols, vector1.length,
                vector2.storage.symbols, vector2.length,
                new_vec.storage.symbols
            );
            (yyval.values) = new_vec;
        }else{

            long long v1 = collapse(vector1.storage.content, vector1.length);
            long long v2 = collapse(vector2.storage.content, vector2.length);

            vec new_vec;
            new_vec.storage.content = (long long*)safe_calloc(sizeof(long long), 1);

            if(gnoll_errno){
                YYABORT;
                yyclearin;
            }
            new_vec.length = 1;
            new_vec.dtype = vector1.dtype;
            new_vec.storage.content[0] = v1 + v2;

            (yyval.values) = new_vec;
        }
        free_vector(vector1);
        free_vector(vector2);

    }
#line 1917 "y.tab.c"
    break;

  case 20: /* math: math MINUS math  */
#line 564 "src/grammar/dice.yacc"
                   {
        /** @brief Collapse both sides and subtract
        * Math vector
        * MINUS symbol '-'
        * Math vector
        */
        vec vector1 = (yyvsp[-2].values);
        vec vector2 = (yyvsp[0].values);
        if (
            (vector1.dtype == SYMBOLIC || vector2.dtype == SYMBOLIC)
        ){
            // It's not clear whether {+,-} - {-, 0} should be {+} or {+, 0}!
            // Therfore, we'll exclude it.
            printf("Subtract not supported with symbolic dice.\n");
            gnoll_errno = UNDEFINED_BEHAVIOUR;
            YYABORT;
            yyclearin;;
        }else{
            // Collapse both sides and subtract


            long long v1 = collapse(vector1.storage.content, vector1.length);
            long long v2 = collapse(vector2.storage.content, vector2.length);

            vec new_vec;
            new_vec.storage.content = (long long*)safe_calloc(sizeof(long long), 1);


            if(gnoll_errno){
                YYABORT;
                yyclearin;
            }
            new_vec.length = 1;
            new_vec.storage.content[0] = v1 - v2;
            new_vec.dtype = vector1.dtype;

            (yyval.values) = new_vec;
        }
        free_vector(vector1);
        free_vector(vector2);

    }
#line 1964 "y.tab.c"
    break;

  case 21: /* math: MINUS math  */
#line 607 "src/grammar/dice.yacc"
                           {
        /**
        * MINUS a symbol '-'
        * math a vector
        */
        // Eltwise Negation
        vec vector = (yyvsp[0].values);

        if (vector.dtype == SYMBOLIC){
            printf("Symbolic Dice, Cannot negate. Consider using Numeric dice or post-processing.\n");
            gnoll_errno = UNDEFINED_BEHAVIOUR;
            YYABORT;
            yyclearin;;
        } else {
            vec new_vec;


            new_vec.storage.content = (long long*)safe_calloc(sizeof(long long), vector.length);

            if(gnoll_errno){
                YYABORT;
                yyclearin;
            }
            new_vec.length = vector.length;
            new_vec.dtype = vector.dtype;


            for(unsigned long long i = 0; i != vector.length; i++){
                new_vec.storage.content[i] = - vector.storage.content[i];


          
            }
            (yyval.values) = new_vec;

        }
        free_vector(vector);
    }
#line 2007 "y.tab.c"
    break;

  case 23: /* collapsing_dice_operations: dice_operations DO_COUNT  */
#line 650 "src/grammar/dice.yacc"
                            {
        /**
        * dice_operations - a vector
        * DO_COUNT - a symbol 'c'
        */

        vec new_vec;
        vec dice = (yyvsp[-1].values);
        initialize_vector(&new_vec, NUMERIC, 1);


        new_vec.storage.content[0] = (long long)dice.length;

        free_vector(dice);
        (yyval.values) = new_vec;
    }
#line 2028 "y.tab.c"
    break;

  case 24: /* collapsing_dice_operations: dice_operations  */
#line 667 "src/grammar/dice.yacc"
                   {
        /** 
        * dice_operations a vector
        * returns a vector
        */

        vec vector = (yyvsp[0].values);

        if (vector.dtype == SYMBOLIC){
            // Symbolic, Impossible to collapse
            (yyval.values) = vector;
        }
        else{
            // Collapse if Necessary
            if(vector.length > 1){
                vec new_vector;
                initialize_vector(&new_vector, NUMERIC, 1);
                new_vector.storage.content[0] = sum(vector.storage.content, vector.length);
                (yyval.values) = new_vector;
                free_vector(vector);
            }else{
                (yyval.values) = vector;
            }
        }
    }
#line 2058 "y.tab.c"
    break;

  case 25: /* dice_operations: die_roll REROLL REROLL condition NUMBER  */
#line 696 "src/grammar/dice.yacc"
                                           {
        /** 
        * dice_roll a vector
        * REROLL symbol 'r'
        * REROLL symbol 'r'
        * condition vector
        * Number vector
        * returns a vector
        */

        vec dice = (yyvsp[-4].values);
        vec cv = (yyvsp[-1].values);
        vec cvno = (yyvsp[0].values);


        int check = (int)cv.storage.content[0];


        if(dice.dtype == NUMERIC){
            int count = 0;
            while (! check_condition(&dice, &cvno, (COMPARATOR)check)){
                if (count > MAX_ITERATION){
                    printf("MAX ITERATION LIMIT EXCEEDED: REROLL\n");
                    gnoll_errno = MAX_LOOP_LIMIT_HIT;
                    YYABORT; 
                    yyclearin;
                    break;
                }
                vec number_of_dice;
                initialize_vector(&number_of_dice, NUMERIC, 1);

                number_of_dice.storage.content[0] = (long long)dice.source.number_of_dice;

                vec die_sides;
                initialize_vector(&die_sides, NUMERIC, 1);
                die_sides.storage.content[0] = (long long)dice.source.die_sides;


                roll_plain_sided_dice(
                    &number_of_dice,
                    &die_sides,
                    &dice,
                    dice.source.explode,
                    1
                );
                count ++;
                free_vector(die_sides);
                free_vector(number_of_dice);
            }
            (yyval.values) = dice;

        }else{
            printf("No support for Symbolic die rerolling yet!\n");
            gnoll_errno = NOT_IMPLEMENTED;
            YYABORT;
            yyclearin;
        }
        free_vector(cv);
        free_vector(cvno);
    }
#line 2123 "y.tab.c"
    break;

  case 26: /* dice_operations: die_roll REROLL condition NUMBER  */
#line 757 "src/grammar/dice.yacc"
                                    {
        /*
        * die_roll vector
        * Reroll symbol
        * condition vector
        * Number vector
        */

        vec dice = (yyvsp[-3].values);
        vec comp = (yyvsp[-1].values);

        int check = (int)comp.storage.content[0];

        vec numv = (yyvsp[0].values);

        if(dice.dtype == NUMERIC){
            if (check_condition(&dice, &numv, (COMPARATOR)check)){

                vec number_of_dice;
                initialize_vector(&number_of_dice, NUMERIC, 1);

                number_of_dice.storage.content[0] = (long long)dice.source.number_of_dice;

                vec die_sides;
                initialize_vector(&die_sides, NUMERIC, 1);
                die_sides.storage.content[0] = (long long)dice.source.die_sides;


                roll_plain_sided_dice(
                    &number_of_dice,
                    &die_sides,
                    &(yyval.values),
                    dice.source.explode,
                    1
                );
                free_vector(dice);
                free_vector(number_of_dice);
            }else{
                // No need to reroll
                (yyval.values) = dice;
            }
        }else{
            printf("No support for Symbolic die rerolling yet!");
            gnoll_errno = NOT_IMPLEMENTED;
            YYABORT;
            yyclearin;;
        }
        free_vector(numv);
        free_vector(comp);
    }
#line 2178 "y.tab.c"
    break;

  case 27: /* dice_operations: dice_operations FILTER condition NUMBER  */
#line 808 "src/grammar/dice.yacc"
                                           {
        /*
        * dice_operations vector
        * Filter symbol 'f'
        * condition vector
        * Number vector
        */
        vec new_vec;
        vec dice = (yyvsp[-3].values);
        vec condition = (yyvsp[0].values);
        vec cv = (yyvsp[-1].values);


        int check = (int)cv.storage.content[0];


        if(dice.dtype == NUMERIC){
            initialize_vector(&new_vec, NUMERIC, dice.length);
            filter(&dice, &condition, check, &new_vec);

            (yyval.values) = new_vec;
        }else{
            printf("No support for Symbolic die rerolling yet!\n");
            gnoll_errno = NOT_IMPLEMENTED;
            YYABORT;
            yyclearin;
        }
        free_vector(dice);
        free_vector(condition);
        free_vector(cv);
    }
#line 2214 "y.tab.c"
    break;

  case 28: /* dice_operations: dice_operations FILTER singular_condition  */
#line 840 "src/grammar/dice.yacc"
                                             {
        /**
        * dice_operations vector
        * FILTER symbol 'f'
        * singular_condition symbol
        */
        vec dice = (yyvsp[-2].values);

        int check = (int)(yyvsp[0].values).storage.content[0];


        vec new_vec;

        if(dice.dtype == NUMERIC){
            initialize_vector(&new_vec, NUMERIC, dice.length);
            filter(&dice, NULL, check, &new_vec);

            (yyval.values) = new_vec;
        }else{
            printf("No support for Symbolic die rerolling yet!\n");
            gnoll_errno = NOT_IMPLEMENTED;
            YYABORT;
            yyclearin;;
        }
        free_vector(dice);
    }
#line 2245 "y.tab.c"
    break;

  case 29: /* dice_operations: dice_operations UNIQUE  */
#line 867 "src/grammar/dice.yacc"
                          {
        /**
        * dice_operations vector
        * UNIQUE symbol 'u'
        */
        vec new_vec;
        vec dice = (yyvsp[-1].values);

        if(dice.dtype == NUMERIC){
            initialize_vector(&new_vec, NUMERIC, dice.length);
            filter_unique(&dice, &new_vec);

            (yyval.values) = new_vec;
        }else{
            printf("No support for Symbolic die rerolling yet!\n");
            gnoll_errno = NOT_IMPLEMENTED;
            YYABORT;
            yyclearin;;
        }
        free_vector(dice);
    }
#line 2271 "y.tab.c"
    break;

  case 30: /* dice_operations: dice_operations KEEP_HIGHEST NUMBER  */
#line 889 "src/grammar/dice.yacc"
                                       {
        /**
        * dice_operations vector
        * KEEP_HIGHEST symbol 'kh'
        * NUMBER vector
        */
        vec roll_vec = (yyvsp[-2].values);
        vec keep_vector = (yyvsp[0].values);

        vec **new_vec;

        unsigned long long num_to_hold = (unsigned long long)keep_vector.storage.content[0];

        
        initialize_vector_pointer(&new_vec, roll_vec.dtype, num_to_hold);

        keep_highest_values(&roll_vec, new_vec, num_to_hold);

        (yyval.values) = **new_vec;
        free_vector(keep_vector);
   
    }
#line 2298 "y.tab.c"
    break;

  case 31: /* dice_operations: dice_operations DROP_HIGHEST NUMBER  */
#line 912 "src/grammar/dice.yacc"
                                       {
        /**
        * dice_operations vector
        * DROP_HIGHEST symbol 'dh'
        * NUMBER vector
        */
        vec roll_vec = (yyvsp[-2].values);
        vec keep_vector = (yyvsp[0].values);


        unsigned long long num_to_hold = (unsigned long long)keep_vector.storage.content[0];


        vec **new_vec;
        initialize_vector_pointer(&new_vec, roll_vec.dtype, roll_vec.length - num_to_hold);

        drop_highest_values(&roll_vec, new_vec, num_to_hold);

        (yyval.values) = **new_vec;
        // free_vector(roll_vec);
        free_vector(keep_vector);

    }
#line 2326 "y.tab.c"
    break;

  case 32: /* dice_operations: dice_operations KEEP_LOWEST NUMBER  */
#line 936 "src/grammar/dice.yacc"
                                      {
        /**
        * dice_operations vector
        * KEEP_LOWEST symbol 'kl'
        * NUMBER vector
        */

        vec roll_vec = (yyvsp[-2].values);
        vec keep_vector = (yyvsp[0].values);

        vec **new_vec;

        unsigned long long num_to_hold = (unsigned long long)keep_vector.storage.content[0];        

        initialize_vector_pointer(&new_vec, roll_vec.dtype, num_to_hold);

        keep_lowest_values(&roll_vec, new_vec, num_to_hold);

        (yyval.values) = **new_vec;
        // free_vector(roll_vec);
        free_vector(keep_vector);
    }
#line 2353 "y.tab.c"
    break;

  case 33: /* dice_operations: dice_operations DROP_LOWEST NUMBER  */
#line 959 "src/grammar/dice.yacc"
                                      {
        /**
        * dice_operations vector
        * DROP_LOWEST symbol 'dl'
        * NUMBER vector
        */
        vec roll_vec = (yyvsp[-2].values);
        vec keep_vector = (yyvsp[0].values);

        unsigned long long num_to_hold = (unsigned long long)keep_vector.storage.content[0];

        vec **new_vec;

        
        initialize_vector_pointer(&new_vec, roll_vec.dtype, roll_vec.length - num_to_hold);
        drop_lowest_values(&roll_vec, new_vec, num_to_hold);

        (yyval.values) = **new_vec;
        // free_vector(roll_vec);
        free_vector(keep_vector);
    }
#line 2379 "y.tab.c"
    break;

  case 34: /* dice_operations: dice_operations KEEP_HIGHEST  */
#line 981 "src/grammar/dice.yacc"
                                {
        /**
        * dice_operations vector
        * KEEP_HIGHEST symbol 'kh'
        */

        vec roll_vec = (yyvsp[-1].values);
        unsigned long long num_to_hold = 1;

        vec **new_vec;        
        initialize_vector_pointer(&new_vec, roll_vec.dtype, num_to_hold);
        keep_highest_values(&roll_vec, new_vec, num_to_hold);

        (yyval.values) = **new_vec;
        // free_vector(roll_vec);
    }
#line 2400 "y.tab.c"
    break;

  case 35: /* dice_operations: dice_operations DROP_HIGHEST  */
#line 998 "src/grammar/dice.yacc"
                                {
        /**
        * dice_operations vector
        * DROP_HIGHEST symbol 'dh'
        */
        vec roll_vec = (yyvsp[-1].values);

        unsigned long long num_to_hold = 1;
        vec **new_vec;        
        initialize_vector_pointer(&new_vec, roll_vec.dtype, roll_vec.length - num_to_hold);
        drop_highest_values(&roll_vec, new_vec, num_to_hold);

        (yyval.values) = **new_vec;
        // free_vector(roll_vec);
    }
#line 2420 "y.tab.c"
    break;

  case 36: /* dice_operations: dice_operations KEEP_LOWEST  */
#line 1014 "src/grammar/dice.yacc"
                               {
        /**
        * dice_operations vector
        * KEEP_LOWEST symbol 'kl'
        */
        vec roll_vec = (yyvsp[-1].values);

        unsigned long long num_to_hold = 1;

        vec **new_vec;
        initialize_vector_pointer(&new_vec, roll_vec.dtype, num_to_hold);


        keep_lowest_values(&roll_vec, new_vec, num_to_hold);

        (yyval.values) = **new_vec;
        // free_vector(roll_vec);
    }
#line 2443 "y.tab.c"
    break;

  case 37: /* dice_operations: dice_operations DROP_LOWEST  */
#line 1033 "src/grammar/dice.yacc"
                               {
        /**
        * dice_operations vector
        * DROP_LOWEST symbol 'dl'
        */
        vec roll_vec = (yyvsp[-1].values);

        unsigned long long num_to_hold = 1;

        vec **new_vec;        
        initialize_vector_pointer(&new_vec, roll_vec.dtype, roll_vec.length - num_to_hold);


        drop_lowest_values(&roll_vec, new_vec, num_to_hold);

        (yyval.values) = **new_vec;
        // free_vector(roll_vec);
    }
#line 2466 "y.tab.c"
    break;

  case 39: /* die_roll: NUMBER die_symbol NUMBER EXPLOSION ONCE  */
#line 1056 "src/grammar/dice.yacc"
                                           {
        /**
        * NUMBER vector
        * die_symbol vector 
        * NUMBER vector
        * EXPLOSION symbol 'e' or similar
        * ONCE symbol 'o'
        */
        vec numA = (yyvsp[-4].values);
        vec ds = (yyvsp[-3].values);
        vec numB = (yyvsp[-2].values);


        long long start_from = ds.storage.content[0];


        vec number_of_dice;
        initialize_vector(&number_of_dice, NUMERIC, 1);
        number_of_dice.storage.content[0] = 1;

        roll_plain_sided_dice(
            &numA,
            &numB,
            &(yyval.values),
            ONLY_ONCE_EXPLOSION,
            start_from
        );
        free_vector(numA);
        free_vector(ds);
        free_vector(numB);
    }
#line 2502 "y.tab.c"
    break;

  case 40: /* die_roll: die_symbol NUMBER EXPLOSION ONCE  */
#line 1088 "src/grammar/dice.yacc"
                                    {
        /**
        * die_symbol vector 
        * NUMBER vector
        * EXPLOSION symbol 'e' or similar
        * ONCE symbol 'o'
        */
        
        vec ds = (yyvsp[-3].values);
        vec numB = (yyvsp[-2].values);


        long long start_from = ds.storage.content[0];


        vec number_of_dice;
        initialize_vector(&number_of_dice, NUMERIC, 1);
        number_of_dice.storage.content[0] = 1;

        roll_plain_sided_dice(
            &number_of_dice,
            &numB,
            &(yyval.values),
            ONLY_ONCE_EXPLOSION,
            start_from
        );
        free_vector(number_of_dice);
        free_vector(ds);
        free_vector(numB);
    }
#line 2537 "y.tab.c"
    break;

  case 41: /* die_roll: NUMBER die_symbol NUMBER EXPLOSION PENETRATE  */
#line 1119 "src/grammar/dice.yacc"
                                                {
        /**
        * NUMBER vector
        * die_symbol vector 
        * NUMBER vector
        * EXPLOSION symbol 'e' or similar
        * PENETRATE symbol 'p'
        */
        vec numA = (yyvsp[-4].values);
        vec ds = (yyvsp[-3].values);
        vec numB = (yyvsp[-2].values);

        long long start_from = ds.storage.content[0];


        roll_plain_sided_dice(
            &numA,
            &numB,
            &(yyval.values),
            PENETRATING_EXPLOSION,
            start_from
        );
        
        free_vector(numA);
        free_vector(ds);
        free_vector(numB);
    }
#line 2569 "y.tab.c"
    break;

  case 42: /* die_roll: die_symbol NUMBER EXPLOSION PENETRATE  */
#line 1147 "src/grammar/dice.yacc"
                                         {
        /**
        * die_symbol vector 
        * NUMBER vector
        * EXPLOSION symbol 'e' or similar
        * PENETRATE symbol 'p'
        */
        vec ds = (yyvsp[-3].values);
        vec numB = (yyvsp[-2].values);
        

        long long start_from = ds.storage.content[0];


        vec number_of_dice;
        initialize_vector(&number_of_dice, NUMERIC, 1);
        number_of_dice.storage.content[0] = 1;

        roll_plain_sided_dice(
            &number_of_dice,
            &numB,
            &(yyval.values),
            PENETRATING_EXPLOSION,
            start_from
        );
        free_vector(number_of_dice);
        free_vector(ds);
        free_vector(numB);
    }
#line 2603 "y.tab.c"
    break;

  case 43: /* die_roll: NUMBER die_symbol NUMBER EXPLOSION  */
#line 1177 "src/grammar/dice.yacc"
                                      {
        /**
        * NUMBER vector
        * die_symbol vector 
        * NUMBER vector
        * EXPLOSION symbol 'e' or similar
        */

        vec numA = (yyvsp[-3].values);
        vec ds = (yyvsp[-2].values);
        vec numB = (yyvsp[-1].values);

        long long start_from = ds.storage.content[0];


        roll_plain_sided_dice(
            &numA,
            &numB,
            &(yyval.values),
            PENETRATING_EXPLOSION,
            start_from
        );
        free_vector(numA);
        free_vector(ds);
        free_vector(numB);
    }
#line 2634 "y.tab.c"
    break;

  case 44: /* die_roll: die_symbol NUMBER EXPLOSION  */
#line 1204 "src/grammar/dice.yacc"
                               {
        /**
        * die_symbol vector 
        * NUMBER vector
        * EXPLOSION symbol 'e' or similar
        */

        vec ds = (yyvsp[-2].values);
        vec numB = (yyvsp[-1].values);

        long long start_from = ds.storage.content[0];


        vec number_of_dice;
        initialize_vector(&number_of_dice, NUMERIC, 1);
        number_of_dice.storage.content[0] = 1;
        
        roll_plain_sided_dice(
            &number_of_dice,
            &numB,
            &(yyval.values),
            STANDARD_EXPLOSION,
            start_from
        );
        free_vector(numB);
        free_vector(ds);
        free_vector(number_of_dice);
    }
#line 2667 "y.tab.c"
    break;

  case 45: /* die_roll: NUMBER die_symbol NUMBER  */
#line 1233 "src/grammar/dice.yacc"
                            {
        /**
        * NUMBER vector
        * die_symbol vector 
        * NUMBER vector
        */
        vec numA = (yyvsp[-2].values);
        vec ds = (yyvsp[-1].values);
        vec numB = (yyvsp[0].values);

        long long start_from = ds.storage.content[0];


        roll_plain_sided_dice(
            &numA,
            &numB,
            &(yyval.values),
            NO_EXPLOSION,
            start_from
        );
        free_vector(numB);
        free_vector(ds);
        free_vector(numA);
    }
#line 2696 "y.tab.c"
    break;

  case 46: /* die_roll: die_symbol NUMBER  */
#line 1258 "src/grammar/dice.yacc"
                     {
        /**
        * die_symbol vector 
        * NUMBER vector
        */
        vec ds = (yyvsp[-1].values);
        vec numB = (yyvsp[0].values);
        vec new_vec;


        long long start_from = ds.storage.content[0];


        vec number_of_dice;
        initialize_vector(&number_of_dice, NUMERIC, 1);
        number_of_dice.storage.content[0] = 1;

        roll_plain_sided_dice(
            &number_of_dice,
            &numB,
            &new_vec,
            NO_EXPLOSION,
            start_from
        );
        free_vector(number_of_dice);
        free_vector(ds);
        free_vector(numB);
        (yyval.values) = new_vec;
    }
#line 2730 "y.tab.c"
    break;

  case 47: /* die_roll: NUMBER die_symbol MODULO  */
#line 1288 "src/grammar/dice.yacc"
                            {   
        /**
        * NUMBER vector
        * die_symbol vector - d or z 
        * MODULE symbol %
        */

        // TODO: z% is not functional!

        vec num_dice = (yyvsp[-2].values);
        vec dice_sides;
        initialize_vector(&dice_sides, NUMERIC, 1);
        dice_sides.storage.content[0] = 100;

        roll_plain_sided_dice(
            &num_dice,
            &dice_sides,
            &(yyval.values),
            NO_EXPLOSION,
            1
        );
        free_vector(num_dice);
        free_vector(dice_sides);
    }
#line 2759 "y.tab.c"
    break;

  case 48: /* die_roll: die_symbol MODULO  */
#line 1313 "src/grammar/dice.yacc"
                     {
        /**
        * die_symbol vector 
        * NUMBER vector
        */
        // TODO: z% is not possible yet.
        vec num_dice;
        initialize_vector(&num_dice, NUMERIC, 1);
        num_dice.storage.content[0] = 1;
        vec dice_sides;
        initialize_vector(&dice_sides, NUMERIC, 1);
        dice_sides.storage.content[0] = 100;

        roll_plain_sided_dice(
            &num_dice,
            &dice_sides,
            &(yyval.values),
            NO_EXPLOSION,
            1
        );
        free_vector(num_dice);
        free_vector(dice_sides);
    }
#line 2787 "y.tab.c"
    break;

  case 49: /* die_roll: NUMBER die_symbol DO_COUNT  */
#line 1337 "src/grammar/dice.yacc"
                              {
        /**
        * NUMBER vector
        * die_symbol vector 
        * DO_COUNT symbol 'c'
        */
        vec num = (yyvsp[-2].values);
        vec die_sym = (yyvsp[-1].values);

        long long start_from = die_sym.storage.content[0];


        vec dice_sides;
        initialize_vector(&dice_sides, NUMERIC, 1);
        dice_sides.storage.content[0] = 2;

        roll_plain_sided_dice(
            &num,
            &dice_sides,
            &(yyval.values),
            NO_EXPLOSION,
            start_from
        );
        free_vector(num);
        free_vector(die_sym);
    }
#line 2818 "y.tab.c"
    break;

  case 50: /* die_roll: die_symbol DO_COUNT  */
#line 1364 "src/grammar/dice.yacc"
                       {
        /**
        * die_symbol vector
        * DO_COUNT symbol 'c'
        */
        vec ds= (yyvsp[-1].values);

        long long start_from = ds.storage.content[0];


        vec num_dice;
        initialize_vector(&num_dice, NUMERIC, 1);
        num_dice.storage.content[0] = 1;
        vec dice_sides;
        initialize_vector(&dice_sides, NUMERIC, 1);
        dice_sides.storage.content[0] = 2;

        roll_plain_sided_dice(
            &num_dice,
            &dice_sides,
            &(yyval.values),
            NO_EXPLOSION,
            start_from
        );
        free_vector(ds);
        free_vector(num_dice);
        free_vector(dice_sides);
    }
#line 2851 "y.tab.c"
    break;

  case 51: /* die_roll: NUMBER FATE_DIE  */
#line 1393 "src/grammar/dice.yacc"
                   {
        /**
        * NUMBER - 
        */
        vec number_of_dice = (yyvsp[-1].values);
        vec symb = (yyvsp[0].values);
        vec result_vec;
        initialize_vector(&result_vec, SYMBOLIC, (unsigned int)number_of_dice.storage.content[0]);

        roll_symbolic_dice(
            &number_of_dice,
            &symb,
            &result_vec
        );
        (yyval.values) = result_vec;
        free_vector(symb);
        free_vector(number_of_dice);

    }
#line 2875 "y.tab.c"
    break;

  case 52: /* die_roll: FATE_DIE  */
#line 1413 "src/grammar/dice.yacc"
            {
        /** 
        * FATE_DIE - Vector
        */
        vec symb = (yyvsp[0].values);
        vec result_vec;
        vec number_of_dice;
        initialize_vector(&result_vec, SYMBOLIC, 1);
        initialize_vector(&number_of_dice, NUMERIC, 1);
        number_of_dice.storage.content[0] = 1;

        roll_symbolic_dice(
            &number_of_dice,
            &symb,
            &result_vec
        );
        (yyval.values) = result_vec;
        free_vector(symb);
        free_vector(number_of_dice);

    }
#line 2901 "y.tab.c"
    break;

  case 55: /* custom_symbol_dice: NUMBER die_symbol SYMBOL_LBRACE csd SYMBOL_RBRACE  */
#line 1443 "src/grammar/dice.yacc"
    {
        /**
        * NUMBER - vector
        * die_symbol - vector
        * SYMBOL_LBRACE - the symbol {
        * csd - vector
        * SYMBOL_RBRACE - the symbol }
        */
        // Nd{SYMB}
        vec left = (yyvsp[-4].values);
        vec dsymb = (yyvsp[-3].values);
        vec right = (yyvsp[-1].values);

        // TODO: Multiple ranges

        vec result_vec;
        initialize_vector(&result_vec, SYMBOLIC, (unsigned int)left.storage.content[0]);

        roll_symbolic_dice(
            &left,
            &right,
            &result_vec
        );
        
        free_vector(left);
        free_vector(right);
        free_vector(dsymb);
        (yyval.values) = result_vec;
    }
#line 2935 "y.tab.c"
    break;

  case 56: /* custom_symbol_dice: die_symbol SYMBOL_LBRACE csd SYMBOL_RBRACE  */
#line 1474 "src/grammar/dice.yacc"
    {
        /** @brief 
        * @param die_symbol a vector
        * @param SYMBOL_LBRACE the symbol "{"
        * @param csd a vector
        * @param SYMBOL_LBRACE the symbol "}"
        * returns a vector
        */
        vec csd_vec = (yyvsp[-1].values);
        vec number_of_dice;
        vec result_vec;
        initialize_vector(&number_of_dice, NUMERIC, 1);
        number_of_dice.storage.content[0] = 1;
        
        if (csd_vec.dtype == NUMERIC){
            vec dice_sides;
            vec num_dice;
            initialize_vector(&dice_sides, NUMERIC, 1);
            initialize_vector(&num_dice, NUMERIC, 1);
            initialize_vector(&result_vec, NUMERIC, 1);
            num_dice.storage.content[0] = 1;


            long long start_value = csd_vec.storage.content[0];
            long long end_value = csd_vec.storage.content[csd_vec.length-1];
            
            dice_sides.storage.content[0] = end_value - start_value + 1;


            // Range
            roll_plain_sided_dice(
                &num_dice,
                &dice_sides,
                &result_vec,
                NO_EXPLOSION,
                start_value
            );
            free_vector(dice_sides);
            free_vector(num_dice);
        }else{
            initialize_vector(&result_vec, SYMBOLIC, 1);

            roll_params rp = {
                .number_of_dice=(unsigned int)number_of_dice.storage.content[0],
                .die_sides=csd_vec.length,
                .dtype=SYMBOLIC,
                .start_value=0,
                .symbol_pool=(char **)safe_calloc(csd_vec.length , sizeof(char *))
            };
            result_vec.source = rp;
            result_vec.has_source = true;
            for(unsigned long long i = 0; i != csd_vec.length; i++){
                result_vec.source.symbol_pool[i] = (char*)safe_calloc(sizeof(char),MAX_SYMBOL_LENGTH);
                memcpy(
                    result_vec.source.symbol_pool[i], 
                    csd_vec.storage.symbols[i], 
                    MAX_SYMBOL_LENGTH*sizeof(char)
                );
            }

            // Custom Symbol
            roll_symbolic_dice(
                &number_of_dice,
                &csd_vec,
                &result_vec
            );
        }

        free_vector(number_of_dice);
        free_vector(csd_vec);
        free_vector((yyvsp[-3].values));
        (yyval.values) = result_vec;
    }
#line 3013 "y.tab.c"
    break;

  case 57: /* custom_symbol_dice: MACRO_ACCESSOR CAPITAL_STRING  */
#line 1548 "src/grammar/dice.yacc"
                                 {
        /**
        * MACRO_ACCESSOR the symbol '@'
        * CAPITAL_STRING A vector containing a macro identifier
        * return A vector containing rollparams for the selected  macro
        */
        vec vector = (yyvsp[0].values);
        char * name = vector.storage.symbols[0];

        vec new_vector;
        search_macros(name, &new_vector.source);

        if(gnoll_errno){YYABORT;yyclearin;}
        // Resolve Roll

        vec number_of_dice;
        vec die_sides;

        // Set Num Dice
        initialize_vector(&number_of_dice, NUMERIC, 1);

        number_of_dice.storage.content[0] = (long long)new_vector.source.number_of_dice;

        
        // Set Die Sides
        // die_sides.storage.content[0] = (int)new_vector.source.die_sides;
        // die_sides.storage.symbols = NULL;

        // Roll according to the stored values
        // Careful: Newvector used already
        if (new_vector.source.dtype == NUMERIC){
            light_initialize_vector(&die_sides, NUMERIC, 1);
            die_sides.length = new_vector.source.die_sides;
            die_sides.storage.content[0] = (int)new_vector.source.die_sides;
            initialize_vector(&new_vector, new_vector.source.dtype, 1);
            roll_plain_sided_dice(
                &number_of_dice,
                &die_sides,
                &new_vector,
                new_vector.source.explode,
                1
            );
            free_vector(die_sides);

        }else if (new_vector.source.dtype == SYMBOLIC){
            light_initialize_vector(&die_sides, SYMBOLIC, 1);
            die_sides.length = new_vector.source.die_sides;
            free(die_sides.storage.symbols);  
            safe_copy_2d_chararray_with_allocation(
                &die_sides.storage.symbols,
                new_vector.source.symbol_pool,
                die_sides.length,
                MAX_SYMBOL_LENGTH
            );

            free_2d_array(&new_vector.source.symbol_pool, new_vector.source.die_sides);

            initialize_vector(&new_vector, new_vector.source.dtype, 1);
            roll_symbolic_dice(
                &number_of_dice,
                &die_sides,
                &new_vector
            );
            free_vector(die_sides);

        }else{
            printf("Complex Dice Equation. Only dice definitions supported. No operations\n");
            gnoll_errno = NOT_IMPLEMENTED;
        }
        free_vector(vector);
        free_vector(number_of_dice);
        (yyval.values) = new_vector;
    }
#line 3091 "y.tab.c"
    break;

  case 58: /* csd: csd SYMBOL_SEPERATOR csd  */
#line 1623 "src/grammar/dice.yacc"
                            {
        /**
        * csd a vector containing custom symbols
        * SYMBOL_SEPERATOR the symbol ','
        * csd a vector containing custom symbols
        * return A vector with all the symbols
        */
        vec l = (yyvsp[-2].values);
        vec r = (yyvsp[0].values);

        vec new_vector;
        initialize_vector(&new_vector, SYMBOLIC, l.length + r.length);

        concat_symbols(
            l.storage.symbols, l.length,
            r.storage.symbols, r.length,
            new_vector.storage.symbols
        );
        free_vector(l);
        free_vector(r);
        (yyval.values) = new_vector;
    }
#line 3118 "y.tab.c"
    break;

  case 59: /* csd: NUMBER RANGE NUMBER  */
#line 1646 "src/grammar/dice.yacc"
                       {
        /**
        * NUMBER The symbol 0-9+
        * RANGE The symbol '..'
        * NUMBER The symbol 0-9+
        * return A vector containing the numeric values as symbols 
        */
        vec start = (yyvsp[-2].values);
        vec end = (yyvsp[0].values);


        long long s = start.storage.content[0];
        long long e = end.storage.content[0];



        if (s > e){
            printf("Range: %lld -> %lld\n", s, e);
            printf("Reversed Ranged not supported yet.\n");
            gnoll_errno = NOT_IMPLEMENTED;
            YYABORT;
            yyclearin;
        }

        // How many values in this range:
        // 2..2 = 1 
        // 2..3 = 2
        // etc.
        unsigned long long spread = (unsigned long long)e - (unsigned long long)s + 1; 

        vec new_vector;
        initialize_vector(&new_vector, SYMBOLIC, spread);

        for (unsigned long long i = 0; i <= spread-1; i++){
            sprintf(new_vector.storage.symbols[i], "%lld", s+i);

        }
        (yyval.values) = new_vector;
    }
#line 3162 "y.tab.c"
    break;

  case 61: /* csd: NUMBER  */
#line 1688 "src/grammar/dice.yacc"
          {
        /**
        * NUMBER The symbol 0-9+
        * return A vector containing the numeric values as symbols 
        */
        vec in = (yyvsp[0].values);

        long long tmp = in.storage.content[0];
        free(in.storage.content);
        in.storage.symbols = safe_calloc(1, sizeof(char *));
        // an int has 10 characters max
        in.storage.symbols[0] = safe_calloc(countDigits(LLONG_MAX), sizeof(char));  
        sprintf(in.storage.symbols[0], "%lld", tmp);

        in.dtype = SYMBOLIC;
        (yyval.values) = in;
    }
#line 3184 "y.tab.c"
    break;

  case 71: /* die_symbol: SIDED_DIE  */
#line 1711 "src/grammar/dice.yacc"
             {
        /**
        * @brief SIDED_DIE The symbol 'd'
        * @param return A vector containing '1', the start index
        */
        vec new_vec;
        initialize_vector(&new_vec, NUMERIC, 1);
        new_vec.storage.content[0] = 1;
        (yyval.values) = new_vec;
    }
#line 3199 "y.tab.c"
    break;

  case 72: /* die_symbol: SIDED_DIE_ZERO  */
#line 1722 "src/grammar/dice.yacc"
                  {
        /**
        * SIDED_DIE The symbol 'z'
        * return A vector containing '0', the start index
        */
        vec new_vec;
        initialize_vector(&new_vec, NUMERIC, 1);
        new_vec.storage.content[0] = 0;
        (yyval.values) = new_vec;
    }
#line 3214 "y.tab.c"
    break;


#line 3218 "y.tab.c"

      default: break;
    }
  /* User semantic actions sometimes alter yychar, and that requires
     that yytoken be updated with the new translation.  We take the
     approach of translating immediately before every use of yytoken.
     One alternative is translating here after every semantic action,
     but that translation would be missed if the semantic action invokes
     YYABORT, YYACCEPT, or YYERROR immediately after altering yychar or
     if it invokes YYBACKUP.  In the case of YYABORT or YYACCEPT, an
     incorrect destructor might then be invoked immediately.  In the
     case of YYERROR or YYBACKUP, subsequent parser actions might lead
     to an incorrect destructor call or verbose syntax error message
     before the lookahead is translated.  */
  YY_SYMBOL_PRINT ("-> $$ =", YY_CAST (yysymbol_kind_t, yyr1[yyn]), &yyval, &yyloc);

  YYPOPSTACK (yylen);
  yylen = 0;

  *++yyvsp = yyval;

  /* Now 'shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */
  {
    const int yylhs = yyr1[yyn] - YYNTOKENS;
    const int yyi = yypgoto[yylhs] + *yyssp;
    yystate = (0 <= yyi && yyi <= YYLAST && yycheck[yyi] == *yyssp
               ? yytable[yyi]
               : yydefgoto[yylhs]);
  }

  goto yynewstate;


/*--------------------------------------.
| yyerrlab -- here on detecting error.  |
`--------------------------------------*/
yyerrlab:
  /* Make sure we have latest lookahead translation.  See comments at
     user semantic actions for why this is necessary.  */
  yytoken = yychar == YYEMPTY ? YYSYMBOL_YYEMPTY : YYTRANSLATE (yychar);
  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;
      yyerror (YY_("syntax error"));
    }

  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse lookahead token after an
         error, discard it.  */

      if (yychar <= YYEOF)
        {
          /* Return failure if at end of input.  */
          if (yychar == YYEOF)
            YYABORT;
        }
      else
        {
          yydestruct ("Error: discarding",
                      yytoken, &yylval);
          yychar = YYEMPTY;
        }
    }

  /* Else will try to reuse lookahead token after shifting the error
     token.  */
  goto yyerrlab1;


/*---------------------------------------------------.
| yyerrorlab -- error raised explicitly by YYERROR.  |
`---------------------------------------------------*/
yyerrorlab:
  /* Pacify compilers when the user code never invokes YYERROR and the
     label yyerrorlab therefore never appears in user code.  */
  if (0)
    YYERROR;
  ++yynerrs;

  /* Do not reclaim the symbols of the rule whose action triggered
     this YYERROR.  */
  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);
  yystate = *yyssp;
  goto yyerrlab1;


/*-------------------------------------------------------------.
| yyerrlab1 -- common code for both syntax error and YYERROR.  |
`-------------------------------------------------------------*/
yyerrlab1:
  yyerrstatus = 3;      /* Each real token shifted decrements this.  */

  /* Pop stack until we find a state that shifts the error token.  */
  for (;;)
    {
      yyn = yypact[yystate];
      if (!yypact_value_is_default (yyn))
        {
          yyn += YYSYMBOL_YYerror;
          if (0 <= yyn && yyn <= YYLAST && yycheck[yyn] == YYSYMBOL_YYerror)
            {
              yyn = yytable[yyn];
              if (0 < yyn)
                break;
            }
        }

      /* Pop the current state because it cannot handle the error token.  */
      if (yyssp == yyss)
        YYABORT;


      yydestruct ("Error: popping",
                  YY_ACCESSING_SYMBOL (yystate), yyvsp);
      YYPOPSTACK (1);
      yystate = *yyssp;
      YY_STACK_PRINT (yyss, yyssp);
    }

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END


  /* Shift the error token.  */
  YY_SYMBOL_PRINT ("Shifting", YY_ACCESSING_SYMBOL (yyn), yyvsp, yylsp);

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturnlab;


/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturnlab;


/*-----------------------------------------------------------.
| yyexhaustedlab -- YYNOMEM (memory exhaustion) comes here.  |
`-----------------------------------------------------------*/
yyexhaustedlab:
  yyerror (YY_("memory exhausted"));
  yyresult = 2;
  goto yyreturnlab;


/*----------------------------------------------------------.
| yyreturnlab -- parsing is finished, clean up and return.  |
`----------------------------------------------------------*/
yyreturnlab:
  if (yychar != YYEMPTY)
    {
      /* Make sure we have latest lookahead translation.  See comments at
         user semantic actions for why this is necessary.  */
      yytoken = YYTRANSLATE (yychar);
      yydestruct ("Cleanup: discarding lookahead",
                  yytoken, &yylval);
    }
  /* Do not reclaim the symbols of the rule whose action triggered
     this YYABORT or YYACCEPT.  */
  YYPOPSTACK (yylen);
  YY_STACK_PRINT (yyss, yyssp);
  while (yyssp != yyss)
    {
      yydestruct ("Cleanup: popping",
                  YY_ACCESSING_SYMBOL (+*yyssp), yyvsp);
      YYPOPSTACK (1);
    }
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif

  return yyresult;
}

#line 1736 "src/grammar/dice.yacc"

/* Subroutines */

typedef struct yy_buffer_state * YY_BUFFER_STATE;
extern YY_BUFFER_STATE yy_scan_string(char * str);
extern void yy_delete_buffer(YY_BUFFER_STATE buffer);

#ifdef __EMSCRIPTEN__
EMSCRIPTEN_KEEPALIVE
#endif
int roll_full_options(
    char* roll_request, 
    char* log_file, 
    int enable_verbosity, 
    int enable_introspection,
    int enable_mocking,
    int enable_builtins,
    int mocking_type,
    long long mocking_seed
){
    /**
    * @brief the main GNOLL roll function
    * @param roll_request the dice notation to parse
    * @param log_file the file location to write results to
    * @param enable_verbosity Adds extra prints to the program
    * @param enable_introspection Adds per-dice breakdown in the output file
    * @param enable_mocking Replaces random rolls with predictables values for testing
    * @param enable_builtins Load in predefined macros for usage
    * @param mocking_type Type of mock values to generate
    * @param mocking_seed The first value of the mock generation to produce
    * @return GNOLL error code
    */
    gnoll_errno = 0;

    if (enable_verbosity){
        verbose = 1;
        printf("Trying to roll '%s'\n", roll_request);
    }
    if (enable_mocking){
        if (enable_verbosity){ printf("mocking_seed '%lld'\n", mocking_seed); }
        init_mocking((MOCK_METHOD)mocking_type, mocking_seed);
    }
    if (log_file != NULL){
        write_to_file = 1;
        output_file = log_file;
        if (enable_introspection){
            dice_breakdown = 1;
        }
    }else{
        if (enable_introspection){
            // Introspection is only implemented on a file-basis
            gnoll_errno = NOT_IMPLEMENTED;
            return gnoll_errno;
        }
    }

    initialize();
    
    if(enable_builtins){
        load_builtins("builtins/");
    }
    
    YY_BUFFER_STATE buffer = yy_scan_string(roll_request);
    yyparse();
    yy_delete_buffer(buffer);
    delete_all_macros();

    return gnoll_errno;
}

void load_builtins(char* root){

    int db_setting = dice_breakdown;
    dice_breakdown = 0; // Dont want dice breakdown for all the macro loading

    tinydir_dir dir = (tinydir_dir){0};
    tinydir_open(&dir, root);
    
    int count = 0;
    while (dir.has_next)
    {
        tinydir_file file;
        tinydir_readfile(&dir, &file);
        if(verbose){
            printf("%s", file.name);
        }
        if (file.is_dir)
        {
            if(verbose){
                printf("/\n");
            }
        }else{
            char *ext = strrchr(file.name, '.');

            if(strcmp(".dice", ext) != 0){
                if(verbose){
                    printf("Skip %s\n", file.name);
                }        
                tinydir_next(&dir);
                continue;
            }

            count++;
            if(verbose){
               printf("\n");
            }
            
            unsigned long max_file_path_length = 1000;
            int max_macro_length = 1000;

            char* path = safe_calloc(sizeof(char), max_file_path_length);
            char* stored_str = safe_calloc(sizeof(char), (unsigned long)max_macro_length);
            if(gnoll_errno){return;}

            // Get full path
            strcat(path, "builtins/");
            strcat(path, file.name);
            
            // TODO: Check filename for length
            FILE* fp = fopen(path, "r");
            while (fgets(stored_str, max_macro_length, fp)!=NULL){
                if(verbose){
                    printf("Contents: %s\n",stored_str); 
                }
                YY_BUFFER_STATE buffer = yy_scan_string(stored_str);
                yyparse();
                yy_delete_buffer(buffer);
                if(gnoll_errno){return;}
            }
            fclose(fp);
            free(path);
            free(stored_str);
        }
        tinydir_next(&dir);
    }

    tinydir_close(&dir);
    dice_breakdown = db_setting;
    return;
}

// The following are legacy functions to be deprecated in the future
// in favor of the general roll_full_options() fn.

int roll(char * s){
    return roll_full_options(s, NULL, 1, 0, 0, 0, 0, 0);
}

int roll_with_breakdown(char * s, char* f){
    return roll_full_options(s, f, 0, 1, 0, 0, 0, 0);
}

int roll_and_write(char* s, char* f){
    return roll_full_options(s, f, 0, 0, 0, 0, 0, 0);
}

void roll_and_write_R(int* return_code, char** s, char** f){    
    (*return_code) = roll_full_options(s[0], f[0], 0, 0, 0, 0, 0, 0);
}

int mock_roll(char * s, char * f, int mock_value, long long mock_const){
    return roll_full_options(s, f, 0, 0, 1, 0, mock_value, mock_const);
}

int main(int argc, char **str){

    for(int a = 1; a != argc; a++){
        if(strcmp(str[a], "--help")==0){
            printf("GNOLL Dice Notation Parser\n");
            printf("Usage: ./executable [dice notation]\n");
            printf("Executable is non configurable. Use functions directly for advanced features.\n");
            return 0;
        }
        if(strcmp(str[a], "--version")==0){
            printf("GNOLL 4.3.0\n");
            return 0;
        }
    }
    
    // Join arguments if they came in as seperate strings

    char * s = concat_strings(&str[1], (unsigned int)(argc - 1));

    remove("output.dice");
    roll_full_options(
        s,
        "output.dice",
        0,  // Verbose
        0,  // Introspect
        0,  // Mocking
        1,  // Builtins
        0,  // Mocking
        0   // Mocking Seed
    );
    print_gnoll_errors();
#ifndef __EMSCRIPTEN__
    FILE  *f = fopen("output.dice","r");
    int c;
    if (f){
        printf("Result:\n");
        while((c = getc(f)) !=  EOF){
            putchar(c);
        }
        fclose(f);
    }
#endif
    // Final Freeing
    free(macros);
}

int yyerror(const char *s)
{
    fprintf(stderr, "%s\n", s);

    if(write_to_file){
        FILE *fp;
        fp = safe_fopen(output_file, "a+");
        fprintf(fp, "%s;", s);
        fclose(fp);
    }
    return(gnoll_errno);

}

int yywrap(void){
    return (1);
}

