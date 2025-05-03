package main

import (
    "fmt"
)

func isPrime(n int) bool {
    if n <= 1 {
        return false
    }
    for i := 2; i*i <= n; i++ {
        if n%i == 0 {
            return false
        }
    }
    return true
}

func main() {
    num := 29

    if isPrime(num) {
        fmt.Printf("%d is a prime number\n", num)
    } else {
        fmt.Printf("%d is not a prime number\n", num)
    }
}
