import { Button } from "@/components/ui/button";
import { LoaderCircle } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

interface LoadingProps {
    id: string;
    episode: string;
    title: string;
}

export function SubLoader({ id, episode, title }: LoadingProps) {
    const [loading, setLoading] = useState<boolean>(false);

    return (
        <>
        {
            (loading) ? 
            (<Button disabled>
                <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> Loading
            </Button>) : 
            (<Link href={`/anime/${id}/episode/${episode}/subtitles?title=${title}`}>
                <Button onClick={() => setLoading(true)}>Download Subtitles</Button>
            </Link>)
        }
        </>
    )
}

export function VocabLoader({ id, episode, title }: LoadingProps) {
    const [loading, setLoading] = useState<boolean>(false);

    return (
        <>
        {
            (loading) ? 
            (<Button disabled>
                <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> Loading
            </Button>) : 
            (<Link href={`/anime/${id}/episode/${episode}?offset=0&title=${title}`}>
                <Button onClick={() => setLoading(true)}>Vocabulary List</Button>
            </Link>)
        }
        </>
    )
}


