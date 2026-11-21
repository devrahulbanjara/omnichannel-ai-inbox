import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { cn } from "@/lib/utils"

// Chat-sized spacing, lists, links, code and tables. Colors come from the surrounding bubble.
const markdownStyles = [
  "space-y-2 break-words leading-relaxed",
  "[&_ul]:list-disc [&_ol]:list-decimal [&_ul]:space-y-1 [&_ol]:space-y-1 [&_ul]:pl-5 [&_ol]:pl-5",
  "[&_li]:pl-0.5 [&_strong]:font-semibold [&_a]:underline [&_a]:underline-offset-2",
  "[&_code]:rounded [&_code]:bg-foreground/10 [&_code]:px-1 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-[0.9em]",
  "[&_table]:block [&_table]:overflow-x-auto [&_th]:border-b [&_td]:border-b [&_th]:px-2 [&_td]:px-2 [&_th]:py-1 [&_td]:py-1 [&_th]:text-left",
]

/** Renders markdown written by the store side (staff or AI). Raw HTML is not rendered. */
function Markdown({ text, className }: { text: string; className?: string }) {
  return (
    <div data-slot="markdown" className={cn(markdownStyles, className)}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
    </div>
  )
}

export { Markdown }
