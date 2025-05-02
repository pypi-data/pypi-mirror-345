import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';

const setupCode = `
%load_ext jupyter_ai
%ai register anthropic-chat anthropic-chat:claude-2.0
%ai register native-cohere cohere:command
%ai register bedrock-cohere bedrock:cohere.command-text-v14
%ai register anthropic anthropic:claude-v1
%ai register bedrock bedrock:amazon.titan-text-lite-v1
%ai register gemini gemini:gemini-1.0-pro-001
%ai register gpto openai-chat:gpt-4o
%ai delete ernie-bot
%ai delete ernie-bot-4
%ai delete titan
%load_ext pergamon_server_extension
`;

/**
 * Initialization data for the pergamon_server_extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'pergamon_server_extension:plugin',
  description: 'Calliope server extension',
  requires: [INotebookTracker],
  autoStart: true,
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker) => {
    console.log('JupyterLab extension pergamon_server_extension is activated!');

    tracker.widgetAdded.connect((sender, notebookPanel) => {
      notebookPanel.sessionContext.ready.then(() => {
        const session = notebookPanel.sessionContext.session;

        if (session?.kernel) {
          // loads the extension
          session.kernel
            .requestExecute({
              code: setupCode
            })
            .done.then(() => {
              console.log('Extension loaded successfully');
            });
        }
      });
    });

    const observer = new MutationObserver((mutationsList, observer) => {
      const splashElement = document.querySelector('.jp-Splash');
      if (splashElement) {
        splashElement.remove();
        observer.disconnect();
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }
};

export default plugin;
