import { useState, useEffect, useCallback } from 'react';
import { creditService } from '@/services/creditService';
import { CreditBalance, CreditPackage } from '@/types/credit';
import { toast } from 'sonner';

export function useCredits() {
  const [balance, setBalance] = useState<CreditBalance | null>(null);
  const [packages, setPackages] = useState<CreditPackage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBalance = useCallback(async () => {
    try {
      const balanceData = await creditService.getCreditBalance();
      setBalance(balanceData);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch credit balance';
      setError(errorMessage);
      toast.error(errorMessage);
    }
  }, []);

  const fetchPackages = useCallback(async () => {
    try {
      const packagesData = await creditService.getCreditPackages();
      setPackages(packagesData);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch credit packages';
      setError(errorMessage);
      toast.error(errorMessage);
    }
  }, []);

  const purchaseCredits = useCallback(async (packageId: number, paymentMethodId: string) => {
    try {
      setIsLoading(true);
      const purchaseData = {
        package_id: packageId,
        payment_method_id: paymentMethodId,
        amount: 0, // This will be calculated based on package
        currency: 'USD',
      };

      const result = await creditService.purchaseCredits(purchaseData);
      
      // Refresh balance after successful purchase
      await fetchBalance();
      
      toast.success(`Successfully purchased ${result.total_credits} credits!`);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to purchase credits';
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchBalance]);

  const validateDiscountCode = useCallback(async (code: string) => {
    try {
      const result = await creditService.validateDiscountCode(code);
      
      if (result.valid) {
        toast.success(result.message || 'Discount code applied!');
      } else {
        toast.error(result.message || 'Invalid discount code');
      }
      
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to validate discount code';
      toast.error(errorMessage);
      throw err;
    }
  }, []);

  useEffect(() => {
    const initializeData = async () => {
      setIsLoading(true);
      try {
        await Promise.all([fetchBalance(), fetchPackages()]);
      } finally {
        setIsLoading(false);
      }
    };

    initializeData();
  }, [fetchBalance, fetchPackages]);

  return {
    balance,
    packages,
    isLoading,
    error,
    fetchBalance,
    purchaseCredits,
    validateDiscountCode,
    refetch: () => Promise.all([fetchBalance(), fetchPackages()]),
  };
}
