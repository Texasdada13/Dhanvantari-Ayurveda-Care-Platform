"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Check, Loader2 } from "lucide-react";
import { assessmentsApi } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

// ── Prakriti Questions (20 questions, each scored V/P/K) ─────────────────

const PRAKRITI_QUESTIONS = [
  {
    id: "body_frame",
    question: "Body Frame",
    options: [
      { label: "Thin, light, tall or short, narrow", dosha: "vata" },
      { label: "Medium, athletic, well-proportioned", dosha: "pitta" },
      { label: "Large, solid, broad shoulders/hips", dosha: "kapha" },
    ],
  },
  {
    id: "body_weight",
    question: "Body Weight",
    options: [
      { label: "Difficulty gaining weight, loses easily", dosha: "vata" },
      { label: "Moderate, gains/loses with effort", dosha: "pitta" },
      { label: "Gains weight easily, hard to lose", dosha: "kapha" },
    ],
  },
  {
    id: "skin",
    question: "Skin Quality",
    options: [
      { label: "Dry, rough, cool, thin", dosha: "vata" },
      { label: "Warm, oily, sensitive, prone to rashes", dosha: "pitta" },
      { label: "Thick, cool, moist, smooth, pale", dosha: "kapha" },
    ],
  },
  {
    id: "hair",
    question: "Hair",
    options: [
      { label: "Dry, curly, thin, brittle", dosha: "vata" },
      { label: "Fine, straight, early gray/thinning", dosha: "pitta" },
      { label: "Thick, wavy, lustrous, oily", dosha: "kapha" },
    ],
  },
  {
    id: "eyes",
    question: "Eyes",
    options: [
      { label: "Small, dry, active, dark", dosha: "vata" },
      { label: "Medium, sharp, sensitive to light", dosha: "pitta" },
      { label: "Large, calm, moist, attractive", dosha: "kapha" },
    ],
  },
  {
    id: "appetite",
    question: "Appetite",
    options: [
      { label: "Irregular, variable, forget to eat", dosha: "vata" },
      { label: "Strong, intense, irritable if meal is missed", dosha: "pitta" },
      { label: "Steady, can skip meals without discomfort", dosha: "kapha" },
    ],
  },
  {
    id: "digestion",
    question: "Digestion",
    options: [
      { label: "Variable, gas and bloating", dosha: "vata" },
      { label: "Quick, strong, acid reflux tendency", dosha: "pitta" },
      { label: "Slow, heavy feeling after meals", dosha: "kapha" },
    ],
  },
  {
    id: "thirst",
    question: "Thirst",
    options: [
      { label: "Variable, often forget to drink", dosha: "vata" },
      { label: "Frequent and strong", dosha: "pitta" },
      { label: "Moderate to low", dosha: "kapha" },
    ],
  },
  {
    id: "bowel_habits",
    question: "Bowel Habits",
    options: [
      { label: "Irregular, dry, constipation tendency", dosha: "vata" },
      { label: "Regular, loose, burning sensation", dosha: "pitta" },
      { label: "Regular but heavy, slow, mucus", dosha: "kapha" },
    ],
  },
  {
    id: "sleep",
    question: "Sleep Pattern",
    options: [
      { label: "Light, interrupted, difficulty falling asleep", dosha: "vata" },
      { label: "Moderate, sharp/vivid dreams", dosha: "pitta" },
      { label: "Deep, heavy, hard to wake up", dosha: "kapha" },
    ],
  },
  {
    id: "dreams",
    question: "Dream Quality",
    options: [
      { label: "Active, flying, anxious, many dreams", dosha: "vata" },
      { label: "Fiery, vivid, competitive, colorful", dosha: "pitta" },
      { label: "Calm, watery, romantic, few dreams", dosha: "kapha" },
    ],
  },
  {
    id: "speech",
    question: "Speech Pattern",
    options: [
      { label: "Fast, talkative, jumps between topics", dosha: "vata" },
      { label: "Sharp, precise, argumentative", dosha: "pitta" },
      { label: "Slow, melodious, thoughtful, few words", dosha: "kapha" },
    ],
  },
  {
    id: "mental_activity",
    question: "Mental Activity",
    options: [
      { label: "Quick, restless, many ideas at once", dosha: "vata" },
      { label: "Sharp, focused, analytical, intense", dosha: "pitta" },
      { label: "Calm, steady, contemplative", dosha: "kapha" },
    ],
  },
  {
    id: "memory",
    question: "Memory",
    options: [
      { label: "Quick to learn, quick to forget", dosha: "vata" },
      { label: "Medium, sharp, good recall", dosha: "pitta" },
      { label: "Slow to learn, excellent long-term retention", dosha: "kapha" },
    ],
  },
  {
    id: "emotions",
    question: "Emotional Tendency",
    options: [
      { label: "Anxiety, fear, worry, nervousness", dosha: "vata" },
      { label: "Irritability, anger, judgment, frustration", dosha: "pitta" },
      { label: "Attachment, complacency, possessiveness", dosha: "kapha" },
    ],
  },
  {
    id: "stress_response",
    question: "Stress Response",
    options: [
      { label: "Worry, overthink, panic", dosha: "vata" },
      { label: "Anger, confrontation, frustration", dosha: "pitta" },
      { label: "Withdrawal, avoidance, emotional eating", dosha: "kapha" },
    ],
  },
  {
    id: "activity_level",
    question: "Physical Activity Preference",
    options: [
      { label: "Very active, restless, quick movements", dosha: "vata" },
      { label: "Moderate, competitive, goal-driven", dosha: "pitta" },
      { label: "Low energy, prefers leisure, steady", dosha: "kapha" },
    ],
  },
  {
    id: "temperature",
    question: "Temperature Preference",
    options: [
      { label: "Prefers warm, dislikes cold/wind", dosha: "vata" },
      { label: "Prefers cool, uncomfortable in heat", dosha: "pitta" },
      { label: "Tolerates both, dislikes damp/cold", dosha: "kapha" },
    ],
  },
  {
    id: "sweating",
    question: "Sweating",
    options: [
      { label: "Minimal sweating", dosha: "vata" },
      { label: "Profuse, strong odor", dosha: "pitta" },
      { label: "Moderate, pleasant or none", dosha: "kapha" },
    ],
  },
  {
    id: "joints",
    question: "Joints",
    options: [
      { label: "Crack and pop, dry, prominent", dosha: "vata" },
      { label: "Flexible, loose, prone to inflammation", dosha: "pitta" },
      { label: "Large, well-lubricated, stable", dosha: "kapha" },
    ],
  },
];

