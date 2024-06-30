import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import Export from "@/components/export";
import { useState } from "react";
import { LoaderCircle } from 'lucide-react';
import { SubLoader, VocabLoader } from "@/components/animeEntry/loading";

interface EpisodeProps {
    count: number;
    id: number;
    title: string;
}

export default function Episode({ count, id, title }: EpisodeProps) {
    const episodeNumbers: number[] = [];
    const [subLoading, setSubLoading] = useState<boolean>(false);
    const [vocabLoading, setVocabLoading] = useState<boolean>(false);

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
                                    <SubLoader id={id.toString()} episode={episode.toString()} title={title}/>
                                    <Export id={id.toString()} episode={episode.toString()} />
                                    <VocabLoader id={id.toString()} episode={episode.toString()} title={title}/>
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