"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Search,
  Clock,
  DollarSign,
  HandHeart,
  Package,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Flower2,
} from "lucide-react";
import { therapiesApi, packagesApi } from "@/lib/api/client";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type Therapy = {
  id: number;
  name: string;
  name_sanskrit?: string;
  description?: string;
  category?: string;
  default_duration_minutes?: number;
  default_price_cents?: number;
  benefits?: string[];
  contraindications?: string[];
  dosha_effect?: string;
  image_url?: string;
};

type PackageTherapyItem = {
  id: number;
  therapy_id: number;
  therapy?: Therapy;
  sort_order: number;
  notes?: string;
};

type ServicePackage = {
  id: number;
  name: string;
  description?: string;
  category?: string;
  total_duration_minutes?: number;
  total_price_cents?: number;
  includes_extras?: string[];
  panchakarma_days?: number;
  therapies?: PackageTherapyItem[];
};

const TABS = [
  { key: "therapies", label: "Therapies", icon: HandHeart },
  { key: "packages", label: "Packages", icon: Package },
  { key: "panchakarma", label: "Panchakarma Programs", icon: Sparkles },
] as const;

const THERAPY_CATEGORIES = [
  "All",
  "Massage",
  "Head Therapy",
  "Basti",
  "Steam",
  "Detox",
  "Exfoliating",
  "Facial",
  "Prenatal",
];

const CATEGORY_COLORS: Record<string, string> = {
  Massage: "bg-amber-100 text-amber-800",
  "Head Therapy": "bg-purple-100 text-purple-800",
  Basti: "bg-blue-100 text-blue-800",
  Steam: "bg-teal-100 text-teal-800",
  Detox: "bg-green-100 text-green-800",
  Exfoliating: "bg-pink-100 text-pink-800",
  Facial: "bg-rose-100 text-rose-800",
  Prenatal: "bg-violet-100 text-violet-800",
  Combination: "bg-amber-100 text-amber-800 border-amber-200",
  Pampering: "bg-yellow-50 text-yellow-800 border-yellow-300",
  Panchakarma: "bg-emerald-100 text-emerald-800 border-emerald-300",
};

function formatPrice(cents?: number) {
  if (!cents) return "";
  return `$${(cents / 100).toFixed(0)}`;
}