// ── Vikriti Symptoms (current imbalance checklist) ─────────────────────────

const VIKRITI_SYMPTOMS = [
  { id: "anxiety", label: "Anxiety / Restlessness", dosha: "vata" },
  { id: "insomnia", label: "Insomnia / Light Sleep", dosha: "vata" },
  { id: "dry_skin", label: "Dry Skin / Cracking", dosha: "vata" },
  { id: "constipation", label: "Constipation / Gas / Bloating", dosha: "vata" },
  { id: "joint_pain", label: "Joint Pain / Stiffness", dosha: "vata" },
  { id: "cold_hands", label: "Cold Hands and Feet", dosha: "vata" },
  { id: "weight_loss", label: "Unintended Weight Loss", dosha: "vata" },
  { id: "acid_reflux", label: "Acid Reflux / Heartburn", dosha: "pitta" },
  { id: "inflammation", label: "Inflammation / Rashes / Acne", dosha: "pitta" },
  { id: "irritability", label: "Irritability / Anger", dosha: "pitta" },
  { id: "excessive_heat", label: "Excessive Body Heat", dosha: "pitta" },
  { id: "loose_stools", label: "Loose Stools / Diarrhea", dosha: "pitta" },
  { id: "burning_eyes", label: "Burning Eyes / Sensitivity", dosha: "pitta" },
  { id: "excessive_sweating", label: "Excessive Sweating", dosha: "pitta" },
  { id: "congestion", label: "Congestion / Sinus Issues", dosha: "kapha" },
  { id: "weight_gain", label: "Weight Gain / Water Retention", dosha: "kapha" },
  { id: "lethargy", label: "Lethargy / Heaviness / Fatigue", dosha: "kapha" },
  { id: "excess_mucus", label: "Excess Mucus Production", dosha: "kapha" },
  { id: "sluggish_digestion", label: "Sluggish Digestion / Nausea", dosha: "kapha" },
  { id: "depression", label: "Depression / Emotional Withdrawal", dosha: "kapha" },
  { id: "attachment", label: "Excessive Attachment / Possessiveness", dosha: "kapha" },
];

