import { ISettingRegistry } from '@jupyterlab/settingregistry';

/**
 * Interface for chat settings
 */
export interface IChatSettings {
  defaultGreeting: string;
  maxMessages: number;
  serverUrl: string;
  apiKey: string;
  username: string;
  proxyPort?: number;
}

/**
 * A class representing the settings page for the chat widget
 */
export class SettingsPage {
  private settingsRegistry: ISettingRegistry;
  private container: HTMLDivElement;
  private overlay: HTMLDivElement;
  private currentSettings: IChatSettings;
  private onSave: (settings: IChatSettings) => void;

  /**
   * Create a new SettingsPage
   * @param settingsRegistry The settings registry
   * @param currentSettings The current settings
   * @param onSave Callback function when settings are saved
   */
  constructor(
    settingsRegistry: ISettingRegistry,
    currentSettings: IChatSettings,
    onSave: (settings: IChatSettings) => void
  ) {
    this.settingsRegistry = settingsRegistry;
    this.currentSettings = currentSettings;
    this.onSave = onSave;

    // Create overlay
    this.overlay = document.createElement('div');
    this.overlay.className = 'escobar-settings-overlay';
    this.overlay.addEventListener('click', (e) => {
      if (e.target === this.overlay) {
        this.hide();
      }
    });

    // Create container
    this.container = this.createContainer();
    this.overlay.appendChild(this.container);
  }

