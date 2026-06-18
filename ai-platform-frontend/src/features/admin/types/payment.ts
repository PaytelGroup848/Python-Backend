export interface Payment {

  id: number;

  payment_reference: string;

  user_id: number;

  provider: string;

  payment_type: string;

  amount: number;

  currency: string;

  status: string;

  created_at: string;
}

export interface PaymentsResponse {

  count: number;

  payments: Payment[];
}