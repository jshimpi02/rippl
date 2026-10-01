public class App {

    public double calculateDiscount(double amount) {
        double discount = 0.0;

        if (amount > 1000) {
            discount = amount * 0.10;
        }

        return discount;
    }

    public double calculateTax(double amount, String state) {
        if (state.equals("IL")) {
            return amount * 0.0625;
        }

        if (state.equals("IN")) {
            return amount * 0.07;
        }

        return 0.0;
    }
}