(* vim: set filetype=sml: *)
type pos = int
type lexresult = Tokens.token

val lineNum = ErrorMsg.lineNum
val linePos = ErrorMsg.linePos
fun err loc = ErrorMsg.error loc

val nestedParen = ref 0
val nestedComment = ref 0
fun eof () =
  let
    val pos = hd(!linePos)
  in 
    if !nestedComment <> 0
    then err pos "EOF occurred within a comment."
    else if !nestedParen <> 0
    then err pos "EOF occurred within open parenthesis."
    else ();
    Tokens.EOF (pos,pos)
  end

fun inc i = i := !i + 1
fun dec i = i := !i - 1
fun incLine loc =
  inc lineNum;
  linePos := loc :: !linePos

val path = ref ""
val pathPos = ref 0
fun appendToPath s = path := !path ^ s


%%
%s EXPORT IMPORT COMMENT;
alpha = [A-Za-z];
numeric = [0-9];
id = {alpha}({alpha}|{numeric}|'|_)*;
ws = [\ \t\r\f\v\n];
basis = ("$(SML_LIB)/")({alpha}|{numeric}|-|\.|\/)+;


%%
(* TODO: skip over nested comments throughout *)
<INITIAL,EXPORT,IMPORT>"\n"	=> (incLine yypos; continue());
<INITIAL,EXPORT,IMPORT>{ws} => (continue());
<INITIAL>"export"           => (YYBEGIN EXPORT;
                                Tokens.EXPORT (yypos, yypos + size yytext));
<INITIAL>"import"           => (YYBEGIN IMPORT;
                                Tokens.IMPORT (yypos, yypos + size yytext));


<EXPORT,IMPORT>"("          => (inc nestedParen;
                                Tokens.LPAREN(yypos, yypos + 1));
<EXPORT>")"                 => (dec nestedParen;
                                if !nestedParen = 0
                                then YYBEGIN INITIAL
                                else ();
                                Tokens.RPAREN(yypos, yypos + 1));
<EXPORT,IMPORT>"signature"  => (Tokens.SIG (yypos, yypos + size yytext));
<EXPORT,IMPORT>"structure"  => (Tokens.STRUCT (yypos, yypos + size yytext));
<EXPORT,IMPORT>"functor"    => (Tokens.FUNCT (yypos, yypos + size yytext));
<EXPORT,IMPORT>"="          => (Tokens.EQ (yypos, yypos + 1));
<EXPORT,IMPORT>","          => (Tokens.COMMA (yypos, yypos + 1));
<EXPORT>{id}                => (Tokens.ID (yytext, yypos, yypos + size yytext));
<EXPORT>.                   => (err yypos ("illegal character " ^ yytext);
                                continue());


<IMPORT>")"                 => (dec nestedParen;
                                Tokens.RPAREN(yypos, yypos + 1));
<IMPORT>"from"              => (Tokens.FROM(yypos, yypos + size yytext));
<IMPORT>{basis}             => (YYBEGIN INITIAL;
                                Tokens.BAS(yytext, yypos, yypos + size yytext));
<IMPORT>"\""                => (YYBEGIN STRING;
                                path := ""; pathPos := yypos; continue());
<STRING>"\""                => (YYBEGIN INITIAL;
                                Tokens.PATH(!path, !pathPos, yypos + 1));
(* TODO: continue handling quoted strings: printable & escape sequences *)

<IMPORT>.                   => (err yypos ("illegal character " ^ yytext);
                                continue());


<INITIAL>.                  => (Tokens.SML (yypos, yypos + 1));
