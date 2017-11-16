(* http://www.cs.cornell.edu/courses/cs312/2008sp/lectures/lec07.html *)
structure Stack : STACK =
  struct
    (* The elements in the stack are the list elements, with the top of the
     * stack represented by the head of the list, and so forth.  *)
    type 'a stack = 'a list
    exception EmptyStack

    val empty = []

    fun isEmpty l = List.null l

    fun push (x, l) = x::l

    fun pop (l) =
      case l of
          [] => raise EmptyStack
        | x::xs => (x, xs)

    fun map (f: 'a -> 'b) l = List.map f l

  end
