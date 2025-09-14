// RichTextRenderer.tsx
import { useEffect, useState } from "react";
import { FastAverageColor } from "fast-average-color";
import tinycolor from 'tinycolor2';
import songs from "@/data/liked_songs2.json";
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { TextEffect } from '@/components/ui/text-effect';
import {
    PromptInput,
    PromptInputSubmit,
    PromptInputTextarea,
    PromptInputToolbar,
} from '@/components/ai-elements/prompt-input';

import {
    HoverCard,
    HoverCardContent,
    HoverCardTrigger,
} from "@/components/ui/hover-card"

const fac = new FastAverageColor();

export default function RichTextRenderer({ text }: { text: string }) {
    const [colors, setColors] = useState<Record<string, string>>({});

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
        <div className="p-2 h-screen">
            <div className="relative flex flex-col w-full h-full justify-between p-2">
                <div className=" overflow-y-auto flex-1 pb-32">
                    <p>{parts}</p>
                </div>

                {/* <div className="absolute bottom-4 left-4 right-4 z-10">
                    <Textarea
                        placeholder="Type your message here."
                        className="w-1/2
                         bg-white/20 
                         backdrop-blur-sm 
                         border border-white rounded-2xl 
                         shadow-xl 
                         placeholder:text-gray-600
                         text-gray-800"
                         />
                         </div> */}

                <div className="absolute bottom-4 left-4 right-4 z-10 flex justify-center">
                    <PromptInput
                        onSubmit={() => { }}
                        className="w-1/2
         bg-white/20 
         backdrop-blur-sm
         border border-white rounded-2xl 
         shadow-xl 
         placeholder:text-gray-600
         text-gray-800"
                    >
                        <PromptInputTextarea
                            onChange={(e) => { }}
                            placeholder="Ask me anything..."
                        />
                        <PromptInputSubmit
                            className="absolute right-1 top-1/2 -translate-y-1/2"
                            disabled={false}
                            status={'ready'}
                        />
                    </PromptInput>
                </div>
            </div>
        </div>
    )
}
