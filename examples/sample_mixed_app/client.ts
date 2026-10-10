export function calculateDiscount(
    amount: number,
    isPremium: boolean
  ): number {
    let discount = 0;
  
    if (isPremium && amount > 1000) {
      discount = amount * 0.15;
    }
  
    return discount;
  }
  
  export const calculateTax = (
    amount: number,
    state: string
  ): number => {
    if (state === "IL") {
      return amount * 0.0625;
    }
  
    if (state === "IN") {
      return amount * 0.07;
    }
  
    return 0;
  };