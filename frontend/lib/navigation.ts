import type { LucideIcon } from "lucide-react";
import {
  Boxes,
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
    icon: Warehouse,
    description: "Stock and warehouses",
  },
  {
    title: "AI Insights",
    href: "/ai-insights",
    icon: Sparkles,
    description: "Model-driven recommendations",
  },
  {
    title: "Forecasting",
    href: "/forecasting",
    icon: LineChart,
    description: "Demand projections",
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
