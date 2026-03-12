"use client";

import { useAuthStore } from "@/store/auth";

export default function DashboardPage() {
  const practitioner = useAuthStore((s) => s.practitioner);

  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          {greeting}, {practitioner?.name?.split(" ")[0] ?? "Vaidya"}
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          Here&apos;s an overview of your practice today.
        </p>
      </div>

      {/* Placeholder stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total Patients", value: "—" },
          { label: "Active Plans", value: "—" },
          { label: "Check-ins Today", value: "—" },
          { label: "Upcoming Follow-ups", value: "—" },
        ].map((s) => (
          <div key={s.label} className="rounded-xl border bg-card p-4 space-y-1">
            <p className="text-xs text-muted-foreground">{s.label}</p>
            <p className="text-2xl font-semibold">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border bg-card p-6 text-center text-muted-foreground text-sm">
        More dashboard widgets coming in Phase 3.
      </div>
    </div>
  );
}
