import * as React from "react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { SendHorizontal } from 'lucide-react';

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.ComponentProps<"textarea">
>(({ className, ...props }, ref) => {

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  return (
    <div className="relative">

      <textarea
        className={cn(
          "flex min-h-[60px] max-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-base shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm ",
          className
        )}
        ref={ref}
        {...props}
        onInput={handleInput}
      />
      <Button
         size="icon"
        className="absolute size-8 bottom-2 right-2 px-3 rounded-full"
      >
        <SendHorizontal /></Button>
    </div>
  )
})
Textarea.displayName = "Textarea"

export { Textarea }
