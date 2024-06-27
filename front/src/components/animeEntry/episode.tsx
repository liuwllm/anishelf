import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface EpisodeProps {
    count: number;
    id: number;
}

export default function Episode({ count, id }: EpisodeProps) {
    const episodeNumbers: number[] = [];
  
    for (let i = 1; i <= count; i++) {
        episodeNumbers.push(i)
    }
  
    return (
        <div className="flex flex-col">
            {
                episodeNumbers.map(episode => {
                    return (
                        <div key={episode}>
                            <div className="flex w-full justify-between p-4">
                                <p className="text-md font-medium text-slate-500">Episode {episode}</p>
                                <div className="flex gap-4">
                                    <Button>Download Subtitles</Button>
                                    <Button>Export Cards</Button>
                                    <Link href={`/anime/${id}/episode/${episode}`}>
                                        <Button>Customize Vocabulary</Button>
                                    </Link>
                                </div>
                            </div>
                            <Separator />
                        </div>
                    )
                })
            }
        </div>
    );
};