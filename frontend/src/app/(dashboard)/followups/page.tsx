"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Check } from "lucide-react";
import { followupsApi, patientsApi } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Dialog } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type FollowUp = {
  id: number;
  patient_name?: string;
  patient_id: number;
  scheduled_date: string;
  reason?: string;
  notes?: string;
  completed_at?: string;
};

type Patient = { id: number; full_name: string };

export default function FollowupsPage() {
  const qc = useQueryClient();
  const [showCompleted, setShowCompleted] = useState(false);
  const [addOpen, setAddOpen] = useState(false);
  const [form, setForm] = useState({ patient_id: "", scheduled_date: "", reason: "", notes: "" });

  const { data: followups = [], isLoading } = useQuery<FollowUp[]>({
    queryKey: ["followups", showCompleted],
    queryFn: () => followupsApi.list({ completed: showCompleted || undefined }).then((r) => r.data),
  });

  const { data: patients = [] } = useQuery<Patient[]>({
    queryKey: ["patients"],
    queryFn: () => patientsApi.list().then((r) => r.data),
    enabled: addOpen,
  });

  const addMutation = useMutation({
    mutationFn: () =>
      followupsApi.create({
        patient_id: parseInt(form.patient_id),
        scheduled_date: form.scheduled_date,
        reason: form.reason || undefined,
        notes: form.notes || undefined,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["followups"] });
      setAddOpen(false);
      setForm({ patient_id: "", scheduled_date: "", reason: "", notes: "" });
    },
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => followupsApi.update(id, { completed: true }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["followups"] }),
  });

  const upcoming = followups.filter((f) => !f.completed_at);
  const completed = followups.filter((f) => f.completed_at);

  const grouped = upcoming.reduce((acc, f) => {
    const month = new Date(f.scheduled_date).toLocaleDateString("en-US", { month: "long", year: "numeric" });
    if (!acc[month]) acc[month] = [];
    acc[month].push(f);
    return acc;
  }, {} as Record<string, FollowUp[]>);

  return (
    <div className="p-6 space-y-5 max-w-3xl">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Follow-ups</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {upcoming.length} upcoming · {completed.length} completed
          </p>
        </div>
        <Button onClick={() => setAddOpen(true)} size="sm" className="gap-1.5">
          <Plus className="size-4" /> Schedule
        </Button>
      </div>

      {/* Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => setShowCompleted(false)}
          className={cn(
            "text-sm px-3 py-1.5 rounded-lg transition-colors",
            !showCompleted ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
          )}
        >
          Upcoming
        </button>
        <button
          onClick={() => setShowCompleted(true)}
          className={cn(
            "text-sm px-3 py-1.5 rounded-lg transition-colors",
            showCompleted ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
          )}
        >
          Completed
        </button>
      </div>

      {isLoading ? (
        <div className="text-sm text-muted-foreground py-8 text-center">Loading…</div>
      ) : !showCompleted ? (
        /* Upcoming — grouped by month */
        Object.keys(grouped).length === 0 ? (
          <div className="rounded-xl border bg-card p-8 text-center text-sm text-muted-foreground">
            No upcoming follow-ups. Schedule one above.
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(grouped).map(([month, items]) => (
              <div key={month} className="space-y-2">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{month}</p>
                <div className="space-y-2">
                  {items.map((f) => (
                    <div key={f.id} className="rounded-xl border bg-card p-4 flex items-start gap-4">
                      <div className="text-center min-w-[40px] shrink-0">
                        <p className="text-lg font-semibold leading-none">
                          {new Date(f.scheduled_date).getDate()}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(f.scheduled_date).toLocaleDateString("en-US", { weekday: "short" })}
                        </p>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm">{f.patient_name ?? "Patient"}</p>
                        {f.reason && <p className="text-sm text-muted-foreground">{f.reason}</p>}
                        {f.notes && <p className="text-xs text-muted-foreground mt-0.5">{f.notes}</p>}
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => completeMutation.mutate(f.id)}
                        disabled={completeMutation.isPending}
                        className="gap-1.5 shrink-0"
                      >
                        <Check className="size-3.5" /> Done
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        /* Completed */
        completed.length === 0 ? (
          <div className="rounded-xl border bg-card p-8 text-center text-sm text-muted-foreground">
            No completed follow-ups yet.
          </div>
        ) : (
          <div className="space-y-2">
            {completed.map((f) => (
              <div key={f.id} className="rounded-xl border bg-card p-4 flex items-start gap-4 opacity-70">
                <div className="text-center min-w-[40px] shrink-0">
                  <p className="text-lg font-semibold leading-none">
                    {new Date(f.scheduled_date).getDate()}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(f.scheduled_date).toLocaleDateString("en-US", { weekday: "short" })}
                  </p>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">{f.patient_name ?? "Patient"}</p>
                  {f.reason && <p className="text-sm text-muted-foreground">{f.reason}</p>}
                </div>
                <Badge variant="success">Done</Badge>
              </div>
            ))}
          </div>
        )
      )}

      {/* Schedule Follow-up Dialog */}
      <Dialog open={addOpen} onClose={() => setAddOpen(false)} title="Schedule Follow-up">
        <form
          onSubmit={(e) => { e.preventDefault(); addMutation.mutate(); }}
          className="space-y-4"
        >
          <div className="space-y-1.5">
            <Label>Patient *</Label>
            <Select
              required
              value={form.patient_id}
              onChange={(e) => setForm((f) => ({ ...f, patient_id: e.target.value }))}
            >
              <option value="">Select patient…</option>
              {patients.map((p) => (
                <option key={p.id} value={p.id}>{p.full_name}</option>
              ))}
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label>Date *</Label>
            <Input
              type="date"
              required
              value={form.scheduled_date}
              onChange={(e) => setForm((f) => ({ ...f, scheduled_date: e.target.value }))}
            />
          </div>
          <div className="space-y-1.5">
            <Label>Reason</Label>
            <Input
              placeholder="e.g. 4-week protocol review"
              value={form.reason}
              onChange={(e) => setForm((f) => ({ ...f, reason: e.target.value }))}
            />
          </div>
          <div className="space-y-1.5">
            <Label>Notes</Label>
            <Textarea
              rows={2}
              placeholder="Any prep notes…"
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
            />
          </div>
          <div className="flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={() => setAddOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={addMutation.isPending}>
              {addMutation.isPending ? "Scheduling…" : "Schedule"}
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
}
