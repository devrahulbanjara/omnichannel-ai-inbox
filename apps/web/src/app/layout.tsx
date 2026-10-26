import type { Metadata } from "next"
import { Noto_Sans_Devanagari, Plus_Jakarta_Sans } from "next/font/google"
import { ThemeProvider } from "next-themes"
import { TooltipProvider } from "@/components/ui/tooltip"
import "./globals.css"
import { Providers } from "./providers"

const jakarta = Plus_Jakarta_Sans({ variable: "--font-jakarta", subsets: ["latin"] })
const devanagari = Noto_Sans_Devanagari({ variable: "--font-devanagari", subsets: ["devanagari"] })

export const metadata: Metadata = {
  title: "Inbox",
  description: "Omnichannel inbox with an AI sales agent",
}

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" suppressHydrationWarning className={`${jakarta.variable} ${devanagari.variable} h-full antialiased`}>
      <body className="h-full overflow-hidden">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <TooltipProvider>
            <Providers>{children}</Providers>
          </TooltipProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
