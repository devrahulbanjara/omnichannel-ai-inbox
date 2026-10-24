import { cn } from "@/lib/utils"

/** Top-level workspace panel. `solid` is for overlays that sit above other content. */
export function Panel({ solid = false, className, ...props }: React.ComponentProps<"section"> & { solid?: boolean }) {
  return (
    <section
      data-slot="panel"
      className={cn(
        "flex h-full min-h-0 flex-col rounded-2xl",
        solid ? "border bg-popover shadow-panel" : "glass",
        className,
      )}
      {...props}
    />
  )
}

/** Raised surface for content inside a panel. */
export function Tile({ className, ...props }: React.ComponentProps<"div">) {
  return <div data-slot="tile" className={cn("glass-raised space-y-1 rounded-lg p-2.5", className)} {...props} />
}
