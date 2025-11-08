import { useRef, useState } from 'react'
import {
    PromptInput,
    PromptInputActionMenu,
    PromptInputBody,
    PromptInputSubmit,
    PromptInputTextarea,
    PromptInputToolbar,
    PromptInputTools,
    PromptInputModelSelect,
    PromptInputModelSelectContent,
    PromptInputModelSelectItem,
    PromptInputModelSelectTrigger,
    PromptInputModelSelectValue,
} from '@/components/ai-elements/prompt-input';
import { Suggestion, Suggestions } from '@/components/ai-elements/suggestion';
import useChatStore from '@/store/chatStore';

const suggestions = [
    'Can you explain how to play tennis?',
    'What is the weather in Tokyo?',
    'How do I make a really good fish taco?',
];
const models = [
    { id: 'gpt-4o', name: 'GPT-4o' },
];
type PromptInputBoxProps = {
    showSuggestions?: boolean;
};

const PromptInputBox = ({ showSuggestions = false }: PromptInputBoxProps) => {
    const [model, setModel] = useState<string>(models[0].id);
    const [input, setInput] = useState('');
    const addChatMessage = useChatStore((state) => state.addMessage);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const temperature = useChatStore((state)=> state.temperature);
    const similarity = useChatStore((state)=> state.similarity);

    const sendMessage = async () => {
        if (!input.trim()) return;
        const message = input
        setInput('')
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
        console.log("input: ", message);
        addChatMessage("user", message)

        addChatMessage("bot", "")

        // navigate("/chat/response");
        console.log("temp: ", temperature)
        console.log("sim: ", similarity)

        try {
            const url = 'http://127.0.0.1:8000/api/chat'
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: message, temperature: temperature, similarity: similarity, })
            })
            const botResponse = await response.json()
            useChatStore.getState().updateLastBotMessage(botResponse.message);
        }
        catch (error) {
            console.log("an error occured when sending a message: ", error)
        }
    }

    const handleSuggestionClick = (suggestion: string) => {
        setInput(suggestion)
    };

    return (
        <div className='flex flex-col items-center gap-5'>
            <div className='w-full'>
                <PromptInput onSubmit={sendMessage} className="relative">
                    <PromptInputBody>
                        <PromptInputTextarea
                            ref={textareaRef}
                            value={input}
                            placeholder="Say something..."
                            onChange={(e) => setInput(e.currentTarget.value)}
                        />
                    </PromptInputBody>
                    <PromptInputToolbar>
                        <PromptInputTools>
                            <PromptInputActionMenu>
                            </PromptInputActionMenu>
                            <PromptInputModelSelect
                                onValueChange={(value) => {
                                    setModel(value);
                                }}
                                value={model}
                            >
                                <PromptInputModelSelectTrigger>
                                    <PromptInputModelSelectValue />
                                </PromptInputModelSelectTrigger>
                                <PromptInputModelSelectContent>
                                    {models.map((model) => (
                                        <PromptInputModelSelectItem key={model.id} value={model.id}>
                                            {model.name}
                                        </PromptInputModelSelectItem>
                                    ))}
                                </PromptInputModelSelectContent>
                            </PromptInputModelSelect>
                        </PromptInputTools>
                        <PromptInputSubmit
                            disabled={!input.trim()}
                            status={'ready'}
                        />
                    </PromptInputToolbar>
                </PromptInput>
            </div>
            {showSuggestions && (
                <div className='hidden sm:block'>
                    <Suggestions>
                        {suggestions.map((suggestion) => (
                            <Suggestion
                                key={suggestion}
                                onClick={handleSuggestionClick}
                                suggestion={suggestion}
                            />
                        ))}
                    </Suggestions>
                </div>
            )}
        </div>
    )
}

export default PromptInputBox
