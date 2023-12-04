# NewsGPT

NewsGPT is an innovative implementation of GPT 3.5 Turbo, enhanced with real-time internet data access capabilities. It utilizes Google's Custom Search API to retrieve relevant websites based on a dynamically generated search query by GPT-3.5 Turbo. The system then scrapes content from these websites, concatenating it into a comprehensive text block. This aggregated data significantly enriches the AI's ability to answer questions with up-to-date information.

## Running NewsGPT

To use NewsGPT, run `main.py` in an Integrated Development Environment (IDE) to launch the Tkinter GUI. This interface will prompt you for three essential keys:

1. **OpenAI API Key**: Used to access GPT-3.5 Turbo.
2. **Google API Key**: Necessary for accessing Google's Custom Search API.
3. **Google Browser ID for Custom Search**: Identifies your custom search engine instance.

### Obtaining API Keys

#### OpenAI API Key:
1. Visit [OpenAI's API website](https://openai.com/api/).
2. Sign up or log in to create an account.
3. Navigate to the API section and follow the instructions to generate your API key.

#### Google API Key and Browser ID:
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to the “APIs & Services” dashboard and enable the “Custom Search API”.
4. Go to “Credentials” and create an API key following the provided steps.
5. For the Browser ID, visit [Google Custom Search Engine](https://cse.google.com/cse/all) and create a new search engine.
6. Copy the unique identifier (CX) of your search engine.

With these keys, you are all set to explore NewsGPT’s capabilities.

#### Inspiration and disclaimer: 
This project was initially conceived for a client on Upwork, who requested an AI application capable of performing enhanced internet searches to support query responses. The work on NewsGPT was completed diligently, meeting the project's specifications. Unfortunately, the client did not follow through with payment upon project completion, and consequently, no formal transaction was made. As a result, the project was never officially accepted nor transferred to the client, and thus, it remains under my ownership. In light of this, I've decided to share NewsGPT on GitHub as an open-source resource for others to learn from and build upon. Please note that while the project is based on a contracted idea, the code and implementation are solely my own contributions, unclaimed and unpaid by the original Upwork client.


![Screenshot 2023-11-17 181025](https://github.com/Aa-ronT/NewsGPT/assets/103137680/cfa8ac92-8be4-437f-9eb8-67b33a0e4195)