// ── Agni Types ──────────────────────────────────────────────────────────────

const AGNI_QUESTIONS = [
  {
    id: "appetite_pattern",
    question: "How is the patient's appetite pattern?",
    options: [
      { label: "Irregular — sometimes ravenous, sometimes no appetite", value: "Vishama Agni" },
      { label: "Very strong — gets irritable/weak if meals are delayed", value: "Tikshna Agni" },
      { label: "Weak — feels full quickly, slow to get hungry", value: "Manda Agni" },
      { label: "Balanced — regular hunger at meal times, digests well", value: "Sama Agni" },
    ],
  },
  {
    id: "post_meal",
    question: "How does the patient feel after eating?",
    options: [
      { label: "Variable — sometimes fine, sometimes bloated/gassy", value: "Vishama Agni" },
      { label: "Quick digestion, may get acid reflux or burning", value: "Tikshna Agni" },
      { label: "Heavy, sluggish, drowsy after meals", value: "Manda Agni" },
      { label: "Comfortable, energized, light", value: "Sama Agni" },
    ],
  },
];

const AMA_QUESTIONS = [
  {
    id: "tongue_coating",
    question: "Tongue coating in the morning?",
    options: [
      { label: "None or minimal", value: 0 },
      { label: "Thin white coating", value: 1 },
      { label: "Moderate thick coating", value: 2 },
      { label: "Heavy yellow/green coating", value: 3 },
    ],
  },
  {
    id: "body_odor",
    question: "Body odor / breath?",
    options: [
      { label: "Fresh, no issues", value: 0 },
      { label: "Mild odor", value: 1 },
      { label: "Noticeable, unpleasant", value: 2 },
      { label: "Strong, persistent despite hygiene", value: 3 },
    ],
  },
  {
    id: "stool_quality",
    question: "Stool quality?",
    options: [
      { label: "Well-formed, regular, no odor", value: 0 },
      { label: "Slightly sticky or irregular", value: 1 },
      { label: "Sticky, sinking, foul-smelling", value: 2 },
      { label: "Very sticky/mucoid, strong odor", value: 3 },
    ],
  },
  {
    id: "energy",
    question: "Overall energy level?",
    options: [
      { label: "Good energy throughout the day", value: 0 },
      { label: "Mild fatigue, especially after meals", value: 1 },
      { label: "Persistent heaviness and fog", value: 2 },
      { label: "Severe fatigue, brain fog, body aches", value: 3 },
    ],
  },
];

// ── Ashtavidha Pareeksha (8-fold exam) ──────────────────────────────────────

