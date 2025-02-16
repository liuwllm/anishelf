import { Button } from "@/components/ui/button"
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { LoaderCircle } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

interface NavBarProps {
    prev: boolean;
    next: boolean;
    id: string;
    episode: string;
    title: string;
    offset: string;
}

interface NavButtonProps {
    id: string;
    episode: string;
    title: string;
    offset: string;
}

function PrevButton({ id, episode, title, offset }: NavButtonProps) {
    return (
        <Link href={`/anime/${id}/episode/${episode}?offset=${parseInt(offset) - 20}&title=${title}`}>
            <Button>
                <NavigateBeforeIcon className="h-4 w-4"/> 
                <p className="mr-2">Previous</p>
            </Button>
        </Link>
    )
}

function NextButton({ id, episode, title, offset }: NavButtonProps) {
    return (
        (<Link href={`/anime/${id}/episode/${episode}?offset=${parseInt(offset) + 20}&title=${title}`}>
            <Button>
                <p className="ml-2">Next</p>
                <NavigateNextIcon className="h-4 w-4"/> 
            </Button>
        </Link>)
    )
}

function NavBarPrev({ id, episode, title, offset }: NavButtonProps) {
    return (
        <div className="flex justify-start">
            <PrevButton id={id} episode={episode} title={title} offset={offset}/>
        </div>
    )
}

function NavBarNext({ id, episode, title, offset }: NavButtonProps) {
    return (
        <div className="flex justify-end">
            <NextButton id={id} episode={episode} title={title} offset={offset}/>
        </div>
    )
}

function NavBarBoth({ id, episode, title, offset }: NavButtonProps) {
    return (
        <div className="flex justify-between w-full">
            <PrevButton id={id} episode={episode} title={title} offset={offset}/>
            <NextButton id={id} episode={episode} title={title} offset={offset}/>
        </div>
    )
}

export default function NavBar({ prev, next, id, episode, title, offset }: NavBarProps ) {
    if (prev && !next) {
        return (
            <NavBarPrev id={id} episode={episode} title={title} offset={offset}/>
        )
    }
    else if (!prev && next) {
        return (
            <NavBarNext id={id} episode={episode} title={title} offset={offset}/>
        )
    }
    else if (prev && next) {
        return (
            <NavBarBoth id={id} episode={episode} title={title} offset={offset}/>
        )
    }
    else {
        return (<></>)
    }
}