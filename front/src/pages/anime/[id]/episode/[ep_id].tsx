import { GetServerSideProps, GetServerSidePropsContext } from 'next';

interface VocabPageProps {
    data: Vocabulary
}

interface Vocabulary {
    id: number;
    keb: string[];
    reb: string[];
    sense: string[];
}

export const getServerSideProps: GetServerSideProps = async (context: GetServerSidePropsContext) => {
    let show_id: string = context.query.id as string;
    let ep_id: string = context.query.ep_id as string;

    const checkEpisodeRes = await fetch(
        "http://127.0.0.1:5000/check_episode?" + new URLSearchParams({
            anilist_id: show_id,
            episode: ep_id,
        }),
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }
    )
    const checkEpisodeData = await checkEpisodeRes.json();
    let result = ""
    if (checkEpisodeData.episode_exists === true) {
        result = "yes"
    }
    else {
        const getSubtitleRes = await fetch(
            "http://127.0.0.1:5000/get_subtitles?" + new URLSearchParams({
                anilist_id: show_id,
                episode: ep_id,
            }),
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        )
        const getSubtitleData = await getSubtitleRes.json();
        result = getSubtitleData.subtitle_url;
    }

    // Pass data to the page via props
    return { props: { result } }
}

export default function Vocab({ result }: any) {
    return (
        <div>
            {result}
        </div>
    )
}