import { Interweave } from 'interweave';
import { polyfill } from 'interweave-ssr';
import { GetServerSideProps, GetServerSidePropsContext } from 'next';
import { Badge } from "@/components/ui/badge";
import { ReactNode } from 'react';
import Episode from "@/components/episode";
import Logo from "@/components/logo";
import Image from 'next/image';

interface AnimePageProps {
    data: AnimeShow;
    key: string;
}

interface AnimeShow {
    id: number;
    title: {
        english: string;
        romaji: string;
    }
    description: string;
    episodes: number;
    averageScore: number;
    popularity: number;
    genres: string[];
    coverImage: {
        extraLarge: string;
        color: string;
    }
}

export const getServerSideProps: GetServerSideProps = async (context: GetServerSidePropsContext) => {
    const id = context.query.id

    const query = `
        query ($id: Int) {
            Media(id: $id) {
                id
                title {
                    english
                    romaji
                }
                description
                episodes
                averageScore
                popularity
                genres
                coverImage {
                    extraLarge
                    color
                }
            }
        }
    `;

    const variables = {
        'id': id
    }

    const fullQuery = {
        'query': query,
        'variables': variables
    }

    const response = await fetch('https://graphql.anilist.co', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify( fullQuery ),
    });
    const result = await response.json();
    const data: AnimeShow = result.data.Media
    
    // Pass data to the page via props
    return { props: { data } }
}

export default function Show({ data }: AnimePageProps) {
    polyfill();

    let title = "";
    if (data.title.english) {
        title = data.title.english;
    }
    else {
        title = data.title.romaji
    }
    
    return (
        <>
        <title>Anishelf - {data.title.english ? data.title.english: data.title.romaji}</title>
        <div className="flex gap-12 flex-col min-h-screen bg-slate-100 px-6 sm:px-12 md:px-24 lg:px-48 py-8 sm:py-12 md:py-16">
            <Logo />
            <div className="flex flex-col md:flex-row gap-12">
                <div className="flex flex-col gap-4 w-full sm:w-56 md:w-64 lg:w-72">
                    <div className="aspect-cover relative overflow-hidden rounded-md w-full sm:w-56 md:w-64 lg:w-72 shadow-lg">
                        <img src={data.coverImage.extraLarge} className="object-cover w-fit" alt={title}></img>
                    </div>
                    <div className="flex flex-row flex-wrap gap-4">
                        {data.genres.map((genre: string): ReactNode => {
                            return(
                                <Badge key={genre}>{genre}</Badge>
                            )
                        })}
                    </div>
                    <p className="text-lg text-slate-800">
                        <span className="font-bold">Average Score: </span>
                        {data.averageScore}
                    </p>
                    <p className="text-lg text-slate-800">
                        <span className="font-bold">Popularity: </span>
                        {data.popularity}
                    </p>
                </div>
                <div className="flex flex-col gap-4 w-fit">
                    <div className="flex flex-row w-full h-min">
                        <h1 className="font-bold text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-slate-800">{data.title.english ? data.title.english: data.title.romaji}</h1>
                    </div>
                    <p className="text-base sm:text-lg text-slate-800 w-fit"><Interweave content={data.description} /></p>
                    <h2 className="font-bold text-lg sm:text-xl md:text-2xl lg:text-3xl text-slate-800 mt-4">Episodes</h2>
                    <Episode count={data.episodes} id={data.id} title={title}/>
                </div>
            </div>
        </div>
        </>
    )
}

