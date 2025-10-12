import React from 'react'
import { useEffect, useState } from "react";
import { FastAverageColor } from "fast-average-color";
import tinycolor from 'tinycolor2';
import songs from "@/data/liked_songs.json";
import { TextEffect } from '@/components/ui/text-effect';
import { Loader } from '@/components/ai-elements/loader';

import {
    HoverCard,
    HoverCardContent,
    HoverCardTrigger,
} from "@/components/ui/hover-card"
import useChatStore from '@/store/chatStore';

const fac = new FastAverageColor();
// const FormattedMessage = ({ text }: { text: string }) => {
const FormattedMessage = () => {
    const [colors, setColors] = useState<Record<string, string>>({});

    const messages: any[] = useChatStore((state) => state.chatMessages);

    // Find the last bot message in the chatMessages array
    const lastBotIndex = messages
        .slice()
        .reverse()
        .findIndex((m: any) => m.role === 'bot');

    const lastBotMessage = lastBotIndex === -1 ? undefined : messages[messages.length - 1 - lastBotIndex];
    const text = lastBotMessage?.message ??'';

    useEffect(() => {
        async function loadColors() {
            const newColors: Record<string, string> = {};
            if (!text) {
                // nothing to parse yet
                setColors({});
                return;
            }

            // 1. Extract song names from the text
            const regex = /\*(.*?)\*\s*\((.*?)\)/g;
            const referencedSongs = new Set<string>();
            let match: RegExpExecArray | null;
            while ((match = regex.exec(text)) !== null) {
                const [, , songName] = match;
                referencedSongs.add(songName);
            }

            // 2. Only fetch colors for those songs
            for (const songName of referencedSongs) {
                const song = songs.find((s) => s.clean_name === songName);
                if (!song) continue;

                try {
                    const img = await new Promise<HTMLImageElement>((resolve, reject) => {
                        const image = new Image();
                        image.crossOrigin = 'anonymous';
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
    let match: RegExpExecArray | null;

    // If there's no text yet, parts will remain empty and we will show loader below
    while ((match = regex.exec(text)) !== null) {
        const [, lyric, songName] = match;
        if (match.index > lastIndex) {
            const plainText = text.slice(lastIndex, match.index);
            parts.push(...renderPlainTextWords(plainText, `plain-${lastIndex}`));
        }
        const color = colors[songName] || '#ffffff'; // fallback
        const song = songs.find((s) => s.clean_name === songName);
        parts.push(
            <span
                key={match.index}
                className="inline-flex items-center gap-1 rounded px-1 text-white font-bold"
                style={{
                    backgroundColor: color,
                    color: getBeautifulContrast(color),
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
                        <TextEffect per="char" preset="fade" speedReveal={0.5} speedSegment={0.3}>
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
        parts.push(...renderPlainTextWords(remainingText, 'remaining'));
    }

    const isWaitingForBot = lastBotMessage === undefined || lastBotMessage.message === '';

    return (
        <div className="flex flex-1 h-full pt-2 pb-2 pl-8 pr-8 md:pl-16 md:pr-16 lg:pl-28 lg:pr-28">
            {isWaitingForBot ? (
                <div className="items-center justify-center flex flex-1">
                    <Loader />
                </div>
            ) : (
                <p>{parts}</p>
            )}
        </div>
    );
}

export default FormattedMessage