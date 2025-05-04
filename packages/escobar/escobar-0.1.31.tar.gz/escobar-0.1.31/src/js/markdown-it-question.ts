/**
 * A markdown-it plugin to handle question blocks
 * 
 * This plugin converts blocks like:
 * ```question
 * Which of the following is a prime number?
 * 
 * A. 6  
 * B. 9  
 * C. 13  
 * D. 15
 * ```
 * 
 * Into interactive question blocks with clickable answer buttons
 */

import MarkdownIt from 'markdown-it';

function parseQuestionBlock(content: string): { question: string, options: string[] } {
    const lines = content.split('\n').filter(line => line.trim() !== '');

    // The first line is the question
    const question = lines[0];

    // The rest are options (could be with or without letter prefixes)
    const options = lines.slice(1).filter(line => line.trim() !== '');

    return { question, options };
}

export default function questionPlugin(md: MarkdownIt): void {
    // Save the original fence renderer
    const defaultFenceRenderer = md.renderer.rules.fence || function (tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
    };

    // Override the fence renderer
    md.renderer.rules.fence = function (tokens, idx, options, env, self) {
        const token = tokens[idx];
        const info = token.info.trim();

        // Only process 'question' code blocks
        if (info === 'question') {
            const { question, options } = parseQuestionBlock(token.content);

            // Create HTML for the question block
            let html = '<div class="escobar-question-block">';

            // Add the question with bold and italic formatting
            html += `<div class="escobar-question"><strong><em>${md.utils.escapeHtml(question)}</em></strong></div>`;

            // Add the options as buttons
            html += '<div class="escobar-question-options">';
            for (const option of options) {
                html += `<button class="escobar-question-option" data-option="${md.utils.escapeHtml(option)}">${md.utils.escapeHtml(option)}</button>`;
            }
            html += '</div>';

            html += '</div>';

            return html;
        }

        // For other fence blocks, use the default renderer
        return defaultFenceRenderer(tokens, idx, options, env, self);
    };

    // Add client-side JavaScript to handle button clicks
    // This will be added once when the plugin is initialized
    if (typeof window !== 'undefined' && !window.hasOwnProperty('__questionPluginInitialized')) {
        window['__questionPluginInitialized'] = true;

        // Add event listener for question option buttons
        document.addEventListener('click', function (event) {
            const target = event.target as HTMLElement;

            // Find the button element (could be the target or a parent)
            let buttonElement = target;
            if (!buttonElement.classList.contains('escobar-question-option')) {
                // If the clicked element is not the button itself, check if it's a child of a button
                buttonElement = target.closest('.escobar-question-option') as HTMLElement;
            }

            // If we found a button element, process the click
            if (buttonElement && buttonElement.classList.contains('escobar-question-option')) {
                // Get the option text from the data-option attribute
                const optionText = buttonElement.getAttribute('data-option') || buttonElement.textContent || '';

                // Highlight the selected option
                const options = document.querySelectorAll('.escobar-question-option');
                options.forEach(opt => {
                    (opt as HTMLElement).classList.remove('selected');
                });
                buttonElement.classList.add('selected');

                // Find the send button and get its text content (mode)
                const sendButton = document.querySelector('.escobar-chat-send-button') as HTMLButtonElement;
                const mode = sendButton ? sendButton.textContent || 'Talk' : 'Talk';

                // Find all chat widgets in the document
                const chatWidgets = document.querySelectorAll('.escobar-chat');
                if (chatWidgets.length > 0) {
                    // Get the first chat widget (there's usually only one)
                    const chatWidget = chatWidgets[0];

                    // We can't directly call the sendMessage method because it expects to get the content from the input field
                    // So we'll always use the input field approach

                    // Find the chat input field
                    const chatInput = document.querySelector('.escobar-chat-input') as HTMLTextAreaElement;
                    if (chatInput) {
                        // Set the input value to the option text
                        chatInput.value = optionText;

                        // Dispatch an input event to trigger any listeners
                        chatInput.dispatchEvent(new Event('input', { bubbles: true }));

                        // Simulate pressing Enter in the input field
                        const enterEvent = new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        });
                        chatInput.dispatchEvent(enterEvent);
                    }
                }
            }
        });
    }
}
