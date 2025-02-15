import { Button } from "@/components/ui/button";
import { Vocabulary } from "@/components/vocabulary/cardgallery";
import { useState } from "react";
import { LoaderCircle } from 'lucide-react';

interface ExportProps {
    id: string;
    episode: string;
}

export default function Export({ id, episode }: ExportProps ) {
    const [loading, setLoading] = useState<boolean>(false);

    async function handleExport(id: string, episode: string) {
        setLoading(true);

        const checkEpisodeRes = await fetch(
            `https://anishelf.tech/api/check_episode?` + new URLSearchParams({
                anilist_id: id,
                episode: episode,
            }),
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        )
        const checkEpisodeData = await checkEpisodeRes.json();
    
        if (checkEpisodeData.episode_exists === false) {
            const getSubtitleRes = await fetch(
                `https://anishelf.tech/api/get_subtitles?` + new URLSearchParams({
                    anilist_id: id,
                    episode: episode,
                }),
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            )
            const getSubtitleData = await getSubtitleRes.json();
            const subUrl = getSubtitleData.subtitle_url;
            
            const formData = new FormData();
            formData.append('url', subUrl);
            if (subUrl.endsWith('.srt')) {
                formData.append('type', '.srt')
            }
            else if (subUrl.endsWith('.ass')) {
                formData.append('type', '.ass')
            }
    
            const analysisRes = await fetch(
                `https://anishelf.tech/api/analyze_episode?` + new URLSearchParams({
                    anilist_id: id,
                    episode: episode,
                }),
                {
                    method: 'POST',
                    body: formData
                }
            )
        }
        
        const lookupRes = await fetch(
            `https://anishelf.tech/api/export_episode?` + new URLSearchParams({
                anilist_id: id,
                episode: episode,
            }),
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        )
        const lookupData: Vocabulary[] = await lookupRes.json()
        
        console.log(lookupData);
                
        const csvHeader = "data:text/csv;charset=utf-8,"
        const csvString = []
        csvString.push(["keb", "reb", "sense"].join(","));
        
        lookupData.map(card =>
            csvString.push([
                card.keb,
                card.reb,
                card.sense.join(" / "),
            ].join(","))
        )

        const finalCsvString = csvString.join('\n');

        const finalCsv = csvHeader + finalCsvString;
    
        let encodedUri = encodeURI(finalCsv);
        window.open(encodedUri);

        setLoading(false);
    }

    return (
        (loading) ? 
        (<Button disabled><LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> Processing...</Button>) : 
        (<Button onClick={() => handleExport(id, episode)}>Export Cards</Button>)
    )
}
