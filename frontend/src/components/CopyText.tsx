import { useState } from 'react'
import { Copy, Check, } from 'lucide-react'
import useChatStore from '@/store/chatStore';


const CopyText = () => {
    const [copied, setCopied] = useState(false);

    const messages: any[] = useChatStore((state) => state.chatMessages);

    // Find the last bot message in the chatMessages array
    const lastBotIndex = messages
        .slice()
        .reverse()
        .findIndex((m: any) => m.role === 'bot');

    const lastBotMessage = lastBotIndex === -1 ? undefined : messages[messages.length - 1 - lastBotIndex];
    const messageData = lastBotMessage?.message;

    const hasMessages = Array.isArray(messageData) && messageData.length > 0;

    const getPlainText = () => {
        if (!Array.isArray(messageData)) return '';

        return messageData
            .map(item => {
                const plainText = item.modified_sentence.replace(/\*/g, '');
                return plainText;
            })
            .join(' ');
    };

    const handleCopy = async () => {
        const plainText = getPlainText();
        try {
            await navigator.clipboard.writeText(plainText);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    return (
        <div>

            {
                hasMessages ? (<div>
                    <button
                        onClick={handleCopy}
                        disabled={!hasMessages}
                        className={`self-end flex items-center gap-2 px-4 py-2 rounded-lg transition-colors 
      ${hasMessages
                                ? 'text-primary hover:text-chart-3 opacity-100 cursor-pointer'
                                : 'text-gray-400 opacity-60 cursor-default'}
                    `}
                        aria-label="Copy text"
                    >
                        {copied ? (
                            <Check className="w-4 h-4" />
                        ) : (
                            <Copy className="w-4 h-4" />
                        )}
                    </button>
                </div >) : (<div>

                </div>)
            }
        </div>

    )
}

export default CopyText
