"use client";

import { cn } from "@/lib/utils";

type BadgeVariant = "default" | "secondary" | "success" | "warning" | "destructive" | "outline" | "vata" | "pitta" | "kapha";

const variants: Record<BadgeVariant, string> = {
  default:     "bg-primary/15 text-primary border-primary/20",
  secondary:   "bg-secondary text-secondary-foreground border-border",
  success:     "bg-emerald-100 text-emerald-700 border-emerald-200",
  warning:     "bg-amber-100 text-amber-700 border-amber-200",
  destructive: "bg-destructive/10 text-destructive border-destructive/20",
  outline:     "bg-transparent text-foreground border-border",
  vata:        "bg-sky-100 text-sky-700 border-sky-200",
  pitta:       "bg-orange-100 text-orange-700 border-orange-200",
  kapha:       "bg-emerald-100 text-emerald-700 border-emerald-200",
};

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

export function DoshaBadge({ dosha }: { dosha: string | null | undefined }) {
  if (!dosha) return null;
  const lower = dosha.toLowerCase();
  const variant = lower.includes("vata")
    ? "vata"
    : lower.includes("pitta")
    ? "pitta"
    : lower.includes("kapha")
    ? "kapha"
    : "default";
  return <Badge variant={variant}>{dosha}</Badge>;
}
