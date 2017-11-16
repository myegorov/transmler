(*#line 1.1 "../../src/stack.sigb"*)(* vim: set filetype=sml: *)

(* http://www.cs.cornell.edu/courses/cs312/2008sp/lectures/lec07.html *)
signature STACK =
  sig
    (* An 'a stack is a immutable stack of elements of 'a. *)
    type 'a stack
    exception EmptyStack

    (* empty is the empty stack *)
    val empty : 'a stack

    (* Returns: whether a stack is empty *)
    val isEmpty : 'a stack -> bool

    (* push(x,s) is the stack s with x pushed on top. *)
    val push : ('a * 'a stack) -> 'a stack

    (* pop(s) is s with the top element removed. *)
    val pop : 'a stack -> 'a * 'a stack

    (* map f s is a new stack whose elements correspond to
     * those in s through the mapping of the function f. *)
    val map : ('a -> 'b) -> 'a stack -> 'b stack

end
