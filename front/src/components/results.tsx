import { useEffect, useState } from "react"; 

interface AnimeSeries {
    id: number;
    title: {
        english: string;
    }
    description: string;
    averageScore: number;
    episodes: number;
    genres: string[];
    coverImage: {
        extraLarge: string;
        large: string;
        medium: string;
        color: string;
    }
}

const allQuery = `
    query {
        Page(page: 1, perPage: 50) {
        media(sort: SCORE_DESC, type: ANIME) {
            id
            title {
            english
            }
            description
            averageScore
            episodes
            genres
            coverImage {
            extraLarge
            large
            medium
            color
            }
        }
        }
    }
`;

export default function Results() {
    const [anime, setAnime] = useState<AnimeSeries[]>([]);

    useEffect(() => {
        const fetchAnimeSeries = async () => {
            const response = await fetch('https://graphql.anilist.co', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: allQuery
                }),
            });
            const result = await response.json();
            const data: AnimeSeries[] = result.data.Page.media
            setAnime(data);
        };
        fetchAnimeSeries();
    }, []);

    return (
        <div className="grid grid-cols-6 gap-x-16 gap-y-8">
            {anime.map((anime) => (
            <div className="flex flex-col items-left gap-3">
                <div className="aspect-cover relative overflow-hidden rounded-md shadow-lg">
                    <img src={anime.coverImage.large} className="object-cover h-full w-full"></img>
                </div>
                <h1 className="text-slate-500 font-semibold text-md">{anime.title.english}</h1>
            </div>
            ))}
        </div>
    );
};