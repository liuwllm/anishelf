import { Search } from "@/components/ui/search";
import { Button } from "@/components/ui/button";
import React, { useEffect, useState } from "react"; 
import Link from "next/link";

interface AnimeSeries {
    id: number;
    title: {
        english: string;
        romaji: string;
    }
    coverImage: {
        large: string;
    }
}

export default function Results() {
    const [fullTerm, setFullTerm] = useState<string>("");
    const [term, setTerm] = useState<string>("");
    const [anime, setAnime] = useState<AnimeSeries[]>([]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
        setTerm(e.target.value);
    }

    const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>): void => {
        if (e.key === 'Enter'){
            setFullTerm(e.currentTarget.value);
        }
    }

    const handleSubmit = (e: React.MouseEvent<HTMLButtonElement>): void => {
        setFullTerm(term);
    }

    useEffect(() => {
        let query = "";
        let searchVar = null;

        if (term === "") {
            query = `
                query {
                    Page(page: 1, perPage: 1000) {
                        media(sort: SCORE_DESC, type: ANIME) {
                            id
                            title {
                                english
                                romaji
                            }
                            coverImage {
                                large
                            }
                        }
                    }
                }
            `;
        } 
        else {
            query = `
                query ($search: String) {
                    Page(page: 1, perPage: 1000) {
                    media(search: $search, sort: SCORE_DESC, type: ANIME) {
                        id
                        title {
                            english
                            romaji
                        }
                        coverImage {
                            large
                        }
                    }
                    }
                }
            `;
            searchVar = {
                'search': term
            }
        }

        const fullJson = searchVar ? 
            ({
                'query': query,
                'variables': searchVar
            }) : 
            ({
                'query': query
            })

        const fetchAnimeSeries = async () => {
            const response = await fetch('https://graphql.anilist.co', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify( fullJson ),
            });
            const result = await response.json();
            const data: AnimeSeries[] = result.data.Page.media
            setAnime(data);
        };
        fetchAnimeSeries();
    }, [fullTerm]);

    return (
        <div className="flex flex-col gap-8">
            <div className="flex w-full gap-4">
                <Search onKeyDown={handleSearch} onChange={handleChange}/>
                <Button onClick={handleSubmit}>Search</Button>
            </div>
            <div className="grid grid-cols-6 gap-x-16 gap-y-8">
                {anime.map((anime) => (
                <div className="flex flex-col items-left gap-3">
                    <div className="aspect-cover relative overflow-hidden rounded-md shadow-lg hover:ring-4">
                        <Link href={`/anime/${anime.id}`}>
                            <img src={anime.coverImage.large} className="object-cover h-full w-full"></img>
                        </Link>
                    </div>
                    <h1 className="text-slate-500 font-semibold text-md">{anime.title.english ? anime.title.english : anime.title.romaji}</h1>
                </div>
                ))}
            </div>
        </div>
    );
};