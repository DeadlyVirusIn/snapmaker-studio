import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Coins, Tag, TrendingUp, ChevronDown, RotateCcw } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { costToPrice, pricingDoctor, profitDoctor } from "@/api";
import { useFilament } from "@/store/filament";
import { useBusiness, bizFactors } from "@/store/business";

function NumField({ label, value, onChange, step = 1 }:
  { label: string; value: number; onChange: (v: number) => void; step?: number }) {
  return (
    <label className="flex flex-col gap-0.5">
      <span className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</span>
      <input type="number" min={0} step={step} value={value}
        onChange={(e) => onChange(Number(e.target.value) || 0)}
        className="w-full rounded-md border border-border bg-background px-2 py-1 text-xs outline-none focus:border-primary" />
    </label>
  );
}

// The Business Intelligence Layer made visible: Cost / Pricing / Profit Doctors
// as three first-class cards. Beginner-friendly headline numbers up top; the
// breakdown, tiers, and projections live behind a "Show details" disclosure.
// Cost factors come from the user's editable assumptions (local-only).
export function BusinessDoctors({ filePath, host }: { filePath: string; host?: string | null }) {
  const [open, setOpen] = useState(false);
  const { pricePerKg, currency } = useFilament();
  const biz = useBusiness();
  const factors = bizFactors(biz, pricePerKg);
  // key on the factor values so editing an assumption refetches.
  const fkey = JSON.stringify(factors) + currency;
  const cost = useQuery({ queryKey: ["bd-cost", filePath, host, fkey], queryFn: () => costToPrice(filePath, { host, currency, factors }), retry: false, staleTime: 30000 });
  const pricing = useQuery({ queryKey: ["bd-pricing", filePath, host, fkey], queryFn: () => pricingDoctor(filePath, host, { currency, factors }), retry: false, staleTime: 30000 });
  const profit = useQuery({ queryKey: ["bd-profit", filePath, host, fkey], queryFn: () => profitDoctor(filePath, host, { currency, factors }), retry: false, staleTime: 30000 });

  const c = cost.data, p = pricing.data, pr = profit.data;
  if (!c?.available && !p?.available) return null;
  const cur = c?.currency ?? p?.currency ?? "$";
  const mk = p?.tiers?.find((t) => t.label === "Marketplace");

  const Pillar = ({ icon: Icon, name, token, value, sub }: any) => (
    <div className="flex-1 rounded-lg border border-border p-3">
      <div className="flex items-center gap-2">
        <span className="flex h-7 w-7 items-center justify-center rounded-md"
              style={{ color: `hsl(var(${token}))`, backgroundColor: `hsl(var(${token}) / 0.12)` }}>
          <Icon className="h-4 w-4" />
        </span>
        <span className="text-xs font-semibold">{name}</span>
      </div>
      <p className="mt-2 text-lg font-bold tabular-nums">{value}</p>
      <p className="text-[11px] text-muted-foreground">{sub}</p>
    </div>
  );

  return (
    <Card>
      <CardContent className="space-y-3 p-5">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold">Cost, Pricing &amp; Profit</span>
          <span className="text-[11px] text-muted-foreground">rough estimates · your assumptions · not financial advice</span>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row">
          <Pillar icon={Coins} name="Cost Doctor" token="--doctor-cost"
                  value={c?.available ? `${cur}${c.true_cost}` : "—"}
                  sub="true cost to make" />
          <Pillar icon={Tag} name="Pricing Doctor" token="--stage-validate"
                  value={mk ? `${cur}${mk.price}` : "—"}
                  sub="suggested marketplace price" />
          <Pillar icon={TrendingUp} name="Profit Doctor" token="--stage-output"
                  value={pr?.available ? `${cur}${pr.profit_per_print}` : "—"}
                  sub={pr?.available ? `${pr.margin_pct}% margin / print` : "profit per print"} />
        </div>

        <button onClick={() => setOpen((o) => !o)}
                className="flex items-center gap-1 text-xs font-medium text-primary">
          <ChevronDown className={`h-3.5 w-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
          {open ? "Hide details" : "Show details & assumptions"}
        </button>

        {open && (
          <div className="space-y-3 border-t border-border pt-3 text-xs">
            <div className="space-y-2 rounded-md border border-border p-3">
              <div className="flex items-center justify-between">
                <p className="font-semibold">Material &amp; business assumptions</p>
                <button onClick={() => biz.reset()} className="flex items-center gap-1 text-[11px] text-primary hover:underline">
                  <RotateCcw className="h-3 w-3" /> Reset
                </button>
              </div>
              <p className="text-muted-foreground">Saved locally on your machine. Defaults are assumptions — edit them and the numbers above update.</p>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                <NumField label={`Spool price ${currency}`} value={pricePerKg} onChange={(v) => useFilament.getState().setPrice(v)} />
                <NumField label="Spool weight (g)" value={biz.spoolWeightG} onChange={(v) => biz.set({ spoolWeightG: v })} />
                <NumField label={`Grams used (0 = ${c?.grams ?? "auto"})`} value={biz.gramsOverride} onChange={(v) => biz.set({ gramsOverride: v })} />
                <NumField label="Electricity /kWh" value={biz.electricityPerKwh} onChange={(v) => biz.set({ electricityPerKwh: v })} step={0.01} />
                <NumField label="Printer watts" value={biz.powerW} onChange={(v) => biz.set({ powerW: v })} />
                <NumField label="Printer price" value={biz.machinePrice} onChange={(v) => biz.set({ machinePrice: v })} />
                <NumField label="Printer life (hrs)" value={biz.machineLifeHours} onChange={(v) => biz.set({ machineLifeHours: v })} />
                <NumField label="Labor (hrs/print)" value={biz.laborHours} onChange={(v) => biz.set({ laborHours: v })} step={0.05} />
                <NumField label={`Labor ${currency}/hr`} value={biz.laborRate} onChange={(v) => biz.set({ laborRate: v })} />
                <NumField label="Packaging" value={biz.packaging} onChange={(v) => biz.set({ packaging: v })} step={0.25} />
                <NumField label="Waste / failure %" value={biz.failureRatePct} onChange={(v) => biz.set({ failureRatePct: v })} />
                <NumField label="Marketplace fee %" value={biz.marketplaceFeePct} onChange={(v) => biz.set({ marketplaceFeePct: v })} />
                <NumField label="Shipping cost" value={biz.shippingCost} onChange={(v) => biz.set({ shippingCost: v })} step={0.5} />
                <NumField label="Shipping charged" value={biz.shippingCharged} onChange={(v) => biz.set({ shippingCharged: v })} step={0.5} />
                <NumField label="Markup / margin %" value={biz.markupPct} onChange={(v) => biz.set({ markupPct: v })} />
              </div>
              {c?.available && c.grams != null && (
                <p className="text-muted-foreground">
                  Material: {c.grams} g × {currency}{pricePerKg} ÷ {biz.spoolWeightG} g ={" "}
                  <span className="font-medium text-foreground">{currency}{c.breakdown?.material}</span>
                  {" "}({c.basis}).
                </p>
              )}
              <p className="text-muted-foreground">
                Formula: material + electricity + machine wear + labour + packaging + failure buffer →
                cost; then marketplace fee + markup → price; shipping (charged − cost) adjusts profit.
              </p>
              <p className="text-muted-foreground opacity-80">
                Material type (density) isn't applied yet. Print time comes from the slicer when you
                send a file to the printer; otherwise time-based costs show as 0. Rough estimate — not
                financial advice.
              </p>
            </div>
            {c?.available && c.breakdown && (
              <div>
                <p className="mb-1 font-semibold">Cost breakdown {c.basis ? `(${c.basis})` : ""}</p>
                <ul className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-muted-foreground sm:grid-cols-3">
                  <li>Material: {cur}{c.breakdown.material}</li>
                  <li>Electricity: {cur}{c.breakdown.electricity}</li>
                  <li>Machine wear: {cur}{c.breakdown.depreciation}</li>
                  <li>Labour: {cur}{c.breakdown.labor}</li>
                  <li>Failure buffer: {cur}{c.breakdown.failure_buffer}</li>
                </ul>
                {!c.time_known && <p className="mt-1 text-muted-foreground opacity-70">Print time unknown — time-based costs shown as 0 until sliced or read from the printer.</p>}
              </div>
            )}
            {p?.available && p.tiers && (
              <div>
                <p className="mb-1 font-semibold">Pricing tiers</p>
                <ul className="space-y-0.5 text-muted-foreground">
                  {p.tiers.map((t) => (
                    <li key={t.label}><span className="font-medium text-foreground">{t.label}: {cur}{t.price}</span> — {t.why}</li>
                  ))}
                </ul>
              </div>
            )}
            {pr?.available && (
              <div>
                <p className="mb-1 font-semibold">Profit projection</p>
                <p className="text-muted-foreground">{pr.verdict}</p>
                {pr.batch && <p className="text-muted-foreground">Batch of {pr.batch.count}: {cur}{pr.batch.profit} profit.</p>}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
