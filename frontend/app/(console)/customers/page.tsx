import type { Metadata } from "next";

import { CustomersAnalytics } from "@/components/customers/CustomersAnalytics";

export const metadata: Metadata = { title: "Customers" };

export default function CustomersPage() {
  return <CustomersAnalytics />;
}
