# LLaMA 3.1 Local Chat Interface

This project is a small **vibe-coding** project I built to interact with the **LLaMA 3.1 model** locally on my machine. The aim was to create a lightweight **GUI interface** that allows for seamless interactions with a powerful language model via a simple API. The idea was to create an easy-to-use chat interface, while also enabling the ability to upload and interact with various document types (PDF, TXT, DOCX).

### Features

- **Localized LLM Chat**: By using LLaMA 3.1, I’ve set up a fully localized environment for AI chat — **no internet required**.
- **Real-time Streaming**: The interface supports **streaming responses** from the model, offering a more responsive chat experience.
- **File Uploads**: You can easily **upload and process files** like PDFs, DOCX, or TXT. The model can then reference these files to provide intelligent responses based on their content.
- **Clean and Simple GUI**: The app has a sleek, **fullscreen interface** with a **minimalist design**, making interactions feel smooth.

### How It Works

1. **Local LLaMA Model**: I’m running the LLaMA 3.1 model locally using `ollama`. It acts as the core backend that processes the input and generates the responses.
2. **GUI Built with Tkinter**: The frontend is a simple Tkinter-based Python app that includes:
   - A **chat interface** with a **scrollable output field**
   - A **single-line input field** for typing
   - A **Send button** for submitting text or documents
   - A **Attach button** to upload files such as PDFs or Word docs
3. **Streaming Responses**: The app uses Python’s **`requests`** library to stream responses from the model, ensuring a real-time chat experience.
4. **Document Uploads**: You can upload documents, and the app extracts the text for the model to use in generating context-aware responses. The model will process documents and respond based on the contents of the file.

### Steps to Set Up

1. **Install Dependencies**: Before running the app, make sure to install the required Python libraries:
    ```bash
    pip install python-docx PyMuPDF requests
    ```
2. **Run LLaMA 3.1 Locally**: Make sure you have the LLaMA 3.1 model running locally with `ollama`. Run the following command to start the model:
    ```bash
    ollama run llama3.1:8b
    ```
3. **Launch the App**: After the model is running, you can launch the Python GUI app. The interface will maximize automatically, and you'll be able to interact with the LLaMA model via the **Attach button** for file uploads and **Send button** for text input.

### Future Improvements

This project was a fun, **small vibe-coding** experiment, but there's plenty more to add, including:
- **Support for more file formats** (e.g., Markdown, CSV, etc.)
- **More customization** in the chat interface
- **Advanced file parsing** and **text summarization** features
- **Exporting chat history** to text or JSON files

### Conclusion

This project has enabled me to create a **localized version** of an LLM-based chat application, giving me full control over the chat experience and the data it processes. It’s a great first step towards building more advanced AI-powered applications without relying on cloud-based services. 

Feel free to fork this repo and experiment with your own tweaks!
