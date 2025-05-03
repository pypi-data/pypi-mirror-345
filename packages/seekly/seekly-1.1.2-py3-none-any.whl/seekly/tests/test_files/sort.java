public class SortTwoElements {
    public static void main(String[] args) {
        int a = 10;
        int b = 5;

        // Before Sorting
        System.out.println("Before Sorting: a = " + a + ", b = " + b);

        // Sorting logic
        if (a > b) {
            // Swap a and b
            int temp = a;
            a = b;
            b = temp;
        }

        // After Sorting
        System.out.println("After Sorting: a = " + a + ", b = " + b);
    }
}