function formatDuration(minutes?: number) {
  if (!minutes) return "";
  if (minutes < 60) return `${minutes} min`;
  const hrs = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hrs}h ${mins}m` : `${hrs}h`;
}

// ── Therapy Card ────────────────────────────────────────────────────────────

function TherapyCard({ therapy }: { therapy: Therapy }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border rounded-xl bg-card overflow-hidden hover:shadow-md transition-shadow">
      <div
        className="p-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-sm">{therapy.name}</h3>
              {therapy.category && (
                <Badge
                  variant="outline"
                  className={cn(
                    "text-[10px] px-1.5 py-0",
                    CATEGORY_COLORS[therapy.category] || "bg-gray-100 text-gray-700"
                  )}
                >
                  {therapy.category}
                </Badge>
              )}
            </div>
            {therapy.name_sanskrit && (
              <p className="text-xs text-muted-foreground italic mb-2">
                {therapy.name_sanskrit}
              </p>
            )}
            <p className="text-xs text-muted-foreground line-clamp-2">
              {therapy.description}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1 shrink-0">
            {therapy.default_price_cents && (
              <span className="text-sm font-bold text-primary">
                {formatPrice(therapy.default_price_cents)}
              </span>
            )}
            {therapy.default_duration_minutes && (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="size-3" />
                {formatDuration(therapy.default_duration_minutes)}
              </span>
            )}
            {expanded ? (
              <ChevronUp className="size-3.5 text-muted-foreground mt-1" />
            ) : (
              <ChevronDown className="size-3.5 text-muted-foreground mt-1" />
            )}
          </div>
        </div>
      </div>
      {expanded && (
        <div className="px-4 pb-4 pt-0 border-t space-y-3">
          {therapy.dosha_effect && (
            <div className="flex items-center gap-2 pt-3">
              <span className="text-xs font-medium text-muted-foreground">Dosha Effect:</span>
              <Badge variant="outline" className="text-[10px] bg-orange-50 text-orange-700 border-orange-200">
                {therapy.dosha_effect}
              </Badge>
            </div>
          )}
          {therapy.benefits && therapy.benefits.length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">Benefits</p>
              <div className="flex flex-wrap gap-1">
                {therapy.benefits.map((b) => (
                  <Badge
                    key={b}
                    variant="outline"
                    className="text-[10px] bg-green-50 text-green-700 border-green-200"
                  >
                    {b}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          {therapy.contraindications && therapy.contraindications.length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">Contraindications</p>
              <div className="flex flex-wrap gap-1">
                {therapy.contraindications.map((c) => (
                  <Badge
                    key={c}
                    variant="outline"
                    className="text-[10px] bg-red-50 text-red-700 border-red-200"
                  >
                    {c}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Package Card ────────────────────────────────────────────────────────────

function PackageCard({ pkg }: { pkg: ServicePackage }) {
  const [expanded, setExpanded] = useState(false);
  const isPampering = pkg.category === "Pampering";

  return (
    <div
      className={cn(
        "border rounded-xl bg-card overflow-hidden hover:shadow-md transition-shadow",
        isPampering && "border-yellow-300 bg-yellow-50/30"
      )}
    >
      <div
        className="p-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              {isPampering && <Flower2 className="size-4 text-yellow-600 shrink-0" />}
              <h3 className="font-semibold text-sm">{pkg.name}</h3>
            </div>
            {pkg.category && (
              <Badge
                variant="outline"
                className={cn(
                  "text-[10px] px-1.5 py-0 mb-2",
                  CATEGORY_COLORS[pkg.category] || "bg-gray-100 text-gray-700"
                )}
              >
                {pkg.category}
              </Badge>
            )}
            <p className="text-xs text-muted-foreground line-clamp-2">
              {pkg.description}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1 shrink-0">
            {pkg.total_price_cents && (
              <span className="text-lg font-bold text-primary">
                {formatPrice(pkg.total_price_cents)}
              </span>
            )}
            {pkg.total_duration_minutes && (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="size-3" />
                {formatDuration(pkg.total_duration_minutes)}
              </span>
            )}
            {expanded ? (
              <ChevronUp className="size-3.5 text-muted-foreground mt-1" />
            ) : (
              <ChevronDown className="size-3.5 text-muted-foreground mt-1" />
            )}
          </div>
        </div>

        {/* Included therapies as pills */}
        {pkg.therapies && pkg.therapies.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {pkg.therapies.map((pt) => (
              <Badge
                key={pt.id}
                variant="outline"
                className="text-[10px] bg-primary/5 text-primary border-primary/20"
              >
                {pt.therapy?.name || `Therapy #${pt.therapy_id}`}
              </Badge>
            ))}
          </div>
        )}
      </div>

      {expanded && (
        <div className="px-4 pb-4 pt-0 border-t space-y-3">
          {pkg.includes_extras && pkg.includes_extras.length > 0 && (
            <div className="pt-3">
              <p className="text-xs font-medium text-muted-foreground mb-1.5">Includes</p>
              <div className="space-y-1">
                {pkg.includes_extras.map((extra) => (
                  <div key={extra} className="flex items-center gap-2 text-xs text-foreground">
                    <span className="text-green-600">&#10003;</span>
                    {extra}
                  </div>
                ))}
              </div>
            </div>
          )}
          {pkg.therapies && pkg.therapies.length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1.5">Therapies in this package</p>
              <div className="space-y-1.5">
                {pkg.therapies.map((pt) => (
                  <div
                    key={pt.id}
                    className="flex items-center justify-between text-xs border rounded-lg px-2.5 py-1.5 bg-muted/40"
                  >
                    <span className="font-medium">{pt.therapy?.name}</span>
                    <span className="text-muted-foreground">
                      {formatDuration(pt.therapy?.default_duration_minutes)}
                      {pt.therapy?.default_price_cents &&
                        ` / ${formatPrice(pt.therapy.default_price_cents)}`}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Panchakarma Card ────────────────────────────────────────────────────────

function PanchakarmaCard({ pkg }: { pkg: ServicePackage }) {
  return (
    <div className="border-2 border-emerald-300 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 overflow-hidden hover:shadow-lg transition-shadow">
      <div className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-bold text-sm">
                {pkg.panchakarma_days}
              </div>
              <div>
                <h3 className="font-semibold text-sm">{pkg.name}</h3>
                <p className="text-xs text-emerald-700">
                  {pkg.panchakarma_days}-day program
                </p>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
              {pkg.description}
            </p>
          </div>
          <div className="text-right shrink-0">
            {pkg.total_price_cents && (
              <span className="text-xl font-bold text-emerald-700">
                {formatPrice(pkg.total_price_cents)}
              </span>
            )}
            {pkg.total_duration_minutes && (
              <p className="text-xs text-emerald-600 mt-0.5">
                {formatDuration(pkg.total_duration_minutes)} total
              </p>
            )}
          </div>
        </div>

        {pkg.includes_extras && pkg.includes_extras.length > 0 && (
          <div className="mt-4 grid grid-cols-2 gap-1.5">
            {pkg.includes_extras.map((extra) => (
              <div
                key={extra}
                className="flex items-center gap-1.5 text-xs text-emerald-800"
              >
                <span className="text-emerald-600 font-bold">&#10003;</span>
                {extra}
              </div>
            ))}
          </div>
        )}

        <p className="text-[10px] text-muted-foreground mt-3 italic">
          * Herbal supplements cost is not included in the Panchakarma package
        </p>
      </div>
    </div>
  );
}

// ── Main Page ───────────────────────────────────────────────────────────────

export default function ServicesPage() {
  const [tab, setTab] = useState<"therapies" | "packages" | "panchakarma">(
    "therapies"
  );
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");

  const { data: therapies = [] } = useQuery<Therapy[]>({
    queryKey: ["therapies", search],
    queryFn: () =>
      therapiesApi
        .list(search ? { search } : undefined)
        .then((r) => r.data),
  });

  const { data: packages = [] } = useQuery<ServicePackage[]>({
    queryKey: ["packages"],
    queryFn: () => packagesApi.list().then((r) => r.data),
  });

  const comboPackages = packages.filter(
    (p) => p.category === "Combination" || p.category === "Pampering"
  );
  const panchakarmaPackages = packages.filter(
    (p) => p.category === "Panchakarma"
  );

  const filteredTherapies =
    categoryFilter === "All"
      ? therapies
      : therapies.filter((t) => t.category === categoryFilter);

  return (
    <div className="p-6 space-y-6 max-w-6xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Services</h1>
        <p className="text-sm text-muted-foreground">
          Ayurvedic therapies, wellness packages, and Panchakarma programs
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px",
              tab === key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            <Icon className="size-4" />
            {label}
            {key === "therapies" && (
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0 ml-1">
                {therapies.length}
              </Badge>
            )}
            {key === "packages" && (
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0 ml-1">
                {comboPackages.length}
              </Badge>
            )}
            {key === "panchakarma" && (
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0 ml-1">
                {panchakarmaPackages.length}
              </Badge>
            )}
          </button>
        ))}
      </div>

      {/* ── Therapies Tab ── */}
      {tab === "therapies" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
              <Input
                placeholder="Search therapies..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          {/* Category filter chips */}
          <div className="flex flex-wrap gap-1.5">
            {THERAPY_CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={cn(
                  "px-3 py-1 rounded-full text-xs font-medium transition-colors border",
                  categoryFilter === cat
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-card text-muted-foreground border-border hover:bg-muted"
                )}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {filteredTherapies.map((t) => (
              <TherapyCard key={t.id} therapy={t} />
            ))}
          </div>
          {filteredTherapies.length === 0 && (
            <p className="text-center text-sm text-muted-foreground py-12">
              No therapies found.
            </p>
          )}
        </div>
      )}

      {/* ── Packages Tab ── */}
      {tab === "packages" && (
        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2">
            {comboPackages.map((p) => (
              <PackageCard key={p.id} pkg={p} />
            ))}
          </div>
          {comboPackages.length === 0 && (
            <p className="text-center text-sm text-muted-foreground py-12">
              No packages found.
            </p>
          )}
        </div>
      )}

      {/* ── Panchakarma Tab ── */}
      {tab === "panchakarma" && (
        <div className="space-y-4">
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-2">
            <h2 className="font-semibold text-emerald-900 text-sm">
              Panchakarma — Ayurveda&apos;s Purification & Rejuvenation
            </h2>
            <p className="text-xs text-emerald-700 mt-1 leading-relaxed">
              A comprehensive detoxification program customized for each individual.
              Reduces inflammation, builds immunity, reverses stress effects, supports
              weight loss, mental clarity, emotional cleansing, and enhances overall
              wellness. Programs of 3+ days require a paid consultation before booking.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {panchakarmaPackages
              .sort((a, b) => (a.panchakarma_days || 0) - (b.panchakarma_days || 0))
              .map((p) => (
                <PanchakarmaCard key={p.id} pkg={p} />
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
