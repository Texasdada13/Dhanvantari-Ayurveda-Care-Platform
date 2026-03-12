"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { recipesApi } from "@/lib/api/client";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

type Recipe = {
  id: number;
  name: string;
  meal_type?: string;
  dosha_good_for?: string;
  dosha_avoid?: string;
  ingredients?: string;
  instructions?: string;
  notes?: string;
  is_tea?: boolean;
};

const MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack", "Drink"];

export default function RecipesPage() {
  const [search, setSearch] = useState("");
  const [mealType, setMealType] = useState("");
  const [expanded, setExpanded] = useState<number | null>(null);

  const { data: recipes = [], isLoading } = useQuery<Recipe[]>({
    queryKey: ["recipes", search, mealType],
    queryFn: () =>
      recipesApi
        .list({ search: search || undefined, meal_type: mealType || undefined })
        .then((r) => r.data),
  });

  return (
    <div className="p-6 space-y-5 max-w-6xl">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Recipes Library</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          {recipes.length} classical Ayurvedic recipes
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search recipes…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={mealType} onChange={(e) => setMealType(e.target.value)} className="w-40">
          <option value="">All types</option>
          {MEAL_TYPES.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </Select>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="text-sm text-muted-foreground py-12 text-center">Loading…</div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {recipes.map((r) => (
            <div
              key={r.id}
              className="rounded-xl border bg-card p-4 space-y-2 cursor-pointer hover:border-primary/40 transition-colors"
              onClick={() => setExpanded(expanded === r.id ? null : r.id)}
            >
              <div className="flex items-start justify-between gap-2">
                <p className="font-medium text-sm">{r.name}</p>
                <div className="flex gap-1.5 shrink-0 flex-wrap justify-end">
                  {r.meal_type && <Badge variant="secondary" className="text-xs">{r.meal_type}</Badge>}
                  {r.is_tea && <Badge variant="default" className="text-xs">Tea</Badge>}
                </div>
              </div>

              {r.dosha_good_for && (
                <p className="text-xs text-emerald-700">
                  Good for: {r.dosha_good_for}
                </p>
              )}
              {r.dosha_avoid && (
                <p className="text-xs text-amber-700">
                  Avoid: {r.dosha_avoid}
                </p>
              )}

              {expanded === r.id && (
                <div className="pt-2 border-t space-y-2 text-xs text-muted-foreground">
                  {r.ingredients && (
                    <div>
                      <p className="font-medium text-foreground mb-0.5">Ingredients</p>
                      <p>{r.ingredients}</p>
                    </div>
                  )}
                  {r.instructions && (
                    <div>
                      <p className="font-medium text-foreground mb-0.5">Instructions</p>
                      <p className="whitespace-pre-line">{r.instructions}</p>
                    </div>
                  )}
                  {r.notes && (
                    <div>
                      <p className="font-medium text-primary mb-0.5">Vaidya Notes</p>
                      <p className="text-foreground/70 italic">{r.notes}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          {recipes.length === 0 && (
            <div className="col-span-full py-12 text-center text-sm text-muted-foreground">
              No recipes match your search.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
