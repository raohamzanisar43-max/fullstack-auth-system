import { CreditBalance, CreditPurchase, CreditPurchaseResponse, CreditPackage } from '@/types/credit';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class CreditService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  async getCreditBalance(): Promise<CreditBalance> {
    const response = await fetch(`${API_BASE_URL}/credits/balance`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch credit balance');
    }

    return response.json();
  }

  async getCreditPackages(): Promise<CreditPackage[]> {
    const response = await fetch(`${API_BASE_URL}/credits/packages`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch credit packages');
    }

    return response.json();
  }

  async purchaseCredits(purchaseData: CreditPurchase): Promise<CreditPurchaseResponse> {
    const response = await fetch(`${API_BASE_URL}/credits/purchase`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(purchaseData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to purchase credits');
    }

    return response.json();
  }

  async validateDiscountCode(code: string): Promise<{ valid: boolean; percentage?: number; message?: string }> {
    // Simulate discount code validation - replace with actual API call
    const validCodes = {
      'SAVE10': { percentage: 10, message: '10% discount applied' },
      'SAVE20': { percentage: 20, message: '20% discount applied' },
      'WELCOME': { percentage: 15, message: 'Welcome! 15% discount applied' },
    };

    const upperCode = code.toUpperCase();
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
    // This would integrate with Stripe or other payment processor
    // For now, simulating a successful payment
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      status: 'completed',
      transactionId: `pi_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };
  }
}

export const creditService = new CreditService();
