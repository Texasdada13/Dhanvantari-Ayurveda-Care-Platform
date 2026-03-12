"use client";

import { useState } from "react";
import { use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ArrowLeft, Plus, Trash2, ExternalLink, Save } from "lucide-react";
import { patientsApi, plansApi, checkinsApi, followupsApi, supplementsApi, recipesApi } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Dialog } from "@/components/ui/dialog";
import { Badge, DoshaBadge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type Tab = "overview" | "plan" | "checkins" | "followups";

const PORTAL_BASE = process.env.NEXT_PUBLIC_API_URL?.replace(":8747", ":3747") ?? "http://localhost:3747";

export default function PatientDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const patientId = parseInt(id);
  const router = useRouter();
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>("overview");

  // ── Data ──────────────────────────────────────────────────────────────────
  const { data: patient, isLoading } = useQuery({
    queryKey: ["patient", patientId],
    queryFn: () => patientsApi.get(patientId).then((r) => r.data),
  });

  const { data: plan } = useQuery({
    queryKey: ["plan", patientId],
    queryFn: () => plansApi.get(patientId).then((r) => r.data),
    enabled: tab === "plan",
    retry: false,
  });

  const { data: checkins = [] } = useQuery({
    queryKey: ["checkins", patientId],
    queryFn: () => checkinsApi.list(patientId).then((r) => r.data),
    enabled: tab === "checkins",
  });

  const { data: followups = [] } = useQuery({
    queryKey: ["patient-followups", patientId],
    queryFn: () => followupsApi.list({ patient_id: patientId }).then((r) => r.data),
    enabled: tab === "followups",
  });

  // ── Plan editor state ─────────────────────────────────────────────────────
  const [planEdits, setPlanEdits] = useState<Record<string, string>>({});
  const [addSupplementOpen, setAddSupplementOpen] = useState(false);
  const [addRecipeOpen, setAddRecipeOpen] = useState(false);
  const [suppSearch, setSuppSearch] = useState("");
  const [recipeSearch, setRecipeSearch] = useState("");
  const [newFollowupOpen, setNewFollowupOpen] = useState(false);
  const [followupForm, setFollowupForm] = useState({ scheduled_date: "", reason: "", notes: "" });

  const { data: suppLib = [] } = useQuery({
    queryKey: ["supplements-lib", suppSearch],
    queryFn: () => supplementsApi.list({ search: suppSearch || undefined }).then((r) => r.data),
    enabled: addSupplementOpen,
  });

  const { data: recipeLib = [] } = useQuery({
    queryKey: ["recipes-lib", recipeSearch],
    queryFn: () => recipesApi.list({ search: recipeSearch || undefined }).then((r) => r.data),
    enabled: addRecipeOpen,
  });

  // ── Mutations ─────────────────────────────────────────────────────────────
  const createPlanMutation = useMutation({
    mutationFn: () => plansApi.create(patientId, { title: "Initial Protocol" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["plan", patientId] }),
  });

  const updatePlanMutation = useMutation({
    mutationFn: (data: Record<string, string>) => plansApi.update(patientId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["plan", patientId] });
      setPlanEdits({});
    },
  });

  const addSupplementMutation = useMutation({
    mutationFn: (supplementId: number) =>
      plansApi.addSupplement(patientId, { supplement_id: supplementId }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["plan", patientId] });
      setAddSupplementOpen(false);
    },
  });

  const removeSupplementMutation = useMutation({
    mutationFn: (psId: number) => plansApi.removeSupplement(psId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["plan", patientId] }),
  });

  const addRecipeMutation = useMutation({
    mutationFn: (recipeId: number) =>
      plansApi.addRecipe(patientId, { recipe_id: recipeId }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["plan", patientId] });
      setAddRecipeOpen(false);
    },
  });

  const removeRecipeMutation = useMutation({
    mutationFn: (prId: number) => plansApi.removeRecipe(prId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["plan", patientId] }),
  });

  const addFollowupMutation = useMutation({
    mutationFn: () => followupsApi.create({ ...followupForm, patient_id: patientId }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["patient-followups", patientId] });
      qc.invalidateQueries({ queryKey: ["followups", "upcoming"] });
      setNewFollowupOpen(false);
      setFollowupForm({ scheduled_date: "", reason: "", notes: "" });
    },
  });

  const completeFollowupMutation = useMutation({
    mutationFn: (id: number) => followupsApi.update(id, { completed: true }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["patient-followups", patientId] }),
  });

  if (isLoading || !patient) {
    return <div className="p-6 text-sm text-muted-foreground">Loading…</div>;
  }

  const TABS: { id: Tab; label: string }[] = [
    { id: "overview", label: "Overview" },
    { id: "plan", label: "Care Plan" },
    { id: "checkins", label: "Check-ins" },
    { id: "followups", label: "Follow-ups" },
  ];

  const planFields = [
    { key: "foods_to_include", label: "Foods to Include" },
    { key: "foods_to_avoid", label: "Foods to Avoid" },
    { key: "lifestyle_notes", label: "Lifestyle" },
    { key: "breathing_notes", label: "Breathing / Pranayama" },
    { key: "nasal_care_notes", label: "Nasal Care (Nasya)" },
    { key: "followup_notes", label: "Follow-up Notes" },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <div className="flex items-center gap-3 px-6 py-4 border-b bg-card">
        <button
          onClick={() => router.push("/patients")}
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="size-4" />
        </button>
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="w-9 h-9 rounded-full bg-primary/15 flex items-center justify-center text-primary text-sm font-semibold shrink-0">
            {patient.full_name?.split(" ").map((n: string) => n[0]).join("").slice(0, 2).toUpperCase()}
          </div>
          <div className="min-w-0">
            <h1 className="font-semibold truncate">{patient.full_name}</h1>
            <div className="flex items-center gap-2 flex-wrap">
              {patient.dob && (
                <span className="text-xs text-muted-foreground">
                  {Math.floor((Date.now() - new Date(patient.dob).getTime()) / (365.25 * 86400000))}y
                  {patient.sex ? ` · ${patient.sex}` : ""}
                </span>
              )}
              <DoshaBadge dosha={patient.dosha_primary} />
            </div>
          </div>
        </div>
        {patient.portal_token && (
          <a
            href={`${PORTAL_BASE}/portal/${patient.portal_token}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button variant="outline" size="sm" className="gap-1.5 shrink-0">
              <ExternalLink className="size-3.5" />
              Portal
            </Button>
          </a>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-0 border-b bg-card px-6 shrink-0">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              "px-4 py-3 text-sm font-medium border-b-2 transition-colors",
              tab === t.id
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* ── Overview ────────────────────────────────────────────────── */}
        {tab === "overview" && (
          <div className="max-w-3xl space-y-6">
            <section className="rounded-xl border bg-card p-5 space-y-4">
              <h2 className="font-medium text-sm">Demographics</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                {[
                  { label: "Email", value: patient.email },
                  { label: "Phone", value: patient.phone },
                  { label: "Location", value: patient.location },
                  { label: "Occupation", value: patient.occupation },
                  { label: "Weight", value: patient.weight_lbs ? `${patient.weight_lbs} lbs` : null },
                  { label: "Height", value: patient.height_in ? `${Math.floor(patient.height_in / 12)}′${Math.round(patient.height_in % 12)}″` : null },
                  { label: "Diet Pattern", value: patient.diet_pattern },
                  { label: "Stress Level", value: patient.stress_level },
                ].map(({ label, value }) => (
                  <div key={label}>
                    <p className="text-xs text-muted-foreground">{label}</p>
                    <p className="mt-0.5">{value ?? "—"}</p>
                  </div>
                ))}
              </div>
            </section>

            {patient.health_profile && (
              <section className="rounded-xl border bg-card p-5 space-y-4">
                <h2 className="font-medium text-sm">Ayurvedic Assessment</h2>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {[
                    { label: "Primary Dosha", value: patient.health_profile.dosha_primary },
                    { label: "Secondary Dosha", value: patient.health_profile.dosha_secondary },
                    { label: "Dosha Imbalances", value: patient.health_profile.dosha_imbalances },
                    { label: "Agni", value: patient.health_profile.agni_assessment },
                    { label: "Ama", value: patient.health_profile.ama_assessment },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <p className="text-xs text-muted-foreground">{label}</p>
                      <p className="mt-0.5">{value ?? "—"}</p>
                    </div>
                  ))}
                </div>
                {patient.health_profile.chief_complaints && (
                  <div>
                    <p className="text-xs text-muted-foreground">Chief Complaints</p>
                    <p className="mt-0.5 text-sm whitespace-pre-wrap">{patient.health_profile.chief_complaints}</p>
                  </div>
                )}
              </section>
            )}
          </div>
        )}

        {/* ── Care Plan ────────────────────────────────────────────────── */}
        {tab === "plan" && (
          <div className="max-w-3xl space-y-5">
            {!plan ? (
              <div className="rounded-xl border bg-card p-8 text-center space-y-3">
                <p className="text-muted-foreground text-sm">No active care plan.</p>
                <Button onClick={() => createPlanMutation.mutate()} disabled={createPlanMutation.isPending}>
                  {createPlanMutation.isPending ? "Creating…" : "Create Initial Protocol"}
                </Button>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="font-medium">{plan.title}</h2>
                  <Button
                    size="sm"
                    onClick={() => updatePlanMutation.mutate(planEdits)}
                    disabled={Object.keys(planEdits).length === 0 || updatePlanMutation.isPending}
                    className="gap-1.5"
                  >
                    <Save className="size-3.5" />
                    {updatePlanMutation.isPending ? "Saving…" : "Save Changes"}
                  </Button>
                </div>

                {/* Plan text fields */}
                <div className="rounded-xl border bg-card p-5 space-y-4">
                  <div className="grid gap-4">
                    {planFields.map(({ key, label }) => (
                      <div key={key} className="space-y-1.5">
                        <Label>{label}</Label>
                        <Textarea
                          rows={2}
                          value={planEdits[key] ?? plan[key] ?? ""}
                          onChange={(e) => setPlanEdits((prev) => ({ ...prev, [key]: e.target.value }))}
                          placeholder={`Enter ${label.toLowerCase()}…`}
                        />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Supplements */}
                <div className="rounded-xl border bg-card p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium text-sm">Supplements ({plan.supplements?.length ?? 0})</h3>
                    <Button size="sm" variant="outline" onClick={() => setAddSupplementOpen(true)} className="gap-1.5">
                      <Plus className="size-3.5" /> Add
                    </Button>
                  </div>
                  {plan.supplements?.length === 0 && (
                    <p className="text-sm text-muted-foreground">No supplements added yet.</p>
                  )}
                  <div className="space-y-2">
                    {plan.supplements?.map((s: { id: number; name: string; name_sanskrit?: string; dose?: string; timing?: string }) => (
                      <div key={s.id} className="flex items-center gap-3 rounded-lg border px-3 py-2.5 text-sm">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{s.name}</p>
                          {s.name_sanskrit && <p className="text-xs text-muted-foreground italic">{s.name_sanskrit}</p>}
                          {(s.dose || s.timing) && (
                            <p className="text-xs text-muted-foreground">{[s.dose, s.timing].filter(Boolean).join(" · ")}</p>
                          )}
                        </div>
                        <button
                          onClick={() => removeSupplementMutation.mutate(s.id)}
                          className="text-muted-foreground hover:text-destructive transition-colors"
                        >
                          <Trash2 className="size-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recipes */}
                <div className="rounded-xl border bg-card p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium text-sm">Recipes ({plan.recipes?.length ?? 0})</h3>
                    <Button size="sm" variant="outline" onClick={() => setAddRecipeOpen(true)} className="gap-1.5">
                      <Plus className="size-3.5" /> Add
                    </Button>
                  </div>
                  {plan.recipes?.length === 0 && (
                    <p className="text-sm text-muted-foreground">No recipes added yet.</p>
                  )}
                  <div className="space-y-2">
                    {plan.recipes?.map((r: { id: number; name: string; meal_type?: string; meal_slot?: string }) => (
                      <div key={r.id} className="flex items-center gap-3 rounded-lg border px-3 py-2.5 text-sm">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{r.name}</p>
                          {(r.meal_type || r.meal_slot) && (
                            <p className="text-xs text-muted-foreground">{[r.meal_type, r.meal_slot].filter(Boolean).join(" · ")}</p>
                          )}
                        </div>
                        <button
                          onClick={() => removeRecipeMutation.mutate(r.id)}
                          className="text-muted-foreground hover:text-destructive transition-colors"
                        >
                          <Trash2 className="size-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* ── Check-ins ────────────────────────────────────────────────── */}
        {tab === "checkins" && (
          <div className="max-w-4xl space-y-4">
            <h2 className="font-medium text-sm text-muted-foreground">Last 30 check-ins</h2>
            {checkins.length === 0 ? (
              <div className="rounded-xl border bg-card p-8 text-center text-sm text-muted-foreground">
                No check-ins yet. Share the portal link with the patient.
              </div>
            ) : (
              <div className="rounded-xl border bg-card overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/40">
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Habits</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Digestion</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Energy</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Avg Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {checkins.map((c: {
                      id: number;
                      date: string;
                      habit_completion_pct: number;
                      digestion_score?: number;
                      energy_score?: number;
                      avg_symptom_score?: number;
                    }) => (
                      <tr key={c.id}>
                        <td className="px-4 py-3 text-muted-foreground">
                          {new Date(c.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                              <div
                                className="h-full rounded-full bg-emerald-500"
                                style={{ width: `${c.habit_completion_pct}%` }}
                              />
                            </div>
                            <span className="text-xs text-muted-foreground">{Math.round(c.habit_completion_pct)}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          {c.digestion_score ? (
                            <span className={cn("font-medium", c.digestion_score >= 4 ? "text-emerald-600" : c.digestion_score <= 2 ? "text-red-500" : "")}>
                              {c.digestion_score}/5
                            </span>
                          ) : "—"}
                        </td>
                        <td className="px-4 py-3">
                          {c.energy_score ? (
                            <span className={cn("font-medium", c.energy_score >= 4 ? "text-emerald-600" : c.energy_score <= 2 ? "text-red-500" : "")}>
                              {c.energy_score}/5
                            </span>
                          ) : "—"}
                        </td>
                        <td className="px-4 py-3">
                          {c.avg_symptom_score != null ? (
                            <Badge variant={c.avg_symptom_score >= 4 ? "success" : c.avg_symptom_score <= 2 ? "destructive" : "secondary"}>
                              {c.avg_symptom_score.toFixed(1)}
                            </Badge>
                          ) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ── Follow-ups ────────────────────────────────────────────────── */}
        {tab === "followups" && (
          <div className="max-w-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-medium text-sm text-muted-foreground">Follow-ups</h2>
              <Button size="sm" onClick={() => setNewFollowupOpen(true)} className="gap-1.5">
                <Plus className="size-3.5" /> Schedule
              </Button>
            </div>
            {followups.length === 0 ? (
              <div className="rounded-xl border bg-card p-8 text-center text-sm text-muted-foreground">
                No follow-ups scheduled.
              </div>
            ) : (
              <div className="space-y-2">
                {followups.map((f: { id: number; scheduled_date: string; reason?: string; notes?: string; completed_at?: string }) => (
                  <div key={f.id} className="rounded-xl border bg-card p-4 flex items-start gap-4">
                    <div className={cn("w-2 h-2 rounded-full mt-1.5 shrink-0", f.completed_at ? "bg-muted-foreground" : "bg-primary")} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">
                        {new Date(f.scheduled_date).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" })}
                      </p>
                      {f.reason && <p className="text-sm text-muted-foreground">{f.reason}</p>}
                      {f.notes && <p className="text-xs text-muted-foreground mt-1">{f.notes}</p>}
                    </div>
                    {!f.completed_at && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => completeFollowupMutation.mutate(f.id)}
                        disabled={completeFollowupMutation.isPending}
                      >
                        Complete
                      </Button>
                    )}
                    {f.completed_at && (
                      <Badge variant="success">Done</Badge>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Dialogs ─────────────────────────────────────────────────────── */}

      {/* Add Supplement */}
      <Dialog open={addSupplementOpen} onClose={() => setAddSupplementOpen(false)} title="Add Supplement" className="max-w-lg">
        <div className="space-y-3">
          <Input placeholder="Search supplements…" value={suppSearch} onChange={(e) => setSuppSearch(e.target.value)} />
          <div className="max-h-72 overflow-y-auto space-y-1.5 -mx-1 px-1">
            {suppLib.map((s: { id: number; name: string; name_sanskrit?: string; dosha_effect?: string; typical_dose?: string }) => (
              <button
                key={s.id}
                onClick={() => addSupplementMutation.mutate(s.id)}
                disabled={addSupplementMutation.isPending}
                className="w-full text-left rounded-lg border px-3 py-2.5 hover:bg-muted/50 transition-colors"
              >
                <p className="text-sm font-medium">{s.name}</p>
                <p className="text-xs text-muted-foreground">
                  {[s.name_sanskrit, s.dosha_effect, s.typical_dose].filter(Boolean).join(" · ")}
                </p>
              </button>
            ))}
          </div>
        </div>
      </Dialog>

      {/* Add Recipe */}
      <Dialog open={addRecipeOpen} onClose={() => setAddRecipeOpen(false)} title="Add Recipe" className="max-w-lg">
        <div className="space-y-3">
          <Input placeholder="Search recipes…" value={recipeSearch} onChange={(e) => setRecipeSearch(e.target.value)} />
          <div className="max-h-72 overflow-y-auto space-y-1.5 -mx-1 px-1">
            {recipeLib.map((r: { id: number; name: string; meal_type?: string; dosha_good_for?: string }) => (
              <button
                key={r.id}
                onClick={() => addRecipeMutation.mutate(r.id)}
                disabled={addRecipeMutation.isPending}
                className="w-full text-left rounded-lg border px-3 py-2.5 hover:bg-muted/50 transition-colors"
              >
                <p className="text-sm font-medium">{r.name}</p>
                <p className="text-xs text-muted-foreground">
                  {[r.meal_type, r.dosha_good_for ? `Good for ${r.dosha_good_for}` : null].filter(Boolean).join(" · ")}
                </p>
              </button>
            ))}
          </div>
        </div>
      </Dialog>

      {/* New Follow-up */}
      <Dialog open={newFollowupOpen} onClose={() => setNewFollowupOpen(false)} title="Schedule Follow-up">
        <form
          onSubmit={(e) => { e.preventDefault(); addFollowupMutation.mutate(); }}
          className="space-y-4"
        >
          <div className="space-y-1.5">
            <Label>Date *</Label>
            <Input
              type="date"
              required
              value={followupForm.scheduled_date}
              onChange={(e) => setFollowupForm((f) => ({ ...f, scheduled_date: e.target.value }))}
            />
          </div>
          <div className="space-y-1.5">
            <Label>Reason</Label>
            <Input
              placeholder="e.g. 4-week follow-up, lab review"
              value={followupForm.reason}
              onChange={(e) => setFollowupForm((f) => ({ ...f, reason: e.target.value }))}
            />
          </div>
          <div className="space-y-1.5">
            <Label>Notes</Label>
            <Textarea
              rows={2}
              placeholder="Any notes for this appointment…"
              value={followupForm.notes}
              onChange={(e) => setFollowupForm((f) => ({ ...f, notes: e.target.value }))}
            />
          </div>
          <div className="flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={() => setNewFollowupOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={addFollowupMutation.isPending}>
              {addFollowupMutation.isPending ? "Scheduling…" : "Schedule"}
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
}
