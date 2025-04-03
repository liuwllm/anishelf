import { Button } from "@/components/ui/button";
import { Vocabulary } from "@/components/cardgallery";
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

        // Check if data exists for episode
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
    
        // If there is no data for the episode, retrieve all data and insert into the database
        if (checkEpisodeData.episode_exists === false) {
            // Retrieve the first subtitle file available for further processing
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
            
            // Check type of subtitle file for backend to process
            const formData = new FormData();
            formData.append('url', subUrl);
            if (subUrl.endsWith('.srt')) {
                formData.append('type', '.srt')
            }
            else if (subUrl.endsWith('.ass')) {
                formData.append('type', '.ass')
            }
    
            // Call /analyze_episode endpoint to parse words from subtitle file, find frequency and dictionary data, and insert into database
            await fetch(
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
        
        // Since all data should be inserted into database, retrieve all word data for the episode from database
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
        
        // Format CSV file
        const csvHeader = "data:text/csv;charset=utf-8,"
        const csvString = []
        csvString.push(["keb", "reb", "sense"].join(","));
        
        // Add all word data from the episode to CSV string
        lookupData.map(card =>
            csvString.push([
                card.keb,
                card.reb,
                card.sense.join(" / "),
            ].join(","))
        )

        // Format CSV string into CSV file
        const finalCsvString = csvString.join('\n');
        const finalCsv = csvHeader + finalCsvString;
    
        // Download CSV file for user
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
