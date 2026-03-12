"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { supplementsApi } from "@/lib/api/client";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

type Supplement = {
  id: number;
  name: string;
  name_sanskrit?: string;
  category?: string;
  purpose?: string;
  dosha_effect?: string;
  typical_dose?: string;
  cautions?: string;
};

const CATEGORIES = ["Adaptogenic", "Rejuvenative", "Nervine", "Digestive", "Immunomodulator", "Nutritive", "Detoxifying", "Anti-inflammatory"];

export default function SupplementsPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [expanded, setExpanded] = useState<number | null>(null);

  const { data: supplements = [], isLoading } = useQuery<Supplement[]>({
    queryKey: ["supplements", search, category],
    queryFn: () =>
      supplementsApi
        .list({ search: search || undefined, category: category || undefined })
        .then((r) => r.data),
  });

  return (
    <div className="p-6 space-y-5 max-w-6xl">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Supplements Library</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          {supplements.length} classical Ayurvedic herbs &amp; supplements
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search supplements…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={category} onChange={(e) => setCategory(e.target.value)} className="w-48">
          <option value="">All categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </Select>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="text-sm text-muted-foreground py-12 text-center">Loading…</div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {supplements.map((s) => (
            <div
              key={s.id}
              className="rounded-xl border bg-card p-4 space-y-2 cursor-pointer hover:border-primary/40 transition-colors"
              onClick={() => setExpanded(expanded === s.id ? null : s.id)}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="font-medium text-sm">{s.name}</p>
                  {s.name_sanskrit && (
                    <p className="text-xs text-muted-foreground italic">{s.name_sanskrit}</p>
                  )}
                </div>
                {s.category && (
                  <Badge variant="secondary" className="shrink-0 text-xs">{s.category}</Badge>
                )}
              </div>

              {s.dosha_effect && (
                <p className="text-xs text-muted-foreground">{s.dosha_effect}</p>
              )}

              {expanded === s.id && (
                <div className="pt-2 border-t space-y-2 text-xs text-muted-foreground">
                  {s.purpose && (
                    <div>
                      <p className="font-medium text-foreground mb-0.5">Purpose</p>
                      <p>{s.purpose}</p>
                    </div>
                  )}
                  {s.typical_dose && (
                    <div>
                      <p className="font-medium text-foreground mb-0.5">Typical Dose</p>
                      <p>{s.typical_dose}</p>
                    </div>
                  )}
                  {s.cautions && (
                    <div>
                      <p className="font-medium text-amber-600 mb-0.5">Cautions</p>
                      <p className="text-amber-700">{s.cautions}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          {supplements.length === 0 && (
            <div className="col-span-full py-12 text-center text-sm text-muted-foreground">
              No supplements match your search.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
