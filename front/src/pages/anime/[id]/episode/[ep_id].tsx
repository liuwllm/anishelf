import { GetServerSideProps, GetServerSidePropsContext } from 'next';

interface VocabPageProps {
    data: Vocabulary[]
}

interface Vocabulary {
    keb: string[];
    reb: string[];
    sense: string[];
}

export const getServerSideProps: GetServerSideProps = async (context: GetServerSidePropsContext) => {
    let show_id: string = context.query.id as string;
    let ep_id: string = context.query.ep_id as string;
    let offset: string = context.query.offset as string;

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

    if (checkEpisodeData.episode_exists === false) {
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
            "http://127.0.0.1:5000/analyze_episode?" + new URLSearchParams({
                anilist_id: show_id,
                episode: ep_id,
            }),
            {
                method: 'POST',
                body: formData
            }
        )
    }

    const lookupRes = await fetch(
        "http://127.0.0.1:5000/get_episode?" + new URLSearchParams({
            anilist_id: show_id,
            episode: ep_id,
            offset: offset
        }),
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }
    )
    const data = await lookupRes.json();
    
    console.log(data);

    // Pass data to the page via props
    return { props: { data } }
}

export default function Vocab({ data }: VocabPageProps) {
    return (
        <div>
            {data.map((vocab: Vocabulary) =>
                vocab.reb + ";"
            )}
        </div>
    )
}