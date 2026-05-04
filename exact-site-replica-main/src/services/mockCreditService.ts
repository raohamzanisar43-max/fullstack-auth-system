import { CreditBalance, CreditPurchase, CreditPurchaseResponse, CreditPackage } from '@/types/credit';

// Mock data for testing
const mockPackages: CreditPackage[] = [
  {
    id: 1,
    name: "Starter Pack",
    credits: 1000,
    price: 20.00,
    description: "Perfect for getting started with our tracing services",
    bonus_credits: 0,
    is_active: true,
  },
  {
    id: 2,
    name: "Professional Pack",
    credits: 2000,
    price: 40.00,
    description: "Great for regular users and small businesses",
    bonus_credits: 0,
    is_active: true,
  },
  {
    id: 3,
    name: "Business Pack",
    credits: 5000,
    price: 100.00,
    description: "Ideal for growing businesses with moderate usage",
    bonus_credits: 500,
    is_active: true,
  },
  {
    id: 4,
    name: "Enterprise Pack",
    credits: 10000,
    price: 200.00,
    description: "Perfect for large teams and high-volume usage",
    bonus_credits: 1000,
    is_active: true,
  },
  {
    id: 5,
    name: "Ultimate Pack",
    credits: 20000,
    price: 400.00,
    description: "Maximum value for enterprise-level operations",
    bonus_credits: 2500,
    is_active: true,
  },
];

let mockBalance: CreditBalance = {
  user_id: 1,
  current_credits: 118,
  total_purchased: 1000,
  total_used: 882,
  total_bonus: 0,
  effective_rate: 0.02,
  last_updated: new Date().toISOString(),
};

class MockCreditService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  async getCreditBalance(): Promise<CreditBalance> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    return { ...mockBalance };
  }

  async getCreditPackages(): Promise<CreditPackage[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    return [...mockPackages];
  }

  async purchaseCredits(purchaseData: CreditPurchase): Promise<CreditPurchaseResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const packageData = mockPackages.find(p => p.id === purchaseData.package_id);
    if (!packageData) {
      throw new Error('Package not found');
    }

    const totalCredits = packageData.credits + packageData.bonus_credits;
    
    // Update mock balance
    mockBalance.current_credits += totalCredits;
    mockBalance.total_purchased += packageData.credits;
    mockBalance.total_bonus += packageData.bonus_credits;
    mockBalance.last_updated = new Date().toISOString();

    const transactionId = `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    return {
      transaction_id: transactionId,
      credits_added: packageData.credits,
      bonus_credits: packageData.bonus_credits,
      total_credits: totalCredits,
      new_balance: mockBalance.current_credits,
      amount_charged: packageData.price,
      currency: purchaseData.currency,
    };
  }

  async validateDiscountCode(code: string): Promise<{ valid: boolean; percentage?: number; message?: string }> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const validCodes = {
      'SAVE10': { percentage: 10, message: '10% discount applied' },
      'SAVE20': { percentage: 20, message: '20% discount applied' },
      'WELCOME': { percentage: 15, message: 'Welcome! 15% discount applied' },
      'TEST': { percentage: 5, message: 'Test code - 5% discount' },
    };

    const upperCode = code.toUpperCase().trim();
    if (validCodes[upperCode as keyof typeof validCodes]) {
      return {
        valid: true,
        percentage: validCodes[upperCode as keyof typeof validCodes].percentage,
        message: validCodes[upperCode as keyof typeof validCodes].message,
      };
    }

    return { valid: false, message: 'Invalid discount code' };
  }

  async processPayment(paymentData: {
    amount: number;
    currency: string;
    paymentMethodId: string;
  }): Promise<{ status: string; transactionId: string }> {
    // Simulate payment processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simulate occasional payment failures (10% chance)
    if (Math.random() < 0.1) {
      throw new Error('Payment failed: Insufficient funds');
    }
    
    return {
      status: 'completed',
      transactionId: `pi_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };
  }

  // Helper method to reset mock data (for testing)
  resetMockData() {
    mockBalance = {
      user_id: 1,
      current_credits: 118,
      total_purchased: 1000,
      total_used: 882,
      total_bonus: 0,
      effective_rate: 0.02,
      last_updated: new Date().toISOString(),
    };
  }
}

export const mockCreditService = new MockCreditService();
