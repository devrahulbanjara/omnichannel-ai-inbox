import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const tagVariants = cva(
  "inline-flex h-5 w-fit shrink-0 items-center gap-1 rounded-sm px-1.5 text-2xs font-medium whitespace-nowrap [&>svg]:size-3",
  {
    variants: {
      tone: {
        neutral: "bg-muted text-muted-foreground",
        brand: "bg-accent text-accent-foreground",
        success: "bg-success-subtle text-success",
        warning: "bg-warning-subtle text-warning",
        danger: "bg-destructive-subtle text-destructive",
        info: "bg-info-subtle text-info",
      },
    },
    defaultVariants: { tone: "neutral" },
  },
)

export type Tone = NonNullable<VariantProps<typeof tagVariants>["tone"]>

export function Tag({ tone, className, ...props }: React.ComponentProps<"span"> & VariantProps<typeof tagVariants>) {
  return <span data-slot="tag" className={cn(tagVariants({ tone }), className)} {...props} />
}
