Split a ChatGPT export JSON into 10 .txt files.

Usage:
    python split_chatgpt_json.py <chatgpt_export.json>  [--parts 20]

The script:
  • walks every conversation in the file (the export is usually a list);
  • extracts messages where content_type == "text" and parts are non-empty;
  • formats each as:

        USER:
        What time is it?

        ASSISTANT:
        It's 8 PM in Luxembourg…

  • distributes the messages evenly so each output file has content.
