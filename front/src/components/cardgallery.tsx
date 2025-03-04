import { Button } from "@/components/ui/button"
import { 
    Collapsible,
    CollapsibleTrigger, 
    CollapsibleContent
} from "@/components/ui/collapsible"
import React, { useState } from 'react';
import UnfoldMoreIcon from '@mui/icons-material/UnfoldMore';

interface CardGalleryProps {
    words: WordGroup[]
}

export interface WordGroup{
    id: number;
    elements: Vocabulary[]
}

export interface Vocabulary {
    id: number;
    keb: string | null;
    reb: string;
    sense: string[];
}

export default function CardGallery({ words }: CardGalleryProps ) {
    const [isOpen, setIsOpen] = useState(false)
    
    return (
        <div className="flex flex-col gap-4">
            {words.map((group: WordGroup) =>
                <div className="w-full p-8 shadow-md rounded-lg bg-white items-center" key={group.id}>
                    {   
                        (group.elements.length == 1) ?
                        (<div className="flex flex-col sm:flex-row" key={group.elements[0].id}>
                            <div className="flex-none w-1/6 justify-center">{
                                (group.elements[0].keb) ?
                                (<div className="flex flex-col">
                                    <h1 className="text-4xl">{group.elements[0].keb}</h1>
                                    <h3 className="p-2 text-slate-500 text-sm">{group.elements[0].reb}</h3>
                                </div>) :
                                (<h1 className="text-4xl">{group.elements[0].reb}</h1>)
                            }</div>
                            <div className="flex-1">
                                <ol className="list-decimal">
                                    {group.elements[0].sense.map(sense =><li key={group.elements[0].id}>{sense}</li>)}
                                </ol>
                            </div>
                        </div>) :
                        (<>
                        {group.elements.slice(1).map((word: Vocabulary) => 
                                <>
                                    <div className="flex flex-col sm:flex-row" key={word.id}>
                                        <div className="flex-none w-1/6">{
                                            (word.keb) ?
                                            (<div className="flex flex-col">
                                                <h1 className="text-4xl">{word.keb}</h1>
                                                <h3 className="p-2 text-slate-500 text-sm">{word.reb}</h3>
                                            </div>) :
                                            (<h1 className="text-4xl">{word.reb}</h1>)
                                        }</div>
                                        <div className="flex-1">
                                            <ol className="list-decimal">
                                                {word.sense.map(sense =><li key={word.id}>{sense}</li>)}
                                            </ol>
                                        </div>
                                    </div>
                                    <hr className="text-slate-500 my-4" />
                                </>
                        )}
                        <div className="flex flex-col sm:flex-row" key={group.elements[group.elements.length - 1].id}>
                            <div className="flex-none w-1/6 justify-center">{
                                (group.elements[group.elements.length - 1].keb) ?
                                (<div className="flex flex-col">
                                    <h1 className="text-4xl">{group.elements[group.elements.length - 1].keb}</h1>
                                    <h3 className="p-2 text-slate-500 text-sm">{group.elements[group.elements.length - 1].reb}</h3>
                                </div>) :
                                (<h1 className="text-4xl">{group.elements[group.elements.length - 1].reb}</h1>)
                            }</div>
                            <div className="flex-1">
                                <ol className="list-decimal">
                                    {group.elements[group.elements.length - 1].sense.map(sense =><li key={group.elements[group.elements.length - 1].id}>{sense}</li>)}
                                </ol>
                            </div>
                        </div>
                        </>)
                    }
                </div>
            )}
        </div>
    )
}