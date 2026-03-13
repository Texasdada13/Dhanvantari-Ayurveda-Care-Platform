"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, Plus, Trash2 } from "lucide-react";
import { recipesApi } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Dialog } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

type Recipe = {
  id: number;
  practitioner_id?: number | null;
  name: string;
  meal_type?: string;
  dosha_good_for?: string;
  dosha_avoid?: string;
  ingredients?: string;
  instructions?: string;
  notes?: string;
  is_tea?: boolean;
  visibility?: string;
  category?: string;
  rasa?: string;
  virya?: string;
  vipaka?: string;
};

const MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack", "Drink"];
const CATEGORIES = ["Yavagu (Gruel)", "Yusha (Soup)", "Kashaya (Decoction)", "Khichdi", "Sabzi", "Tea/Tisane", "Dessert", "Other"];
const DOSHAS = ["Vata", "Pitta", "Kapha", "Vata-Pitta", "Pitta-Kapha", "Vata-Kapha", "Tridoshic"];
const RASAS = ["Sweet", "Sour", "Salty", "Pungent", "Bitter", "Astringent"];

const EMPTY_FORM = {
  name: "", meal_type: "", dosha_good_for: "", dosha_avoid: "", ingredients: "",
  instructions: "", notes: "", is_tea: false, category: "", rasa: "", virya: "", vipaka: "",
  visibility: "practice",
};