const ASHTAVIDHA_ITEMS = [
  {
    id: "nadi",
    name: "Nadi (Pulse)",
    findings: ["Vata-type (irregular, thin, fast)", "Pitta-type (sharp, bounding, moderate)", "Kapha-type (slow, broad, steady)", "Mixed / dual pulse"],
  },
  {
    id: "jihwa",
    name: "Jihwa (Tongue)",
    findings: ["Dry, cracked, thin coating (Vata)", "Red, yellow coating, inflammation (Pitta)", "Swollen, thick white coating (Kapha)", "Mixed findings"],
  },
  {
    id: "mutra",
    name: "Mutra (Urine)",
    findings: ["Scanty, clear, frequent (Vata)", "Dark yellow, burning (Pitta)", "Cloudy, thick, infrequent (Kapha)", "Normal / mixed"],
  },
  {
    id: "mala",
    name: "Mala (Stool)",
    findings: ["Dry, hard, irregular (Vata)", "Loose, burning, yellow (Pitta)", "Heavy, mucoid, sluggish (Kapha)", "Normal / mixed"],
  },
  {
    id: "shabda",
    name: "Shabda (Voice/Sound)",
    findings: ["Hoarse, cracking, fast (Vata)", "Sharp, loud, forceful (Pitta)", "Deep, slow, melodious (Kapha)", "Normal / mixed"],
  },
  {
    id: "sparsha",
    name: "Sparsha (Touch/Skin)",
    findings: ["Dry, rough, cool, thin (Vata)", "Warm, moist, sensitive (Pitta)", "Cool, thick, oily, smooth (Kapha)", "Normal / mixed"],
  },
  {
    id: "drika",
    name: "Drika (Eyes)",
    findings: ["Dry, sunken, restless (Vata)", "Red, sensitive, sharp (Pitta)", "Moist, calm, heavy-lidded (Kapha)", "Normal / mixed"],
  },
  {
    id: "akriti",
    name: "Akriti (Appearance)",
    findings: ["Thin, restless, ungrounded (Vata)", "Medium, flushed, intense (Pitta)", "Heavy, calm, lethargic (Kapha)", "Normal / mixed"],
  },
];

// ── Wizard Steps ─────────────────────────────────────────────────────────────

type Step = "prakriti" | "vikriti" | "agni_ama" | "ashtavidha" | "review";
const STEPS: { id: Step; label: string }[] = [
  { id: "prakriti", label: "Prakriti" },
  { id: "vikriti", label: "Vikriti" },
  { id: "agni_ama", label: "Agni & Ama" },
  { id: "ashtavidha", label: "8-Fold Exam" },
  { id: "review", label: "Review" },
];

function computeLabel(v: number, p: number, k: number): string {
  const total = v + p + k;
  if (total === 0) return "—";
  const pcts: [string, number][] = [
    ["Vata", v / total],
    ["Pitta", p / total],
    ["Kapha", k / total],
  ];
  pcts.sort((a, b) => b[1] - a[1]);
  if (pcts[0][1] >= 0.5) {
    if (pcts[1][1] >= 0.3) return `${pcts[0][0]}-${pcts[1][0]}`;
    return pcts[0][0];
  }
  if (Math.abs(pcts[0][1] - pcts[1][1]) <= 0.1) {
    if (Math.abs(pcts[1][1] - pcts[2][1]) <= 0.1) return "Tridoshic";
    return `${pcts[0][0]}-${pcts[1][0]}`;
  }
  return pcts[0][0];
}

// ── Colors ────────────────────────────────────────────────────────────────────

const DOSHA_COLORS: Record<string, string> = {
  vata: "bg-sky-500",
  pitta: "bg-orange-500",
  kapha: "bg-emerald-500",
};

// ── Component ────────────────────────────────────────────────────────────────

