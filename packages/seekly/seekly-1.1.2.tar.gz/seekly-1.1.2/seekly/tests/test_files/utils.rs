fn sort_two_elements(mut a: i32, mut b: i32) {
    if a > b {
        let temp = a;
        a = b;
        b = temp;
    }
    println!("Sorted: {}, {}", a, b);
}

fn add_two_elements(a: i32, b: i32) {
    println!("Sum: {}", a + b);
}

fn binary_search(arr: &[i32], target: i32) -> i32 {
    let mut left = 0;
    let mut right = arr.len() as i32 - 1;

    while left <= right {
        let mid = left + (right - left) / 2;
        if arr[mid as usize] == target {
            return mid;
        } else if arr[mid as usize] < target {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    -1
}

fn subtract(a: i32, b: i32) {
    println!("Subtraction: {}", a - b);
}

fn is_prime(n: i32) -> bool {
    if n <= 1 {
        return false;
    }
    for i in 2..=((n as f64).sqrt() as i32) {
        if n % i == 0 {
            return false;
        }
    }
    true
}

fn odd_or_even(n: i32) {
    if n % 2 == 0 {
        println!("{} is Even", n);
    } else {
        println!("{} is Odd", n);
    }
}

fn main() {
    // Sorting two elements
    sort_two_elements(12, 7);

    // Adding two elements
    add_two_elements(5, 9);

    // Binary search
    let arr = [2, 4, 6, 8, 10, 12];
    let target = 8;
    let result = binary_search(&arr, target);
    if result != -1 {
        println!("Binary Search: Element found at index {}", result);
    } else {
        println!("Binary Search: Element not found");
    }

    // Subtraction
    subtract(20, 7);

    // Prime number checking
    let num = 31;
    if is_prime(num) {
        println!("{} is a Prime number", num);
    } else {
        println!("{} is not a Prime number", num);
    }

    // Odd or even checking
    odd_or_even(17);
}
