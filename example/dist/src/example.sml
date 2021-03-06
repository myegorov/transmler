(*#line 6.1 "../../src/example.smlb"*)fun main () =
  let
    val stack = Stack'.push(3, Stack'.push(2, Stack'.push(1, Stack'.empty)))
    fun pprint s = List.app print (map (fn x => (Int.toString x) ^ "\n") s)
  in
    pprint stack
  end

val _ = main ()
