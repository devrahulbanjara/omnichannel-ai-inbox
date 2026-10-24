import { useId } from "react"
import { cn } from "@/lib/utils"

// Four-point sparkle centred on (x, y) with radius r.
const sparkle = (x: number, y: number, r: number) => {
  const k = r * 0.14
  return `M${x} ${y - r}Q${x + k} ${y - k} ${x + r} ${y}Q${x + k} ${y + k} ${x} ${y + r}Q${x - k} ${y + k} ${x - r} ${y}Q${x - k} ${y - k} ${x} ${y - r}Z`
}

const STARS = [
  { d: sparkle(10, 13.5, 9), origin: "10px 13.5px" },
  { d: sparkle(19.5, 4.5, 3.6), origin: "19.5px 4.5px" },
  { d: sparkle(20, 18.5, 2.4), origin: "20px 18.5px" },
]

/** AI identity mark. `active` animates the gradient while the agent is working. */
export function AiMark({ active = false, className }: { active?: boolean; className?: string }) {
  const id = useId()
  const flow = (delay: string) => (active ? { animation: `ai-flow 4s ease-in-out ${delay} infinite` } : undefined)

  return (
    <svg data-slot="ai-mark" viewBox="0 0 24 24" aria-hidden="true" className={cn("size-4 shrink-0", className)}>
      <defs>
        <linearGradient id={id} x1="2" y1="3" x2="22" y2="22" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="var(--ai-1)" style={flow("0s")} />
          <stop offset="0.55" stopColor="var(--ai-2)" style={flow("-1.3s")} />
          <stop offset="1" stopColor="var(--ai-3)" style={flow("-2.6s")} />
        </linearGradient>
      </defs>
      {STARS.map((s, i) => (
        <path
          key={i}
          d={s.d}
          fill={`url(#${id})`}
          style={
            active && i > 0
              ? { transformOrigin: s.origin, animation: `ai-twinkle 2.4s ease-in-out ${i * 0.6}s infinite` }
              : undefined
          }
        />
      ))}
    </svg>
  )
}
