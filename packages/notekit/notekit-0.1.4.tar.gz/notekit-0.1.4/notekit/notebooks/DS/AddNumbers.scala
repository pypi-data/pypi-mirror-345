object Main {
  def main(args: Array[String]): Unit = {
    // Taking two numbers as input
    println("Enter the first number: ")
    val num1 = scala.io.StdIn.readInt()
    
    println("Enter the second number: ")
    val num2 = scala.io.StdIn.readInt()

    // Calculating the sum
    val sum = num1 + num2

    // Displaying the result
    println(s"The sum of $num1 and $num2 is: $sum")
  }
}