  /**
   * Create the settings UI container
   */
  private createContainer(): HTMLDivElement {
    // Create container
    const container = document.createElement('div');
    container.className = 'escobar-settings-container';

    // Create header
    const header = document.createElement('div');
    header.className = 'escobar-settings-header';

    const title = document.createElement('h2');
    title.textContent = 'Settings';
    header.appendChild(title);

    const closeButton = document.createElement('button');
    closeButton.className = 'escobar-settings-close-button';
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', () => this.hide());
    header.appendChild(closeButton);

    container.appendChild(header);

    // Create form
    const form = document.createElement('form');
    form.className = 'escobar-settings-form';
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.saveSettings();
    });

    // Create form fields

    // Default greeting field
    const defaultGreetingGroup = document.createElement('div');
    defaultGreetingGroup.className = 'escobar-settings-group';

    const defaultGreetingLabel = document.createElement('label');
    defaultGreetingLabel.textContent = 'Default Greeting';
    defaultGreetingLabel.htmlFor = 'escobar-default-greeting';
    defaultGreetingGroup.appendChild(defaultGreetingLabel);

    const defaultGreetingDescription = document.createElement('div');
    defaultGreetingDescription.className = 'escobar-settings-description';
    defaultGreetingDescription.textContent = 'The default greeting message shown when opening a new chat.';
    defaultGreetingGroup.appendChild(defaultGreetingDescription);

    const defaultGreetingInput = document.createElement('textarea');
    defaultGreetingInput.id = 'escobar-default-greeting';
    defaultGreetingInput.className = 'escobar-settings-input';
    defaultGreetingInput.value = this.currentSettings.defaultGreeting;
    defaultGreetingInput.rows = 3;
    defaultGreetingGroup.appendChild(defaultGreetingInput);

    form.appendChild(defaultGreetingGroup);

    // Max messages field
    const maxMessagesGroup = document.createElement('div');
    maxMessagesGroup.className = 'escobar-settings-group';

    const maxMessagesLabel = document.createElement('label');
    maxMessagesLabel.textContent = 'Maximum Messages';
    maxMessagesLabel.htmlFor = 'escobar-max-messages';
    maxMessagesGroup.appendChild(maxMessagesLabel);

    const maxMessagesDescription = document.createElement('div');
    maxMessagesDescription.className = 'escobar-settings-description';
    maxMessagesDescription.textContent = 'The maximum number of messages to keep in the chat history.';
    maxMessagesGroup.appendChild(maxMessagesDescription);

    const maxMessagesInput = document.createElement('input');
    maxMessagesInput.id = 'escobar-max-messages';
    maxMessagesInput.className = 'escobar-settings-input';
    maxMessagesInput.type = 'number';
    maxMessagesInput.min = '10';
    maxMessagesInput.max = '1000';
    maxMessagesInput.value = this.currentSettings.maxMessages.toString();
    maxMessagesGroup.appendChild(maxMessagesInput);

    form.appendChild(maxMessagesGroup);

    // Server URL field
    const serverUrlGroup = document.createElement('div');
    serverUrlGroup.className = 'escobar-settings-group';

    const serverUrlLabel = document.createElement('label');
    serverUrlLabel.textContent = 'Server URL';
    serverUrlLabel.htmlFor = 'escobar-server-url';
    serverUrlGroup.appendChild(serverUrlLabel);

    const serverUrlDescription = document.createElement('div');
    serverUrlDescription.className = 'escobar-settings-description';
    serverUrlDescription.textContent = 'The URL of the WebSocket server to connect to.';
    serverUrlGroup.appendChild(serverUrlDescription);

    const serverUrlInput = document.createElement('input');
    serverUrlInput.id = 'escobar-server-url';
    serverUrlInput.className = 'escobar-settings-input';
    serverUrlInput.type = 'text';
    serverUrlInput.value = this.currentSettings.serverUrl;
    serverUrlGroup.appendChild(serverUrlInput);

    form.appendChild(serverUrlGroup);

    // API Key field
    const apiKeyGroup = document.createElement('div');
    apiKeyGroup.className = 'escobar-settings-group';

    const apiKeyLabel = document.createElement('label');
    apiKeyLabel.textContent = 'API Key';
    apiKeyLabel.htmlFor = 'escobar-api-key';
    apiKeyGroup.appendChild(apiKeyLabel);

    const apiKeyDescription = document.createElement('div');
    apiKeyDescription.className = 'escobar-settings-description';
    apiKeyDescription.textContent = 'The API key for authentication with the server.';
    apiKeyGroup.appendChild(apiKeyDescription);

    const apiKeyInput = document.createElement('input');
    apiKeyInput.id = 'escobar-api-key';
    apiKeyInput.className = 'escobar-settings-input';
    apiKeyInput.type = 'text';
    apiKeyInput.value = this.currentSettings.apiKey;
    apiKeyGroup.appendChild(apiKeyInput);

    form.appendChild(apiKeyGroup);

    // Username field
    const usernameGroup = document.createElement('div');
    usernameGroup.className = 'escobar-settings-group';

    const usernameLabel = document.createElement('label');
    usernameLabel.textContent = 'Username';
    usernameLabel.htmlFor = 'escobar-username';
    usernameGroup.appendChild(usernameLabel);

    const usernameDescription = document.createElement('div');
    usernameDescription.className = 'escobar-settings-description';
    usernameDescription.textContent = 'Your display name for chat messages.';
    usernameGroup.appendChild(usernameDescription);

    const usernameInput = document.createElement('input');
    usernameInput.id = 'escobar-username';
    usernameInput.className = 'escobar-settings-input';
    usernameInput.type = 'text';
    usernameInput.value = this.currentSettings.username;
    usernameGroup.appendChild(usernameInput);

    form.appendChild(usernameGroup);

    // Proxy Port field
    const proxyPortGroup = document.createElement('div');
    proxyPortGroup.className = 'escobar-settings-group';

    const proxyPortLabel = document.createElement('label');
    proxyPortLabel.textContent = 'Proxy Port';
    proxyPortLabel.htmlFor = 'escobar-proxy-port';
    proxyPortGroup.appendChild(proxyPortLabel);

    const proxyPortDescription = document.createElement('div');
    proxyPortDescription.className = 'escobar-settings-description';
    proxyPortDescription.textContent = 'The port number for the proxy server.';
    proxyPortGroup.appendChild(proxyPortDescription);

    const proxyPortInput = document.createElement('input');
    proxyPortInput.id = 'escobar-proxy-port';
    proxyPortInput.className = 'escobar-settings-input';
    proxyPortInput.type = 'number';
    proxyPortInput.min = '1';
    proxyPortInput.max = '65535';
    proxyPortInput.value = (this.currentSettings.proxyPort || 3000).toString();
    proxyPortGroup.appendChild(proxyPortInput);

    form.appendChild(proxyPortGroup);

    // Create buttons
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'escobar-settings-buttons';

    const cancelButton = document.createElement('button');
    cancelButton.className = 'escobar-settings-button escobar-settings-cancel-button';
    cancelButton.textContent = 'Cancel';
    cancelButton.type = 'button';
    cancelButton.addEventListener('click', () => this.hide());
    buttonsContainer.appendChild(cancelButton);

    const saveButton = document.createElement('button');
    saveButton.className = 'escobar-settings-button escobar-settings-save-button';
    saveButton.textContent = 'Save';
    saveButton.type = 'submit';
    buttonsContainer.appendChild(saveButton);

    form.appendChild(buttonsContainer);

    container.appendChild(form);

    return container;
  }

  /**
   * Show the settings page
   */
  public show(): void {
    // Fetch the latest settings from the registry before showing the form
    this.settingsRegistry.load('escobar:plugin')
      .then(settings => {
        // Update current settings with the latest from the registry
        const latestSettings = settings.composite as any as IChatSettings;
        console.log('Fetched latest settings from registry for settings page:', latestSettings);

        // Merge with default settings to ensure all fields are present
        this.currentSettings = {
          defaultGreeting: latestSettings.defaultGreeting || this.currentSettings.defaultGreeting,
          maxMessages: latestSettings.maxMessages || this.currentSettings.maxMessages,
          serverUrl: latestSettings.serverUrl || this.currentSettings.serverUrl,
          apiKey: latestSettings.apiKey || this.currentSettings.apiKey,
          username: latestSettings.username || this.currentSettings.username,
          proxyPort: latestSettings.proxyPort || this.currentSettings.proxyPort || 3000
        };

        // Update form fields with the latest settings
        this.updateFormFields();

        // Show the settings page
        document.body.appendChild(this.overlay);
        // Add animation class after a small delay to trigger animation
        setTimeout(() => {
          this.overlay.classList.add('escobar-settings-overlay-visible');
          this.container.classList.add('escobar-settings-container-visible');
        }, 10);
      })
      .catch(error => {
        console.error('Failed to load latest settings from registry:', error);

        // Fall back to using the current settings
        this.updateFormFields();

        // Show the settings page anyway
        document.body.appendChild(this.overlay);
        // Add animation class after a small delay to trigger animation
        setTimeout(() => {
          this.overlay.classList.add('escobar-settings-overlay-visible');
          this.container.classList.add('escobar-settings-container-visible');
        }, 10);
      });

    const proxyPortInput = document.getElementById('escobar-proxy-port') as HTMLInputElement;
    if (proxyPortInput) proxyPortInput.value = (this.currentSettings.proxyPort || 3000).toString();
  }

  /**
   * Update form fields with current settings
   */
  private updateFormFields(): void {
    // Get form elements
    const defaultGreetingInput = document.getElementById('escobar-default-greeting') as HTMLTextAreaElement;
    const maxMessagesInput = document.getElementById('escobar-max-messages') as HTMLInputElement;
    const serverUrlInput = document.getElementById('escobar-server-url') as HTMLInputElement;
    const apiKeyInput = document.getElementById('escobar-api-key') as HTMLInputElement;
    const usernameInput = document.getElementById('escobar-username') as HTMLInputElement;
    const proxyPortInput = document.getElementById('escobar-proxy-port') as HTMLInputElement;

    // Update values with current settings
    if (defaultGreetingInput) defaultGreetingInput.value = this.currentSettings.defaultGreeting;
    if (maxMessagesInput) maxMessagesInput.value = this.currentSettings.maxMessages.toString();
    if (serverUrlInput) serverUrlInput.value = this.currentSettings.serverUrl;
    if (apiKeyInput) apiKeyInput.value = this.currentSettings.apiKey;
    if (usernameInput) usernameInput.value = this.currentSettings.username;

  }

  /**
   * Hide the settings page
   */
  public hide(): void {
    this.overlay.classList.remove('escobar-settings-overlay-visible');
    this.container.classList.remove('escobar-settings-container-visible');

    // Remove from DOM after animation completes
    setTimeout(() => {
      if (this.overlay.parentNode) {
        this.overlay.parentNode.removeChild(this.overlay);
      }
    }, 300); // Match the CSS transition duration
  }

  /**
   * Save settings changes
   */
  private saveSettings(): void {
    // Get values from form
    const defaultGreetingInput = document.getElementById('escobar-default-greeting') as HTMLTextAreaElement;
    const maxMessagesInput = document.getElementById('escobar-max-messages') as HTMLInputElement;
    const serverUrlInput = document.getElementById('escobar-server-url') as HTMLInputElement;
    const apiKeyInput = document.getElementById('escobar-api-key') as HTMLInputElement;
    const usernameInput = document.getElementById('escobar-username') as HTMLInputElement;
    const proxyPortInput = document.getElementById('escobar-proxy-port') as HTMLInputElement;

    // Validate input
    const defaultGreeting = defaultGreetingInput.value.trim();
    const maxMessages = parseInt(maxMessagesInput.value, 10);
    const serverUrl = serverUrlInput.value.trim();
    const apiKey = apiKeyInput.value.trim();
    const username = usernameInput.value.trim();

    if (isNaN(maxMessages) || maxMessages < 10 || maxMessages > 1000) {
      alert('Maximum Messages must be a number between 10 and 1000');
      return;
    }

    if (!serverUrl) {
      alert('Server URL is required');
      return;
    }

    if (!apiKey) {
      alert('API Key is required');
      return;
    }

    if (!username) {
      alert('Username is required');
      return;
    }

    // Create new settings object
    const newSettings: IChatSettings = {
      defaultGreeting,
      maxMessages,
      serverUrl,
      apiKey,
      username,
      proxyPort: proxyPortInput ? parseInt(proxyPortInput.value, 10) : 3000
    };

    // First update the current settings to ensure they're immediately available
    this.currentSettings = newSettings;

    // Call onSave callback before hiding the settings page
    // This ensures the settings are applied immediately
    this.onSave(newSettings);

    // Save settings to registry
    this.settingsRegistry.load('escobar:plugin')
      .then(settings => {
        settings.set('defaultGreeting', defaultGreeting);
        settings.set('maxMessages', maxMessages);
        settings.set('serverUrl', serverUrl);
        settings.set('apiKey', apiKey);
        settings.set('username', username);
        settings.set('proxyPort', newSettings.proxyPort);

        console.log('Settings saved to registry successfully');

        // Hide settings page
        this.hide();
      })
      .catch(reason => {
        console.error('Failed to save settings for escobar.', reason);
        alert('Failed to save settings. Please try again.');
      });
  }
}
