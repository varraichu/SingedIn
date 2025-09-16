import React from 'react'
import { useEffect, useState } from "react";
import { FastAverageColor } from "fast-average-color";
import tinycolor from 'tinycolor2';
import songs from "@/data/liked_songs2.json";
import { TextEffect } from '@/components/ui/text-effect';
import { Loader } from '@/components/ai-elements/loader';

import {
    HoverCard,
    HoverCardContent,
    HoverCardTrigger,
} from "@/components/ui/hover-card"

const fac = new FastAverageColor();
// const FormattedMessage = ({ text }: { text: string }) => {
const FormattedMessage = () => {
    const [colors, setColors] = useState<Record<string, string>>({});
    const [state,setState] = useState(false);

    const text = `
I was *working on the weekend* (yes, and?) like usual, grinding away at my desk while everyone else seemed to be out enjoying the sun. Deadlines stacked up, and I kept reminding myself *started from the bottom now we here* (positions), but it didn't feel like I'd reached anywhere yet. Coffee cups piled high, and still *I can't feel my face when I'm with you* (Crash) echoed through my headphones, giving me just enough energy to keep pushing through.\n
By the time the evening rolled around, I thought about stepping away, *but I'm still standing, yeah yeah yeah* (Ashley) was playing, and somehow it kept me glued to the chair. I remembered the nights when *we found love in a hopeless place* (We Found Love) and how much those memories fueled me when things got tough. I told myself I will survive, oh, as long as I know *how to love I know I'll stay alive* (I Will Always Love You), and suddenly the exhaustion didn't seem as heavy.\n
Finally, as the clock struck midnight, I leaned back and laughed — *it's a hard knock life for us* (Midnight Rain) but maybe that's the beauty of it. My friends texted me, telling me to come out, and I thought of *how we're all just kids in America* (Hopeless), trying to figure it out one day at a time. I shut my laptop, grabbed my jacket, and whispered to myself *tonight's gonna be a good night* (Call Me Maybe), ready to trade work stress for music, laughter, and maybe a little freedom.\n
I was *working on the weekend* (yes, and?) like usual, grinding away at my desk while everyone else seemed to be out enjoying the sun. Deadlines stacked up, and I kept reminding myself *started from the bottom now we here* (positions), but it didn't feel like I'd reached anywhere yet. Coffee cups piled high, and still *I can't feel my face when I'm with you* (Crash) echoed through my headphones, giving me just enough energy to keep pushing through.\n
By the time the evening rolled around, I thought about stepping away, *but I'm still standing, yeah yeah yeah* (Ashley) was playing, and somehow it kept me glued to the chair. I remembered the nights when *we found love in a hopeless place* (We Found Love) and how much those memories fueled me when things got tough. I told myself I will survive, oh, as long as I know *how to love I know I'll stay alive* (I Will Always Love You), and suddenly the exhaustion didn't seem as heavy.\n
Finally, as the clock struck midnight, I leaned back and laughed — *it's a hard knock life for us* (Midnight Rain) but maybe that's the beauty of it. My friends texted me, telling me to come out, and I thought of *how we're all just kids in America* (Hopeless), trying to figure it out one day at a time. I shut my laptop, grabbed my jacket, and whispered to myself *tonight's gonna be a good night* (Call Me Maybe), ready to trade work stress for music, laughter, and maybe a little freedom.\n
`;

    useEffect(() => {
        async function loadColors() {
            const newColors: Record<string, string> = {};

            // 1. Extract song names from the text
            const regex = /\*(.*?)\*\s*\((.*?)\)/g;
            const referencedSongs = new Set<string>();
            let match;
            while ((match = regex.exec(text)) !== null) {
                const [, , songName] = match;
                referencedSongs.add(songName);
            }

            // 2. Only fetch colors for those songs
            for (const songName of referencedSongs) {
                const song = songs.find((s) => s.name === songName);
                if (!song) continue;

                try {
                    const img = await new Promise<HTMLImageElement>((resolve, reject) => {
                        const image = new Image();
                        image.crossOrigin = "anonymous";
                        image.onload = () => resolve(image);
                        image.onerror = (error) =>
                            reject(new Error(`Failed to load image for ${song.name}: ${error}`));
                        image.src = song.album_art;
                    });

                    const color = await fac.getColor(img);
                    console.log(`Color for ${song.name}:`, color.hex);
                    newColors[song.name] = color.hex;
                } catch (error) {
                    console.error(`Error processing ${songName}:`, error);
                }
            }

            setColors(newColors);
        }

        loadColors();
    }, [text]);

    function getBeautifulContrast(hex: string): string {
        const color = tinycolor(hex);
        const isDark = color.isDark();

        if (isDark) {
            // For dark colors, return a light, slightly warm color
            return color.lighten(60).desaturate(20).toString();
        } else {
            // For light colors, return a dark, sophisticated color
            return color.darken(40).saturate(15).toString();
        }
    }

    const renderPlainTextWords = (text: string, startKey: string) => {
        return text.split(/(\s+)/).map((part, index) => {
            if (part.match(/^\s+$/)) {
                return part;
            } else if (part.trim()) {
                return (
                    <span
                        key={`${startKey}-${index}`}
                        className="inline-flex items-center rounded text-black font-semibold"
                    >
                        <div className="h-8 opacity-0" />
                        {part}
                    </span>
                );
            }
            return part;
        });
    };

    // 3. Render text with highlights
    const parts: (string | React.ReactNode)[] = [];
    const regex = /\*(.*?)\*\s*\((.*?)\)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
        const [full, lyric, songName] = match;
        if (match.index > lastIndex) {
            const plainText = text.slice(lastIndex, match.index);
            parts.push(...renderPlainTextWords(plainText, `plain-${lastIndex}`));
        }
        const color = colors[songName] || "#ffffff"; // fallback
        const song = songs.find((s) => s.name === songName);
        parts.push(
            <span
                key={match.index}
                className="inline-flex items-center gap-1 rounded px-1 text-white font-bold"
                style={{
                    backgroundColor: color,
                    color: getBeautifulContrast(color)
                }}
            >
                {song && (
                    <img
                        src={song.album_art}
                        alt={song.name}
                        className="w-8 h-8 object-cover rounded-sm border transform rotate-[-17deg]"
                    />
                )}
                <HoverCard>
                    <HoverCardTrigger>
                        <TextEffect per='char' preset='fade' speedReveal={0.5} speedSegment={0.3}>
                            {lyric}
                        </TextEffect>
                    </HoverCardTrigger>
                    <HoverCardContent>
                        {song && song.name}
                    </HoverCardContent>
                </HoverCard>
            </span>
        );
        lastIndex = regex.lastIndex;
    }


    if (lastIndex < text.length) {
        const remainingText = text.slice(lastIndex);
        parts.push(...renderPlainTextWords(remainingText, "remaining"));
    }
    return (
        <div className="flex flex-1 h-full pt-2 pb-2 pl-8 pr-8 md:pl-16 md:pr-16 lg:pl-28 lg:pr-28">
            {
                state ? 
                    <p>{parts}</p> 
                    : 
                    <div className='items-center justify-center flex flex-1'>
                        <Loader/>
                    </div> 
            }
        </div>
    )
}

export default FormattedMessage


