import { GetServerSideProps, GetServerSidePropsContext } from 'next';

interface AnimePageProps {
    data: AnimeShow
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
        large: string;
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
                    large
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
    return (
        <div>{data.title.romaji}</div>
    )
}

