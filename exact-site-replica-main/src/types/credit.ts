export interface CreditPackage {
  id: number;
  name: string;
  credits: number;
  price: number;
  description?: string;
  bonus_credits: number;
  is_active: boolean;
}

export interface CreditBalance {
  user_id: number;
  current_credits: number;
  total_purchased: number;
  total_used: number;
  total_bonus: number;
  effective_rate: number;
  last_updated: string;
}

export interface CreditTransaction {
  id: number;
  user_id: number;
  transaction_type: 'purchase' | 'usage' | 'refund' | 'bonus';
  amount: number;
  balance_after: number;
  description?: string;
  reference_id?: string;
  created_at: string;
}

export interface CreditPurchase {
  package_id: number;
  payment_method_id: string;
  amount: number;
  currency: string;
}

export interface CreditPurchaseResponse {
  transaction_id: string;
  credits_added: number;
  bonus_credits: number;
  total_credits: number;
  new_balance: number;
  amount_charged: number;
  currency: string;
}

export interface CreditUsage {
  amount: number;
  description?: string;
  reference_id?: string;
}

export interface CreditUsageResponse {
  transaction_id: string;
  credits_used: number;
  new_balance: number;
  description: string;
}

export interface CreditTransactionHistory {
  transactions: CreditTransaction[];
  total_count: number;
  page: number;
  per_page: number;
}

export interface CreditStats {
  current_balance: number;
  total_purchased: number;
  total_used: number;
  total_bonus: number;
  effective_rate_per_credit: number;
  last_purchase_date?: string;
  last_usage_date?: string;
  usage_this_month: number;
  purchases_this_month: number;
}
