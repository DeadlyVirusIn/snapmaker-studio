import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Coins, Tag, TrendingUp, ChevronDown } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { costToPrice, pricingDoctor, profitDoctor } from "@/api";

// The Business Intelligence Layer made visible: Cost / Pricing / Profit Doctors
// as three first-class cards. Beginner-friendly headline numbers up top; the
// breakdown, tiers, and projections live behind a "Show details" disclosure.
export function BusinessDoctors({ filePath, host }: { filePath: string; host?: string | null }) {
  const [open, setOpen] = useState(false);
  const cost = useQuery({ queryKey: ["bd-cost", filePath, host], queryFn: () => costToPrice(filePath, { host }), retry: false, staleTime: 30000 });
  const pricing = useQuery({ queryKey: ["bd-pricing", filePath, host], queryFn: () => pricingDoctor(filePath, host), retry: false, staleTime: 30000 });
  const profit = useQuery({ queryKey: ["bd-profit", filePath, host], queryFn: () => profitDoctor(filePath, host), retry: false, staleTime: 30000 });

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
          <span className="text-[11px] text-muted-foreground" title="These cards use a default material price; your Settings filament price is applied on the main Cost estimate and in Batch.">estimates · default material price</span>
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
