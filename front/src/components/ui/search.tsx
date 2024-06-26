import * as React from "react"
import SearchIcon from '@mui/icons-material/Search'
import { cn } from "@/lib/utils"

export interface SearchProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Search = React.forwardRef<HTMLInputElement, SearchProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <div className="flex space-x-1 h-10 w-full rounded-lg border-none shadow-md bg-background placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50">
        <SearchIcon className="ml-3 mr-1 my-2"/>
        <input
          type={type}
          className={cn(
            "w-full px-3 py-2 rounded-lg text-sm ring-offset-background focus-visible:outline-none",
            className
          )}
          ref={ref}
          {...props}
        />
      </div>
    )
  }
)
Search.displayName = "Search"

export { Search }
