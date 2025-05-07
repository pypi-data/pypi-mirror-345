import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from ragloader.indexing import File
from ragloader.parsing import ParsedFile
from ragloader.parsing import BaseFileParser


load_dotenv()

class OpenAIImageParser(BaseFileParser):
    """This class implements OCR text parsing from images using OpenAI API"""

    def parse(self, file: File) -> ParsedFile:
        with open(file.file_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")

        prompt = """Extract text from the image. In your answer include
                    only the text in the file without any other comments"""
        messages = [
            {"role": "user",
             "content": [{"type": "text", "text": prompt},
                         {"type": "image_url",
                          "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}]}
        ]

        llm = ChatOpenAI(model="gpt-4o")
        response = llm.invoke(messages)
        file_content = response.content

        parsed_file: ParsedFile = ParsedFile(file.file_path, file_content)
        return parsed_file
