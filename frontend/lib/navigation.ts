import type { LucideIcon } from "lucide-react";
import {
  Boxes,
  Building2,
  LayoutDashboard,
  LineChart,
  Package,
  Settings,
  ShoppingCart,
  Sparkles,
  Truck,
  Users,
  Warehouse,
} from "lucide-react";

export type NavItem = {
  title: string;
  href: string;
  icon: LucideIcon;
  description: string;
};

export const mainNav: NavItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    description: "Executive overview",
  },
  {
    title: "Sales",
    href: "/sales",
    icon: ShoppingCart,
    description: "Revenue and order trends",
  },
  {
    title: "Customers",
    href: "/customers",
    icon: Users,
    description: "Customer performance",
  },
  {
    title: "Products",
    href: "/products",
    icon: Package,
    description: "Catalog and margin",
  },
  {
    title: "Shipping",
    href: "/shipping",
    icon: Truck,
    description: "Delivery operations",
  },
  {
    title: "Inventory",
    href: "/inventory",
    icon: Boxes,
    description: "Stock levels and alerts",
  },
  {
    title: "Warehouses",
    href: "/warehouses",
    icon: Warehouse,
    description: "Capacity and utilization",
  },
  {
    title: "Vendors",
    href: "/vendors",
    icon: Building2,
    description: "Supplier performance",
  },
  {
    title: "Forecasting",
    href: "/forecasting",
    icon: LineChart,
    description: "Demand projections",
  },
  {
    title: "AI Insights",
    href: "/ai-insights",
    icon: Sparkles,
    description: "Model-driven recommendations",
  },
];

export const utilityNav: NavItem[] = [
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
    description: "Workspace preferences",
  },
];

export const allNavItems: NavItem[] = [...mainNav, ...utilityNav];

export function getNavItemByPath(pathname: string): NavItem | undefined {
  return allNavItems.find(
    (item) => pathname === item.href || pathname.startsWith(`${item.href}/`),
  );
}

/** Brand mark icon used in the logo lockup. */
export const BrandIcon = Boxes;