export default function RecipesPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [mealType, setMealType] = useState("");
  const [showMine, setShowMine] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);

  const { data: recipes = [], isLoading } = useQuery<Recipe[]>({
    queryKey: ["recipes", search, mealType, showMine],
    queryFn: () =>
      recipesApi.list({ search: search || undefined, meal_type: mealType || undefined, mine: showMine || undefined }).then((r) => r.data),
  });

  const saveMutation = useMutation({
    mutationFn: () => {
      const payload = { ...form, is_tea: form.is_tea || false };
      if (editingId) return recipesApi.update(editingId, payload);
      return recipesApi.create(payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["recipes"] });
      setFormOpen(false);
      setEditingId(null);
      setForm(EMPTY_FORM);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => recipesApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["recipes"] }),
  });

  function openEdit(r: Recipe) {
    setForm({
      name: r.name, meal_type: r.meal_type || "", dosha_good_for: r.dosha_good_for || "",
      dosha_avoid: r.dosha_avoid || "", ingredients: r.ingredients || "", instructions: r.instructions || "",
      notes: r.notes || "", is_tea: r.is_tea || false, category: r.category || "",
      rasa: r.rasa || "", virya: r.virya || "", vipaka: r.vipaka || "",
      visibility: r.visibility || "community",
    });
    setEditingId(r.id);
    setFormOpen(true);
  }

  return (
    <div className="p-6 space-y-5 max-w-6xl">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Recipes Library</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {recipes.length} Ayurvedic recipes
          </p>
        </div>
        <Button size="sm" className="gap-1.5" onClick={() => { setForm(EMPTY_FORM); setEditingId(null); setFormOpen(true); }}>
          <Plus className="size-4" /> New Recipe
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input placeholder="Search recipes…" value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" />
        </div>
        <Select value={mealType} onChange={(e) => setMealType(e.target.value)} className="w-40">
          <option value="">All types</option>
          {MEAL_TYPES.map((m) => <option key={m} value={m}>{m}</option>)}
        </Select>
        <button
          onClick={() => setShowMine(!showMine)}
          className={cn(
            "text-sm px-3 py-1.5 rounded-lg transition-colors border",
            showMine ? "bg-primary text-primary-foreground border-primary" : "text-muted-foreground hover:text-foreground"
          )}
        >
          My Recipes
        </button>
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
                  {r.practitioner_id && <Badge variant="default" className="text-xs">Mine</Badge>}
                </div>
              </div>

              {r.dosha_good_for && <p className="text-xs text-emerald-700">Good for: {r.dosha_good_for}</p>}
              {r.dosha_avoid && <p className="text-xs text-amber-700">Avoid: {r.dosha_avoid}</p>}
              {r.category && <p className="text-xs text-muted-foreground">Category: {r.category}</p>}

              {r.rasa && (
                <div className="flex gap-1 flex-wrap">
                  {r.rasa.split(",").map((t) => (
                    <span key={t.trim()} className="text-[10px] bg-muted px-1.5 py-0.5 rounded">{t.trim()}</span>
                  ))}
                </div>
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
                  {(r.virya || r.vipaka) && (
                    <div className="flex gap-4">
                      {r.virya && <span>Virya: <strong>{r.virya}</strong></span>}
                      {r.vipaka && <span>Vipaka: <strong>{r.vipaka}</strong></span>}
                    </div>
                  )}
                  {r.practitioner_id && (
                    <div className="flex gap-2 pt-1">
                      <Button size="sm" variant="outline" onClick={(e) => { e.stopPropagation(); openEdit(r); }}>Edit</Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-destructive hover:text-destructive"
                        onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(r.id); }}
                      >
                        <Trash2 className="size-3.5" />
                      </Button>
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

      {/* Create / Edit Dialog */}
      <Dialog open={formOpen} onClose={() => { setFormOpen(false); setEditingId(null); }} title={editingId ? "Edit Recipe" : "New Recipe"}>
        <form
          onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(); }}
          className="space-y-4 max-h-[70vh] overflow-y-auto pr-1"
        >
          <div className="space-y-1.5">
            <Label>Name *</Label>
            <Input required value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="e.g. Tridoshic Kitchari" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Meal Type</Label>
              <Select value={form.meal_type} onChange={(e) => setForm((f) => ({ ...f, meal_type: e.target.value }))}>
                <option value="">Select…</option>
                {MEAL_TYPES.map((m) => <option key={m} value={m}>{m}</option>)}
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Category</Label>
              <Select value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}>
                <option value="">Select…</option>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Good for Dosha</Label>
              <Select value={form.dosha_good_for} onChange={(e) => setForm((f) => ({ ...f, dosha_good_for: e.target.value }))}>
                <option value="">Select…</option>
                {DOSHAS.map((d) => <option key={d} value={d}>{d}</option>)}
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Avoid for Dosha</Label>
              <Select value={form.dosha_avoid} onChange={(e) => setForm((f) => ({ ...f, dosha_avoid: e.target.value }))}>
                <option value="">Select…</option>
                {DOSHAS.map((d) => <option key={d} value={d}>{d}</option>)}
              </Select>
            </div>
          </div>

          {/* Ayurvedic Properties */}
          <div className="border-t pt-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Ayurvedic Properties</p>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1.5">
                <Label>Rasa (Taste)</Label>
                <Select value={form.rasa} onChange={(e) => setForm((f) => ({ ...f, rasa: e.target.value }))}>
                  <option value="">Select…</option>
                  {RASAS.map((r) => <option key={r} value={r}>{r}</option>)}
                  <option value="Sweet, Sour">Sweet, Sour</option>
                  <option value="Sweet, Bitter">Sweet, Bitter</option>
                  <option value="Pungent, Bitter">Pungent, Bitter</option>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Virya</Label>
                <Select value={form.virya} onChange={(e) => setForm((f) => ({ ...f, virya: e.target.value }))}>
                  <option value="">Select…</option>
                  <option value="Heating">Heating (Ushna)</option>
                  <option value="Cooling">Cooling (Sheeta)</option>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Vipaka</Label>
                <Select value={form.vipaka} onChange={(e) => setForm((f) => ({ ...f, vipaka: e.target.value }))}>
                  <option value="">Select…</option>
                  <option value="Sweet">Sweet (Madhura)</option>
                  <option value="Sour">Sour (Amla)</option>
                  <option value="Pungent">Pungent (Katu)</option>
                </Select>
              </div>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label>Ingredients</Label>
            <Textarea rows={3} value={form.ingredients} onChange={(e) => setForm((f) => ({ ...f, ingredients: e.target.value }))} placeholder="List ingredients, one per line…" />
          </div>
          <div className="space-y-1.5">
            <Label>Instructions</Label>
            <Textarea rows={4} value={form.instructions} onChange={(e) => setForm((f) => ({ ...f, instructions: e.target.value }))} placeholder="Step-by-step cooking instructions…" />
          </div>
          <div className="space-y-1.5">
            <Label>Vaidya Notes</Label>
            <Textarea rows={2} value={form.notes} onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))} placeholder="Clinical notes, contraindications…" />
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_tea}
                onChange={(e) => setForm((f) => ({ ...f, is_tea: e.target.checked }))}
                className="rounded border"
              />
              Herbal Tea / Tisane
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="outline" onClick={() => { setFormOpen(false); setEditingId(null); }}>Cancel</Button>
            <Button type="submit" disabled={saveMutation.isPending}>
              {saveMutation.isPending ? "Saving…" : editingId ? "Update Recipe" : "Create Recipe"}
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
}
