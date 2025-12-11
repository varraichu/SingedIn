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

const FormattedMessage = () => {
    const [colors, setColors] = useState<Record<string, string>>({});

    const messages: any[] = useChatStore((state) => state.chatMessages);

    // Find the last bot message in the chatMessages array
    const lastBotIndex = messages
        .slice()
        .reverse()
        .findIndex((m: any) => m.role === 'bot');

    const lastBotMessage = lastBotIndex === -1 ? undefined : messages[messages.length - 1 - lastBotIndex];
    const messageData = lastBotMessage?.message;

    useEffect(() => {
        console.log("bot message: ", messageData)
        const loadColors = async () => {
            const newColors: Record<string, string> = {};

            // Check if messageData is an array
            if (!Array.isArray(messageData) || messageData.length === 0) {
                setColors({});
                return;
            }

            // Extract unique song names from the array
            const referencedSongs = new Set<string>();
            messageData.forEach((item: any) => {
                if (item.song_name) {
                    referencedSongs.add(item.song_name);
                }
            });

            // Fetch colors for those songs
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
                    newColors[songName] = color.hex;
                } catch (error) {
                    console.error(`Error processing ${songName}:`, error);
                }
            }

            setColors(newColors);
        }

        loadColors();
    }, [messageData]);

    const getBeautifulContrast = (hex: string): string => {
        const color = tinycolor(hex);
        const isDark = color.isDark();

        if (isDark) {
            return color.lighten(60).desaturate(20).toString();
        } else {
            return color.darken(40).saturate(15).toString();
        }
    }

    const renderTextWithNewlines = (text: string, parts: React.ReactNode[], keyPrefix: string) => {
        // Split text by newlines and add <br /> elements
        const lines = text.split('\n');
        lines.forEach((line, lineIndex) => {
            if (line) {
                parts.push(
                    <span
                        key={`${keyPrefix}-line-${lineIndex}`}
                        className="items-center gap-1 px-1 text-gray-800 font-medium align-middle"
                    >
                        {line}
                    </span>
                );
            }
            // Add line break after each line except the last one
            if (lineIndex < lines.length - 1) {
                parts.push(<br key={`${keyPrefix}-br-${lineIndex}`} />);
            }
        });
    };

    const renderSentence = (item: any, index: number) => {
        const song = songs.find((s) => s.clean_name === item.song_name);
        const color = colors[item.song_name] || '#cccccc';

        const modifiedText = item.modified_sentence;

        // Find all text between asterisks using matchAll
        const regex = /\*(.*?)\*/g;
        const matches = Array.from(modifiedText.matchAll(regex));

        console.log(`Processing sentence ${index}:`, modifiedText);
        console.log(`Found ${matches.length} matches:`, matches.map(m => m[1]));

        if (matches.length === 0) {
            // No asterisks in modified sentence, handle newlines and show plain text
            const parts: React.ReactNode[] = [];
            renderTextWithNewlines(modifiedText, parts, `plain-${index}`);
            return <span key={index}>{parts}{" "}</span>;
        }

        // Build the sentence with all highlighted parts
        const parts: React.ReactNode[] = [];
        let lastIndex = 0;

        matches.forEach((match, matchIndex) => {
            const highlightedText = match[1];
            const matchStart = match.index!;

            // Add text before this match (with newline handling)
            if (matchStart > lastIndex) {
                const textBefore = modifiedText.slice(lastIndex, matchStart);
                renderTextWithNewlines(textBefore, parts, `before-${index}-${matchIndex}`);
            }

            // Check if highlighted text contains newlines
            const highlightLines = highlightedText.split('\n');

            if (highlightLines.length === 1) {
                // No newlines in highlighted text - simple case
                parts.push(
                    <span
                        key={`${index}-${matchIndex}`}
                        className="inline-flex items-center gap-1 rounded px-1 text-white font-bold mx-0.5 align-middle"
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
                                <span className="cursor-pointer">
                                    <TextEffect per="char" preset="fade" speedReveal={0.5} speedSegment={0.3}>
                                        {highlightedText}
                                    </TextEffect>
                                </span>
                            </HoverCardTrigger>
                            <HoverCardContent>
                                {song && song.name}
                            </HoverCardContent>
                        </HoverCard>
                    </span>
                );
            } else {
                // Highlighted text contains newlines - render each line separately
                highlightLines.forEach((line:string, lineIdx:number) => {
                    if (line) {
                        parts.push(
                            <span
                                key={`${index}-${matchIndex}-line-${lineIdx}`}
                                className="inline-flex items-center gap-1 rounded px-1 text-white font-bold mx-0.5"
                                style={{
                                    backgroundColor: color,
                                    color: getBeautifulContrast(color),
                                }}
                            >
                                {song && lineIdx === 0 && (
                                    <img
                                        src={song.album_art}
                                        alt={song.name}
                                        className="w-8 h-8 object-cover rounded-sm border transform rotate-[-17deg]"
                                    />
                                )}
                                <HoverCard>
                                    <HoverCardTrigger>
                                        <span className="cursor-pointer">
                                            <TextEffect per="char" preset="fade" speedReveal={0.5} speedSegment={0.3}>
                                                {line}
                                            </TextEffect>
                                        </span>
                                    </HoverCardTrigger>
                                    <HoverCardContent>
                                        {song && song.name}
                                    </HoverCardContent>
                                </HoverCard>
                            </span>
                        );
                    }
                    // Add line break after each line except the last
                    if (lineIdx < highlightLines.length - 1) {
                        parts.push(<br key={`${index}-${matchIndex}-br-${lineIdx}`} />);
                    }
                });
            }

            lastIndex = matchStart + match[0].length;
        });

        // Add any remaining text after the last match
        if (lastIndex < modifiedText.length) {
            const textAfter = modifiedText.slice(lastIndex);
            renderTextWithNewlines(textAfter, parts, `after-${index}`);
        }

        // Add space after sentence
        parts.push(<React.Fragment key={`${index}-space`}> </React.Fragment>);

        return (
            <span key={index} className="inline">
                {parts}
            </span>
        );
    };

    const isWaitingForBot = lastBotMessage === undefined ||
        lastBotMessage.message === '' ||
        lastBotMessage.message === null ||
        (Array.isArray(lastBotMessage.message) && lastBotMessage.message.length === 0);

    const hasMessages = messages.length > 0;

    return (
        <div className="flex flex-1 h-full pt-2 pb-2 pl-2 pr-2 md:pl-8 md:pr-8 lg:pl-8 lg:pr-8">
            {!hasMessages ? (
                <div className="flex items-center justify-center flex-1">
                    <p>Your text will appear here</p>
                </div>
            ) : isWaitingForBot ? (
                <div className="items-center justify-center flex flex-1">
                    <Loader />
                </div>
            ) : (
                <div className="flex flex-col gap-4">
                    <div className="text-base leading-loose">
                        {Array.isArray(messageData) && messageData.map((item, index) =>
                            renderSentence(item, index)
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default FormattedMessage