export default function DoshaAssessmentWizard({
  patientId,
  onComplete,
  onCancel,
}: {
  patientId: number;
  onComplete: () => void;
  onCancel: () => void;
}) {
  const qc = useQueryClient();
  const [step, setStep] = useState<Step>("prakriti");
  const [notes, setNotes] = useState("");

  // Prakriti responses: { questionId: "vata" | "pitta" | "kapha" }
  const [prakritiR, setPrakritiR] = useState<Record<string, string>>({});
  // Vikriti responses: { symptomId: 0-3 severity }
  const [vikritiR, setVikritiR] = useState<Record<string, number>>({});
  // Agni
  const [agniR, setAgniR] = useState<Record<string, string>>({});
  // Ama
  const [amaR, setAmaR] = useState<Record<string, number>>({});
  // Ashtavidha
  const [ashtaR, setAshtaR] = useState<Record<string, { finding: string; notes: string }>>({});

  const saveMutation = useMutation({
    mutationFn: () => {
      // Compute prakriti scores
      const pScores = { vata: 0, pitta: 0, kapha: 0 };
      Object.values(prakritiR).forEach((d) => {
        if (d in pScores) pScores[d as keyof typeof pScores]++;
      });

      // Compute vikriti scores
      const vScores = { vata: 0, pitta: 0, kapha: 0 };
      Object.entries(vikritiR).forEach(([id, severity]) => {
        if (severity > 0) {
          const symptom = VIKRITI_SYMPTOMS.find((s) => s.id === id);
          if (symptom) vScores[symptom.dosha as keyof typeof vScores] += severity;
        }
      });

      // Determine agni type (most frequent answer)
      const agniCounts: Record<string, number> = {};
      Object.values(agniR).forEach((v) => {
        agniCounts[v] = (agniCounts[v] || 0) + 1;
      });
      const agniType = Object.entries(agniCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || "Sama Agni";

      // Determine ama level
      const amaTotal = Object.values(amaR).reduce((sum, v) => sum + v, 0);
      const amaMax = AMA_QUESTIONS.length * 3;
      let amaLevel = "None";
      if (amaTotal > 0) {
        const pct = amaTotal / amaMax;
        if (pct <= 0.25) amaLevel = "Mild";
        else if (pct <= 0.6) amaLevel = "Moderate";
        else amaLevel = "Severe";
      }

      return assessmentsApi.create(patientId, {
        patient_id: patientId,
        prakriti: { ...pScores, responses: prakritiR },
        vikriti: { ...vScores, responses: vikritiR },
        agni_ama: {
          agni_type: agniType,
          ama_level: amaLevel,
          agni_responses: agniR,
          ama_responses: amaR,
        },
        ashtavidha: ashtaR,
        notes,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assessments", patientId] });
      qc.invalidateQueries({ queryKey: ["patient", patientId] });
      onComplete();
    },
  });

  const stepIdx = STEPS.findIndex((s) => s.id === step);

  // Prakriti scores for display
  const pScores = { vata: 0, pitta: 0, kapha: 0 };
  Object.values(prakritiR).forEach((d) => {
    if (d in pScores) pScores[d as keyof typeof pScores]++;
  });

  // Vikriti scores for display
  const vScores = { vata: 0, pitta: 0, kapha: 0 };
  Object.entries(vikritiR).forEach(([id, severity]) => {
    if (severity > 0) {
      const symptom = VIKRITI_SYMPTOMS.find((s) => s.id === id);
      if (symptom) vScores[symptom.dosha as keyof typeof vScores] += severity;
    }
  });

  return (
    <div className="space-y-5">
      {/* Step indicator */}
      <div className="flex items-center gap-1">
        {STEPS.map((s, i) => (
          <div key={s.id} className="flex items-center gap-1">
            <button
              onClick={() => setStep(s.id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
                step === s.id
                  ? "bg-primary text-primary-foreground"
                  : i < stepIdx
                    ? "bg-primary/15 text-primary"
                    : "text-muted-foreground hover:text-foreground"
              )}
            >
              {i < stepIdx && <Check className="size-3" />}
              {s.label}
            </button>
            {i < STEPS.length - 1 && <ChevronRight className="size-3 text-muted-foreground" />}
          </div>
        ))}
      </div>

      {/* ── Step: Prakriti ──────────────────────────────────────────────────── */}
      {step === "prakriti" && (
        <div className="space-y-4">
          <div>
            <h3 className="font-medium">Prakriti Assessment</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Constitutional body type — select the option that best describes the patient&apos;s natural, lifelong tendencies.
              {Object.keys(prakritiR).length}/{PRAKRITI_QUESTIONS.length} answered
            </p>
          </div>

          {/* Live score bar */}
          {Object.keys(prakritiR).length > 0 && (
            <ScoreBar vata={pScores.vata} pitta={pScores.pitta} kapha={pScores.kapha} total={PRAKRITI_QUESTIONS.length} />
          )}

          <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
            {PRAKRITI_QUESTIONS.map((q, qi) => (
              <div key={q.id} className="rounded-xl border bg-card p-4 space-y-2">
                <p className="text-sm font-medium">
                  <span className="text-muted-foreground mr-1.5">{qi + 1}.</span>
                  {q.question}
                </p>
                <div className="grid gap-1.5">
                  {q.options.map((opt) => (
                    <button
                      key={opt.dosha}
                      onClick={() => setPrakritiR((prev) => ({ ...prev, [q.id]: opt.dosha }))}
                      className={cn(
                        "text-left text-sm px-3 py-2 rounded-lg border transition-colors",
                        prakritiR[q.id] === opt.dosha
                          ? "border-primary bg-primary/10 text-primary font-medium"
                          : "hover:bg-muted/50"
                      )}
                    >
                      <span className={cn(
                        "inline-block w-1.5 h-1.5 rounded-full mr-2",
                        DOSHA_COLORS[opt.dosha]
                      )} />
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Step: Vikriti ──────────────────────────────────────────────────── */}
      {step === "vikriti" && (
        <div className="space-y-4">
          <div>
            <h3 className="font-medium">Vikriti Assessment</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Current imbalance symptoms — rate severity from 0 (absent) to 3 (severe).
            </p>
          </div>

          {(vScores.vata > 0 || vScores.pitta > 0 || vScores.kapha > 0) && (
            <ScoreBar vata={vScores.vata} pitta={vScores.pitta} kapha={vScores.kapha} total={vScores.vata + vScores.pitta + vScores.kapha} />
          )}

          <div className="space-y-1 max-h-[60vh] overflow-y-auto pr-1">
            {(["vata", "pitta", "kapha"] as const).map((dosha) => (
              <div key={dosha} className="space-y-1">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground pt-3 pb-1 flex items-center gap-1.5">
                  <span className={cn("w-2 h-2 rounded-full", DOSHA_COLORS[dosha])} />
                  {dosha.charAt(0).toUpperCase() + dosha.slice(1)} Symptoms
                </p>
                {VIKRITI_SYMPTOMS.filter((s) => s.dosha === dosha).map((symptom) => (
                  <div key={symptom.id} className="flex items-center gap-3 rounded-lg border bg-card px-3 py-2">
                    <span className="text-sm flex-1">{symptom.label}</span>
                    <div className="flex gap-1">
                      {[0, 1, 2, 3].map((sev) => (
                        <button
                          key={sev}
                          onClick={() => setVikritiR((prev) => ({ ...prev, [symptom.id]: sev }))}
                          className={cn(
                            "w-8 h-7 rounded text-xs font-medium transition-colors",
                            (vikritiR[symptom.id] ?? 0) === sev
                              ? sev === 0
                                ? "bg-muted text-foreground"
                                : sev === 1
                                  ? "bg-yellow-100 text-yellow-800"
                                  : sev === 2
                                    ? "bg-orange-100 text-orange-800"
                                    : "bg-red-100 text-red-800"
                              : "bg-muted/40 text-muted-foreground hover:bg-muted"
                          )}
                        >
                          {sev}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Step: Agni & Ama ───────────────────────────────────────────────── */}
      {step === "agni_ama" && (
        <div className="space-y-5">
          <div>
            <h3 className="font-medium">Agni (Digestive Fire) Assessment</h3>
            <p className="text-xs text-muted-foreground mt-0.5">Determine the type of digestive fire.</p>
          </div>
          <div className="space-y-3">
            {AGNI_QUESTIONS.map((q) => (
              <div key={q.id} className="rounded-xl border bg-card p-4 space-y-2">
                <p className="text-sm font-medium">{q.question}</p>
                <div className="grid gap-1.5">
                  {q.options.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setAgniR((prev) => ({ ...prev, [q.id]: opt.value }))}
                      className={cn(
                        "text-left text-sm px-3 py-2 rounded-lg border transition-colors",
                        agniR[q.id] === opt.value
                          ? "border-primary bg-primary/10 text-primary font-medium"
                          : "hover:bg-muted/50"
                      )}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t pt-5">
            <h3 className="font-medium">Ama (Toxin Accumulation) Assessment</h3>
            <p className="text-xs text-muted-foreground mt-0.5">Rate from 0 (none) to 3 (severe).</p>
          </div>
          <div className="space-y-3">
            {AMA_QUESTIONS.map((q) => (
              <div key={q.id} className="rounded-xl border bg-card p-4 space-y-2">
                <p className="text-sm font-medium">{q.question}</p>
                <div className="grid gap-1.5">
                  {q.options.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setAmaR((prev) => ({ ...prev, [q.id]: opt.value }))}
                      className={cn(
                        "text-left text-sm px-3 py-2 rounded-lg border transition-colors",
                        amaR[q.id] === opt.value
                          ? "border-primary bg-primary/10 text-primary font-medium"
                          : "hover:bg-muted/50"
                      )}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Step: Ashtavidha ───────────────────────────────────────────────── */}
      {step === "ashtavidha" && (
        <div className="space-y-4">
          <div>
            <h3 className="font-medium">Ashtavidha Pareeksha (8-Fold Examination)</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Record clinical findings from the traditional eight-point examination.
            </p>
          </div>
          <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
            {ASHTAVIDHA_ITEMS.map((item) => (
              <div key={item.id} className="rounded-xl border bg-card p-4 space-y-2">
                <p className="text-sm font-medium">{item.name}</p>
                <div className="grid gap-1.5">
                  {item.findings.map((f) => (
                    <button
                      key={f}
                      onClick={() =>
                        setAshtaR((prev) => ({
                          ...prev,
                          [item.id]: { ...prev[item.id], finding: f, notes: prev[item.id]?.notes || "" },
                        }))
                      }
                      className={cn(
                        "text-left text-xs px-3 py-2 rounded-lg border transition-colors",
                        ashtaR[item.id]?.finding === f
                          ? "border-primary bg-primary/10 text-primary font-medium"
                          : "hover:bg-muted/50"
                      )}
                    >
                      {f}
                    </button>
                  ))}
                </div>
                <Textarea
                  rows={1}
                  placeholder="Additional notes…"
                  className="text-xs"
                  value={ashtaR[item.id]?.notes || ""}
                  onChange={(e) =>
                    setAshtaR((prev) => ({
                      ...prev,
                      [item.id]: { ...prev[item.id], finding: prev[item.id]?.finding || "", notes: e.target.value },
                    }))
                  }
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Step: Review ───────────────────────────────────────────────────── */}
      {step === "review" && (
        <div className="space-y-5">
          <h3 className="font-medium">Assessment Summary</h3>

          {/* Prakriti result */}
          <div className="rounded-xl border bg-card p-5 space-y-3">
            <h4 className="text-sm font-medium">Prakriti (Constitution)</h4>
            <div className="flex items-center gap-3">
              <span className="text-2xl font-semibold text-primary">
                {computeLabel(pScores.vata, pScores.pitta, pScores.kapha)}
              </span>
              <span className="text-xs text-muted-foreground">
                V:{pScores.vata} · P:{pScores.pitta} · K:{pScores.kapha}
              </span>
            </div>
            <ScoreBar vata={pScores.vata} pitta={pScores.pitta} kapha={pScores.kapha} total={PRAKRITI_QUESTIONS.length} />
          </div>

          {/* Vikriti result */}
          <div className="rounded-xl border bg-card p-5 space-y-3">
            <h4 className="text-sm font-medium">Vikriti (Current Imbalance)</h4>
            <div className="flex items-center gap-3">
              <span className="text-2xl font-semibold text-primary">
                {computeLabel(vScores.vata, vScores.pitta, vScores.kapha)}
              </span>
              <span className="text-xs text-muted-foreground">
                V:{vScores.vata} · P:{vScores.pitta} · K:{vScores.kapha}
              </span>
            </div>
            {(vScores.vata > 0 || vScores.pitta > 0 || vScores.kapha > 0) && (
              <ScoreBar vata={vScores.vata} pitta={vScores.pitta} kapha={vScores.kapha} total={vScores.vata + vScores.pitta + vScores.kapha} />
            )}
          </div>

          {/* Agni & Ama */}
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-xl border bg-card p-5">
              <h4 className="text-sm font-medium mb-1">Agni Type</h4>
              <p className="text-lg font-semibold text-primary">
                {(() => {
                  const counts: Record<string, number> = {};
                  Object.values(agniR).forEach((v) => { counts[v] = (counts[v] || 0) + 1; });
                  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] || "Not assessed";
                })()}
              </p>
            </div>
            <div className="rounded-xl border bg-card p-5">
              <h4 className="text-sm font-medium mb-1">Ama Level</h4>
              <p className="text-lg font-semibold text-primary">
                {(() => {
                  const total = Object.values(amaR).reduce((s, v) => s + v, 0);
                  const max = AMA_QUESTIONS.length * 3;
                  if (total === 0) return "None";
                  const pct = total / max;
                  if (pct <= 0.25) return "Mild";
                  if (pct <= 0.6) return "Moderate";
                  return "Severe";
                })()}
              </p>
            </div>
          </div>

          {/* Ashtavidha summary */}
          {Object.keys(ashtaR).length > 0 && (
            <div className="rounded-xl border bg-card p-5 space-y-2">
              <h4 className="text-sm font-medium">8-Fold Examination Findings</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {ASHTAVIDHA_ITEMS.filter((i) => ashtaR[i.id]?.finding).map((item) => (
                  <div key={item.id}>
                    <p className="text-xs text-muted-foreground">{item.name}</p>
                    <p className="text-xs">{ashtaR[item.id].finding}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Practitioner Notes</label>
            <Textarea
              rows={3}
              placeholder="Additional observations, clinical reasoning…"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between pt-2 border-t">
        <div>
          {stepIdx > 0 ? (
            <Button variant="outline" size="sm" onClick={() => setStep(STEPS[stepIdx - 1].id)} className="gap-1.5">
              <ChevronLeft className="size-3.5" /> Back
            </Button>
          ) : (
            <Button variant="outline" size="sm" onClick={onCancel}>
              Cancel
            </Button>
          )}
        </div>
        <div>
          {step !== "review" ? (
            <Button size="sm" onClick={() => setStep(STEPS[stepIdx + 1].id)} className="gap-1.5">
              Next <ChevronRight className="size-3.5" />
            </Button>
          ) : (
            <Button
              size="sm"
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              className="gap-1.5"
            >
              {saveMutation.isPending ? (
                <><Loader2 className="size-3.5 animate-spin" /> Saving…</>
              ) : (
                <><Check className="size-3.5" /> Save Assessment</>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Score Bar Component ──────────────────────────────────────────────────────

function ScoreBar({ vata, pitta, kapha, total }: { vata: number; pitta: number; kapha: number; total: number }) {
  if (total === 0) return null;
  const vPct = (vata / total) * 100;
  const pPct = (pitta / total) * 100;
  const kPct = (kapha / total) * 100;

  return (
    <div className="space-y-1">
      <div className="flex h-3 rounded-full overflow-hidden bg-muted">
        {vPct > 0 && <div className="bg-sky-500 transition-all" style={{ width: `${vPct}%` }} />}
        {pPct > 0 && <div className="bg-orange-500 transition-all" style={{ width: `${pPct}%` }} />}
        {kPct > 0 && <div className="bg-emerald-500 transition-all" style={{ width: `${kPct}%` }} />}
      </div>
      <div className="flex justify-between text-[10px] font-medium">
        <span className="text-sky-600">V {Math.round(vPct)}%</span>
        <span className="text-orange-600">P {Math.round(pPct)}%</span>
        <span className="text-emerald-600">K {Math.round(kPct)}%</span>
      </div>
    </div>
  );
}
